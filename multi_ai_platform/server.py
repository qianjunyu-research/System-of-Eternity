from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

STATIC_DIR = Path(__file__).with_name("static")
RECENT_WINDOW = 8
SUMMARY_TRIGGER = 14
MAX_SUMMARY_LINES = 14
STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "been",
    "before",
    "being",
    "could",
    "does",
    "from",
    "have",
    "just",
    "like",
    "maybe",
    "more",
    "need",
    "platform",
    "should",
    "that",
    "then",
    "they",
    "this",
    "were",
    "what",
    "when",
    "with",
    "would",
    "your",
}
AGENT_ALIASES = {
    "codex": ("codex", "openai"),
    "claude": ("claude", "anthropic"),
    "gemini": ("gemini", "google"),
    "grok": ("grok", "xai", "x.ai"),
    "chatgpt": ("chatgpt", "chat gpt", "gpt"),
}
SPEAKER_KEYWORDS = {
    "codex": ("build", "code", "simulation", "sim", "tool", "bug", "system", "platform", "upgrade", "queue", "turn"),
    "claude": ("safe", "risk", "guard", "policy", "careful", "pause", "rule", "trust"),
    "gemini": ("design", "ui", "ux", "screen", "product", "look", "flow", "interface"),
    "grok": ("critic", "stress", "challenge", "debate", "argue", "problem", "mess", "weird"),
    "chatgpt": ("explain", "teach", "simple", "understand", "help", "idea", "plain", "beginner"),
}
BROAD_DISCUSSION_WORDS = ("all", "everyone", "group", "compare", "debate", "both", "together", "team")


class RoomError(Exception):
    """Raised when a request cannot be fulfilled in the current room state."""


@dataclass
class AgentState:
    agent_id: str
    name: str
    tagline: str
    color: str
    tokens_remaining: int
    base_cost: int
    last_cost: int = 0
    messages_sent: int = 0
    status: str = "waiting"


class ConversationRoom:
    def __init__(self) -> None:
        self._lock = Lock()
        self._reset_locked()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot_locked()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self._reset_locked()
            return self._snapshot_locked()

    def send_user_message(self, content: str) -> dict[str, Any]:
        with self._lock:
            text = content.strip()
            if not text:
                raise RoomError("Type a message before sending.")
            if self.paused:
                raise RoomError("The room is paused. Add tokens and resume first.")
            self._clear_queue_locked()
            self.direct_target = self._detect_direct_target_locked(text)
            self._append_message("user", "You", "user", text)
            self._update_summary_locked()
            self._prepare_queue_locked(source="user")
            if self.next_speaker is None:
                self.last_event = "Message sent. Nobody raised a hand yet."
            else:
                speaker_name = self.agents[self.next_speaker].name
                if self.direct_target is not None:
                    self.last_event = f"Message sent. Directed to {speaker_name}; {speaker_name} has the mic next."
                else:
                    self.last_event = f"Message sent. {speaker_name} has the mic next."
            return self._snapshot_locked()

    def send_private_message(self, agent_id: str, content: str) -> dict[str, Any]:
        with self._lock:
            text = content.strip()
            if not text:
                raise RoomError("Type a private note before sending.")
            agent = self.agents.get(agent_id)
            if agent is None:
                raise RoomError(f"Unknown agent: {agent_id}")
            workspace = self.workspaces[agent_id]
            required = self._estimate_private_cost_locked(agent, text)
            if agent.tokens_remaining < required:
                deficit = required - agent.tokens_remaining
                raise RoomError(
                    f"{agent.name} needs {required} tokens for this private turn but only has "
                    f"{agent.tokens_remaining}. Add at least {deficit} tokens first."
                )

            self._append_workspace_message_locked(agent_id, "user", "You", text)
            agent.tokens_remaining -= required
            agent.last_cost = required
            agent.messages_sent += 1
            reply = self._generate_private_reply_locked(agent, text, workspace)
            self._append_workspace_message_locked(agent_id, "assistant", agent.name, reply)
            workspace["last_event"] = f"{agent.name} replied in its private box."
            workspace["last_cost"] = required
            self.last_event = f"{agent.name} did private work. The public queue is unchanged."
            return self._snapshot_locked()

    def share_workspace_latest(self, agent_id: str) -> dict[str, Any]:
        with self._lock:
            if self.paused:
                raise RoomError("The public room is paused. Resume it before sharing private work.")
            agent = self.agents.get(agent_id)
            if agent is None:
                raise RoomError(f"Unknown agent: {agent_id}")
            workspace = self.workspaces[agent_id]
            latest = self._latest_workspace_assistant_locked(agent_id)
            if latest is None:
                raise RoomError(f"{agent.name} has no private result to share yet.")
            if latest["id"] == workspace["last_shared_message_id"]:
                raise RoomError("The latest private result is already in the room.")

            shared_text = f"From private box: {latest['content']}"
            self.direct_target = None
            self._append_message("assistant", agent.name, agent_id, shared_text)
            self._update_summary_locked()
            workspace["share_count"] += 1
            workspace["last_shared_message_id"] = latest["id"]
            workspace["last_event"] = f"Shared result {workspace['share_count']} back to the room."
            self._prepare_queue_locked(source="workspace_share")
            if self.next_speaker is None:
                self.last_event = f"{agent.name} shared a private result to the room. Nobody else wants the mic right now."
            else:
                next_name = self.agents[self.next_speaker].name
                self.last_event = f"{agent.name} shared a private result to the room. {next_name} has the mic next."
            return self._snapshot_locked()

    def request_simulation(self, agent_id: str, request: str) -> dict[str, Any]:
        with self._lock:
            text = request.strip()
            if not text:
                raise RoomError("Describe the simulation before requesting it.")
            agent = self.agents.get(agent_id)
            if agent is None:
                raise RoomError(f"Unknown agent: {agent_id}")
            workspace = self.workspaces[agent_id]
            workspace["simulation_status"] = "waiting_on_user"
            workspace["simulation_request"] = text
            workspace["last_simulation_result"] = ""
            workspace["simulation_request_count"] += 1
            self._append_workspace_message_locked(
                agent_id,
                "system",
                "Simulation Request",
                f"{agent.name} needs you to run a simulation: {text}",
            )
            workspace["last_event"] = "Simulation requested. Waiting on you to run it outside the room."
            self.last_event = f"{agent.name} asked for a simulation. The public queue is unchanged."
            return self._snapshot_locked()

    def submit_simulation_result(self, agent_id: str, result: str) -> dict[str, Any]:
        with self._lock:
            text = result.strip()
            if not text:
                raise RoomError("Paste a simulation result before sending it back.")
            agent = self.agents.get(agent_id)
            if agent is None:
                raise RoomError(f"Unknown agent: {agent_id}")
            workspace = self.workspaces[agent_id]
            if workspace["simulation_status"] != "waiting_on_user":
                raise RoomError(f"{agent.name} does not have an open simulation request right now.")

            self._append_workspace_message_locked(agent_id, "user", "Simulation Result", text)
            reply = self._generate_simulation_review_locked(agent, text, workspace)
            self._append_workspace_message_locked(agent_id, "assistant", agent.name, reply)
            workspace["simulation_status"] = "result_received"
            workspace["last_simulation_result"] = text
            workspace["simulation_result_count"] += 1
            workspace["last_event"] = "Simulation result received and reviewed privately."
            self.last_event = f"{agent.name} reviewed a simulation result in its private box. The public queue is unchanged."
            return self._snapshot_locked()

    def continue_round(self) -> dict[str, Any]:
        with self._lock:
            if self.paused:
                raise RoomError("The room is paused. Add tokens and resume first.")
            if not self.hand_queue:
                self._prepare_queue_locked(source="continue")
                if not self.hand_queue:
                    self.last_event = "Nobody wants the mic right now."
                    return self._snapshot_locked()

            while self.hand_queue:
                speaker_id = self.hand_queue[0]
                speaker = self.agents[speaker_id]
                required = self._estimate_cost_locked(speaker)
                if speaker.tokens_remaining < required:
                    if self.strict_mode:
                        self.pending_round = True
                        self.pending_reason = f"{speaker.name} has the mic next."
                        self._pause_locked(speaker_id)
                        return self._snapshot_locked()
                    self.hand_queue.pop(0)
                    if speaker_id == self.direct_target:
                        self.direct_target = None
                    continue

                self.hand_queue.pop(0)
                self.round_index += 1
                self.pending_round = bool(self.hand_queue)
                self.pending_reason = ""
                speaker.tokens_remaining -= required
                speaker.last_cost = required
                speaker.messages_sent += 1
                speaker.status = "speaking"
                self.direct_target = None
                reply = self._generate_reply_locked(speaker)
                self._append_message("assistant", speaker.name, speaker.agent_id, reply)
                self._update_summary_locked()

                if not self.hand_queue:
                    self._prepare_queue_locked(source="follow_up")
                else:
                    self._apply_statuses_locked()

                if self.next_speaker is None:
                    self.last_event = f"{speaker.name} spoke. Nobody else wants the mic right now."
                else:
                    next_name = self.agents[self.next_speaker].name
                    self.last_event = f"{speaker.name} spoke. {next_name} is up next."
                return self._snapshot_locked()

            self.last_event = "Nobody wants the mic right now."
            self._apply_statuses_locked()
            return self._snapshot_locked()

    def top_up(self, agent_id: str, amount: int) -> dict[str, Any]:
        with self._lock:
            if amount <= 0:
                raise RoomError("Top-up amount must be positive.")
            agent = self.agents.get(agent_id)
            if agent is None:
                raise RoomError(f"Unknown agent: {agent_id}")
            agent.tokens_remaining += amount
            self.last_event = f"Added {amount} tokens to {agent.name}."
            self._apply_statuses_locked()
            return self._snapshot_locked()

    def resume(self) -> dict[str, Any]:
        with self._lock:
            if not self.paused:
                self.last_event = "The room was already active."
                return self._snapshot_locked()
            self.paused = False
            self.pause_reason = ""
            self.last_event = "Room resumed. Let the next speaker take their turn."
            self._apply_statuses_locked()
            return self._snapshot_locked()

    def set_strict_mode(self, enabled: bool) -> dict[str, Any]:
        with self._lock:
            self.strict_mode = bool(enabled)
            mode = "strict pause" if self.strict_mode else "flexible skip"
            self.last_event = f"Switched to {mode} mode."
            self._apply_statuses_locked()
            return self._snapshot_locked()

    def _reset_locked(self) -> None:
        self.strict_mode = True
        self.paused = False
        self.pause_reason = ""
        self.pending_round = False
        self.pending_reason = ""
        self.round_index = 0
        self.summary = ""
        self.summary_upto_index = 0
        self.message_id = 1
        self.last_event = "Room ready. Send a message to begin."
        self.hand_queue: list[str] = []
        self.next_speaker: str | None = None
        self.direct_target: str | None = None
        self.agents = {
            "codex": AgentState(
                agent_id="codex",
                name="Codex",
                tagline="builder",
                color="#d78143",
                tokens_remaining=420,
                base_cost=120,
            ),
            "claude": AgentState(
                agent_id="claude",
                name="Claude",
                tagline="guardrails",
                color="#c95b36",
                tokens_remaining=390,
                base_cost=108,
            ),
            "gemini": AgentState(
                agent_id="gemini",
                name="Gemini",
                tagline="product sense",
                color="#2f7f6d",
                tokens_remaining=360,
                base_cost=102,
            ),
            "grok": AgentState(
                agent_id="grok",
                name="Grok",
                tagline="stress tests",
                color="#335c91",
                tokens_remaining=330,
                base_cost=96,
            ),
            "chatgpt": AgentState(
                agent_id="chatgpt",
                name="ChatGPT",
                tagline="plain English",
                color="#85634e",
                tokens_remaining=405,
                base_cost=110,
            ),
        }
        self.agent_order = ["codex", "claude", "gemini", "grok", "chatgpt"]
        self.workspaces = {
            agent_id: {
                "messages": [],
                "next_message_id": 1,
                "last_event": f"{self.agents[agent_id].name}'s private box is idle.",
                "share_count": 0,
                "last_shared_message_id": 0,
                "last_cost": 0,
                "simulation_status": "idle",
                "simulation_request": "",
                "last_simulation_result": "",
                "simulation_request_count": 0,
                "simulation_result_count": 0,
            }
            for agent_id in self.agent_order
        }
        self.transcript: list[dict[str, Any]] = []
        self._append_message(
            "system",
            "System",
            "system",
            "Room booted. One speaker talks at a time, agents can raise a hand or pass, and strict pause mode stops the room if the next speaker cannot afford a turn.",
        )
        self._apply_statuses_locked()

    def _snapshot_locked(self) -> dict[str, Any]:
        agents_payload = []
        for agent_id in self.agent_order:
            agent = self.agents[agent_id]
            agent_payload = asdict(agent)
            required = self._estimate_cost_locked(agent)
            agent_payload["required_next_tokens"] = required
            agent_payload["can_speak_next_round"] = agent.tokens_remaining >= required
            agent_payload["is_next_speaker"] = agent_id == self.next_speaker
            agents_payload.append(agent_payload)
        workspaces_payload = []
        for agent_id in self.agent_order:
            agent = self.agents[agent_id]
            workspace = self.workspaces[agent_id]
            latest_private = self._latest_workspace_assistant_locked(agent_id)
            required_private = self._estimate_private_cost_locked(agent)
            workspaces_payload.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "messages": list(workspace["messages"]),
                    "last_event": workspace["last_event"],
                    "share_count": workspace["share_count"],
                    "last_cost": workspace["last_cost"],
                    "simulation_status": workspace["simulation_status"],
                    "simulation_request": workspace["simulation_request"],
                    "last_simulation_result": workspace["last_simulation_result"],
                    "simulation_request_count": workspace["simulation_request_count"],
                    "simulation_result_count": workspace["simulation_result_count"],
                    "required_private_tokens": required_private,
                    "can_send_private": agent.tokens_remaining >= required_private,
                    "has_shareable_message": (
                        latest_private is not None
                        and latest_private["id"] != workspace["last_shared_message_id"]
                    ),
                }
            )
        return {
            "strict_mode": self.strict_mode,
            "paused": self.paused,
            "pause_reason": self.pause_reason,
            "pending_round": self.pending_round,
            "pending_reason": self.pending_reason,
            "round_index": self.round_index,
            "summary": self.summary,
            "summary_message_count": self.summary_upto_index,
            "last_event": self.last_event,
            "hand_queue": list(self.hand_queue),
            "next_speaker": self.next_speaker,
            "direct_target": self.direct_target,
            "agents": agents_payload,
            "workspaces": workspaces_payload,
            "transcript": list(self.transcript),
        }

    def _clear_queue_locked(self) -> None:
        self.hand_queue = []
        self.next_speaker = None
        self.pending_round = False
        self.pending_reason = ""
        self._apply_statuses_locked()

    def _prepare_queue_locked(self, source: str) -> None:
        del source
        latest = self._latest_public_message_locked()
        if latest is None:
            self.hand_queue = []
            self.next_speaker = None
            self.pending_round = False
            self.pending_reason = ""
            self._apply_statuses_locked()
            return

        queue = self._decide_queue_locked(latest)
        self.hand_queue = queue
        self.next_speaker = queue[0] if queue else None
        self.pending_round = bool(queue)
        self.pending_reason = (
            f"{self.agents[self.next_speaker].name} has the mic next."
            if self.next_speaker is not None
            else ""
        )
        self._apply_statuses_locked()

    def _decide_queue_locked(self, latest: dict[str, Any]) -> list[str]:
        if latest["role"] == "user" and self.direct_target is not None:
            return [self.direct_target]

        mentioned = self._detect_mentions_locked(
            latest["content"],
            exclude={latest["agent_id"]},
        )
        queue: list[str] = []

        if latest["role"] == "user":
            if mentioned:
                queue.extend(mentioned[:3])
            else:
                primary = self._pick_best_speaker_locked(latest["content"])
                if primary is not None:
                    queue.append(primary)
                if self._should_add_second_speaker_locked(latest["content"]):
                    secondary = self._pick_best_speaker_locked(
                        latest["content"],
                        exclude=set(queue),
                    )
                    if secondary is not None:
                        queue.append(secondary)
        else:
            if mentioned:
                queue.extend(mentioned[:2])
            else:
                depth = self._assistant_depth_locked()
                if depth < 3:
                    follow_up = self._pick_follow_up_speaker_locked(
                        latest["agent_id"],
                        latest["content"],
                    )
                    if follow_up is not None:
                        queue.append(follow_up)
                    if depth < 2 and self._should_add_second_speaker_locked(latest["content"]):
                        exclude = set(queue)
                        exclude.add(latest["agent_id"])
                        secondary = self._pick_best_speaker_locked(
                            latest["content"],
                            exclude=exclude,
                        )
                        if secondary is not None:
                            queue.append(secondary)

        return self._dedupe_agent_ids(queue)

    def _apply_statuses_locked(self) -> None:
        latest_exists = self._latest_public_message_locked() is not None
        base_status = "passed" if latest_exists else "waiting"
        for agent in self.agents.values():
            agent.status = base_status
        if self.hand_queue:
            first = self.hand_queue[0]
            self.next_speaker = first
            self.agents[first].status = "paused" if self.paused else "thinking"
            for agent_id in self.hand_queue[1:]:
                self.agents[agent_id].status = "raised_hand"
        else:
            self.next_speaker = None

    def _pause_locked(self, agent_id: str) -> None:
        agent = self.agents[agent_id]
        required = self._estimate_cost_locked(agent)
        deficit = required - agent.tokens_remaining
        self.paused = True
        self.pause_reason = (
            f"{agent.name} has the mic next, but it needs {required} tokens and only has "
            f"{agent.tokens_remaining}. Add at least {deficit} tokens and then resume."
        )
        self.last_event = "Turn queue paused because strict mode requires the next speaker to be ready."
        self._apply_statuses_locked()

    def _estimate_cost_locked(self, agent: AgentState) -> int:
        summary_tax = min(26, len(self.summary) // 90)
        round_tax = min(24, self.round_index * 2)
        return agent.base_cost + summary_tax + round_tax

    def _estimate_private_cost_locked(self, agent: AgentState, text: str = "") -> int:
        workspace = self.workspaces[agent.agent_id]
        base = max(52, agent.base_cost - 42)
        word_tax = min(12, len(text.split()) // 6)
        history_tax = min(10, len(workspace["messages"]) // 4)
        return base + word_tax + history_tax

    def _append_message(
        self,
        role: str,
        display_name: str,
        agent_id: str,
        content: str,
    ) -> None:
        self.transcript.append(
            {
                "id": self.message_id,
                "role": role,
                "display_name": display_name,
                "agent_id": agent_id,
                "content": content,
                "round": self.round_index,
            }
        )
        self.message_id += 1

    def _append_workspace_message_locked(
        self,
        agent_id: str,
        role: str,
        display_name: str,
        content: str,
    ) -> None:
        workspace = self.workspaces[agent_id]
        workspace["messages"].append(
            {
                "id": workspace["next_message_id"],
                "role": role,
                "display_name": display_name,
                "agent_id": agent_id,
                "content": content,
            }
        )
        workspace["next_message_id"] += 1

    def _update_summary_locked(self) -> None:
        if len(self.transcript) - self.summary_upto_index <= SUMMARY_TRIGGER:
            return
        archive_end = len(self.transcript) - RECENT_WINDOW
        if archive_end <= self.summary_upto_index:
            return
        chunk = self.transcript[self.summary_upto_index:archive_end]
        lines = self._summarize_chunk(chunk)
        if not lines:
            self.summary_upto_index = archive_end
            return
        current_lines = [line for line in self.summary.splitlines() if line.strip()]
        current_lines.extend(lines)
        if len(current_lines) > MAX_SUMMARY_LINES:
            current_lines = ["- Earlier discussion compressed."] + current_lines[-(MAX_SUMMARY_LINES - 1) :]
        self.summary = "\n".join(current_lines)
        self.summary_upto_index = archive_end

    def _summarize_chunk(self, messages: list[dict[str, Any]]) -> list[str]:
        lines: list[str] = []
        for message in messages:
            if message["role"] == "system":
                continue
            snippet = self._clip_words(message["content"], limit=18)
            lines.append(f"- {message['display_name']}: {snippet}")
        return lines[-6:]

    def _clip_words(self, text: str, limit: int) -> str:
        words = text.split()
        clipped = " ".join(words[:limit]).strip()
        if len(words) > limit:
            return f"{clipped}..."
        return clipped

    def _latest_public_message_locked(self) -> dict[str, Any] | None:
        for message in reversed(self.transcript):
            if message["role"] != "system":
                return message
        return None

    def _latest_workspace_assistant_locked(self, agent_id: str) -> dict[str, Any] | None:
        for message in reversed(self.workspaces[agent_id]["messages"]):
            if message["role"] == "assistant":
                return message
        return None

    def _assistant_depth_locked(self) -> int:
        depth = 0
        for message in reversed(self.transcript):
            if message["role"] == "assistant":
                depth += 1
                continue
            if message["role"] == "user":
                break
        return depth

    def _detect_mentions_locked(self, text: str, exclude: set[str] | None = None) -> list[str]:
        lowered = text.lower()
        hits: list[tuple[int, str]] = []
        blocked = exclude or set()
        for agent_id in self.agent_order:
            if agent_id in blocked:
                continue
            positions = [
                lowered.find(alias)
                for alias in AGENT_ALIASES[agent_id]
                if lowered.find(alias) != -1
            ]
            if positions:
                hits.append((min(positions), agent_id))
        hits.sort()
        return [agent_id for _, agent_id in hits]

    def _detect_direct_target_locked(self, text: str) -> str | None:
        lowered = text.lower()
        hits: list[tuple[int, str]] = []
        for agent_id in self.agent_order:
            for alias in AGENT_ALIASES[agent_id]:
                escaped = re.escape(alias)
                patterns = (
                    rf"^\s*@?{escaped}\b(?:[\s,:-]|$)",
                    rf"\b(?:to|for|ask|tell|let|have)\s+@?{escaped}\b",
                )
                positions = [
                    match.start()
                    for pattern in patterns
                    for match in [re.search(pattern, lowered)]
                    if match is not None
                ]
                if positions:
                    hits.append((min(positions), agent_id))
                    break
        if not hits:
            return None
        hits.sort()
        return hits[0][1]

    def _pick_best_speaker_locked(
        self,
        text: str,
        exclude: set[str] | None = None,
    ) -> str | None:
        blocked = exclude or set()
        lowered = text.lower()
        best_id: str | None = None
        best_score = -1
        for offset, agent_id in enumerate(self.agent_order):
            if agent_id in blocked:
                continue
            score = 1 if agent_id == "chatgpt" else 0
            for keyword in SPEAKER_KEYWORDS[agent_id]:
                if keyword in lowered:
                    score += 2
            score += (len(self.agent_order) - ((self.round_index + offset) % len(self.agent_order))) * 0.01
            if score > best_score:
                best_score = score
                best_id = agent_id
        return best_id

    def _pick_follow_up_speaker_locked(self, last_agent_id: str, text: str) -> str | None:
        mentioned = self._detect_mentions_locked(text, exclude={last_agent_id})
        if mentioned:
            return mentioned[0]
        return self._pick_best_speaker_locked(text, exclude={last_agent_id})

    def _should_add_second_speaker_locked(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in BROAD_DISCUSSION_WORDS)

    def _dedupe_agent_ids(self, agent_ids: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for agent_id in agent_ids:
            if agent_id in seen:
                continue
            if agent_id not in self.agents:
                continue
            seen.add(agent_id)
            ordered.append(agent_id)
        return ordered

    def _generate_reply_locked(self, agent: AgentState) -> str:
        focus = self._focus_phrase_locked()
        previous_speaker = self._previous_speaker_locked(agent.agent_id)
        summary_sentence = self._summary_sentence_locked()
        queue_sentence = self._queue_sentence_locked(agent.agent_id)
        if agent.agent_id == "codex":
            return (
                f"I can take this one. For {focus}, I would keep the next step concrete and testable. "
                f"{queue_sentence} {summary_sentence}"
            )
        if agent.agent_id == "claude":
            return (
                f"I want to keep the rules clear here. {previous_speaker} covered the direction, and I would make sure the stop conditions stay visible to the user. "
                f"{queue_sentence} {summary_sentence}"
            )
        if agent.agent_id == "gemini":
            return (
                f"From the user's side, {focus} should feel calm and readable. "
                f"{queue_sentence} {summary_sentence}"
            )
        if agent.agent_id == "grok":
            return (
                f"I'll stress-test it. If {focus} gets vague, the room gets messy fast, so I would rather keep one clear turn at a time. "
                f"{queue_sentence} {summary_sentence}"
            )
        return (
            f"Here is the plain-English version. {focus} works better when one speaker goes at a time and the others either wait or pass. "
            f"{queue_sentence} {summary_sentence}"
        )

    def _generate_private_reply_locked(
        self,
        agent: AgentState,
        prompt: str,
        workspace: dict[str, Any],
    ) -> str:
        focus = self._focus_from_text_locked(prompt)
        share_sentence = (
            "Nothing from this box reaches the room until you press Share Latest To Room."
            if workspace["share_count"] == 0
            else f"This box has already shared {workspace['share_count']} result(s) to the room."
        )
        if agent.agent_id == "codex":
            return (
                f"Private box note: I would treat {focus} like a work item and break it into concrete steps, quick tests, and the smallest useful change. "
                f"{share_sentence}"
            )
        if agent.agent_id == "claude":
            return (
                f"Private box note: I would look at edge cases, failure modes, and whether {focus} needs clearer rules before it goes public. "
                f"{share_sentence}"
            )
        if agent.agent_id == "gemini":
            return (
                f"Private box note: I would turn {focus} into a cleaner user flow, better labels, and a calmer screen before sharing it with the room. "
                f"{share_sentence}"
            )
        if agent.agent_id == "grok":
            return (
                f"Private box note: I would try to poke holes in {focus}, find what breaks first, and come back with the sharpest objections. "
                f"{share_sentence}"
            )
        return (
            f"Private box note: here is the simple version of {focus}. I would turn it into a cleaner explanation before sending it back to everyone else. "
            f"{share_sentence}"
        )

    def _generate_simulation_review_locked(
        self,
        agent: AgentState,
        result: str,
        workspace: dict[str, Any],
    ) -> str:
        focus = self._focus_from_text_locked(result)
        request = self._clip_words(workspace["simulation_request"], limit=18)
        if agent.agent_id == "codex":
            return (
                f"Thanks. For the simulation request about {request}, the signal I would pull forward is {focus}. "
                "I would keep refining this privately, then share a short conclusion back to the room if it is useful."
            )
        if agent.agent_id == "claude":
            return (
                f"That result helps. For {request}, the main thing I notice is {focus}, and I would use it to tighten the guardrails before making a public recommendation."
            )
        if agent.agent_id == "gemini":
            return (
                f"Useful result. For {request}, I would translate {focus} into a simpler user-facing flow before sharing it outside this box."
            )
        if agent.agent_id == "grok":
            return (
                f"Good. For {request}, the sharpest takeaway is {focus}, and I would use that to pressure-test the idea before it goes back into the room."
            )
        return (
            f"Thanks. For {request}, the simple takeaway is {focus}. I can keep this private or turn it into a short plain-English summary for the room."
        )

    def _queue_sentence_locked(self, current_agent_id: str) -> str:
        if not self.hand_queue:
            return "Right now nobody else is asking for the mic."
        next_id = self.hand_queue[0]
        if next_id == current_agent_id and len(self.hand_queue) > 1:
            next_id = self.hand_queue[1]
        if next_id == current_agent_id:
            return "I do not see another raised hand after this."
        return f"{self.agents[next_id].name} looks like the next speaker after me."

    def _focus_phrase_locked(self) -> str:
        source = ""
        latest = self._latest_public_message_locked()
        if latest is not None:
            source = latest["content"]
        return self._focus_from_text_locked(source)

    def _focus_from_text_locked(self, source: str) -> str:
        words: list[str] = []
        seen: set[str] = set()
        for raw_word in re.findall(r"[A-Za-z][A-Za-z'-]+", source.lower()):
            word = raw_word.strip("'")
            if len(word) < 4 or word in STOPWORDS or word in seen:
                continue
            words.append(word)
            seen.add(word)
            if len(words) == 3:
                break
        if not words:
            return "the shared room"
        return " / ".join(words)

    def _previous_speaker_locked(self, current_agent_id: str) -> str:
        for message in reversed(self.transcript):
            if message["role"] == "assistant" and message["agent_id"] != current_agent_id:
                return message["display_name"]
            if message["role"] == "user":
                return "You"
        return "The room"

    def _summary_sentence_locked(self) -> str:
        if self.summary_upto_index == 0:
            return "The summary panel is still empty because the room has not gotten crowded yet."
        return (
            f"The summary panel already covers {self.summary_upto_index} earlier messages, so older context stays short without disappearing."
        )


ROOM = ConversationRoom()


class PrototypeHandler(BaseHTTPRequestHandler):
    server_version = "MultiAIPrototype/0.4"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self._send_json(ROOM.snapshot())
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        body = self._read_json_body()
        try:
            if parsed.path == "/api/send":
                payload = ROOM.send_user_message(str(body.get("message", "")))
            elif parsed.path == "/api/continue":
                payload = ROOM.continue_round()
            elif parsed.path == "/api/resume":
                payload = ROOM.resume()
            elif parsed.path == "/api/reset":
                payload = ROOM.reset()
            elif parsed.path == "/api/config":
                payload = ROOM.set_strict_mode(bool(body.get("strict_mode", True)))
            else:
                top_up_match = re.fullmatch(r"/api/agents/([a-z0-9_-]+)/topup", parsed.path)
                workspace_send_match = re.fullmatch(r"/api/workspaces/([a-z0-9_-]+)/send", parsed.path)
                workspace_share_match = re.fullmatch(r"/api/workspaces/([a-z0-9_-]+)/share-latest", parsed.path)
                workspace_request_sim_match = re.fullmatch(r"/api/workspaces/([a-z0-9_-]+)/request-simulation", parsed.path)
                workspace_submit_sim_match = re.fullmatch(r"/api/workspaces/([a-z0-9_-]+)/submit-simulation", parsed.path)
                if top_up_match:
                    payload = ROOM.top_up(top_up_match.group(1), int(body.get("amount", 250)))
                elif workspace_send_match:
                    payload = ROOM.send_private_message(workspace_send_match.group(1), str(body.get("message", "")))
                elif workspace_share_match:
                    payload = ROOM.share_workspace_latest(workspace_share_match.group(1))
                elif workspace_request_sim_match:
                    payload = ROOM.request_simulation(workspace_request_sim_match.group(1), str(body.get("request", "")))
                elif workspace_submit_sim_match:
                    payload = ROOM.submit_simulation_result(workspace_submit_sim_match.group(1), str(body.get("result", "")))
                else:
                    self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
                    return
        except RoomError as exc:
            self._send_json({"error": str(exc), "state": ROOM.snapshot()}, status=HTTPStatus.CONFLICT)
            return
        except ValueError:
            self._send_json({"error": "Invalid numeric value."}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RoomError(f"Invalid JSON payload: {exc.msg}") from exc

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_static(self, raw_path: str) -> None:
        path = raw_path or "/"
        if path == "/":
            candidate = STATIC_DIR / "index.html"
        else:
            candidate = (STATIC_DIR / path.lstrip("/")).resolve()
            if STATIC_DIR.resolve() not in candidate.parents:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
        if not candidate.exists() or not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", self._content_type(candidate))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _content_type(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".html":
            return "text/html; charset=utf-8"
        if suffix == ".js":
            return "application/javascript; charset=utf-8"
        if suffix == ".css":
            return "text/css; charset=utf-8"
        return "text/plain; charset=utf-8"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-AI chat prototype.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the local server to.")
    parser.add_argument("--port", type=int, default=8008, help="Port to bind the local server to.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), PrototypeHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Multi-AI prototype running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
