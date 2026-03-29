const state = {
  data: null,
  mode: window.location.protocol === "file:" ? "local" : "server",
  autoPlay: false,
  autoPlayDelayMs: 900,
  autoPlayTimer: null,
  continueInFlight: false,
  selectedWorkspace: "codex",
};

const STOPWORDS = new Set([
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
]);

const AGENT_ALIASES = {
  codex: ["codex", "openai"],
  claude: ["claude", "anthropic"],
  gemini: ["gemini", "google"],
  grok: ["grok", "xai", "x.ai"],
  chatgpt: ["chatgpt", "chat gpt", "gpt"],
};

const SPEAKER_KEYWORDS = {
  codex: ["build", "code", "simulation", "sim", "tool", "bug", "system", "platform", "upgrade", "queue", "turn"],
  claude: ["safe", "risk", "guard", "policy", "careful", "pause", "rule", "trust"],
  gemini: ["design", "ui", "ux", "screen", "product", "look", "flow", "interface"],
  grok: ["critic", "stress", "challenge", "debate", "argue", "problem", "mess", "weird"],
  chatgpt: ["explain", "teach", "simple", "understand", "help", "idea", "plain", "beginner"],
};

const BROAD_DISCUSSION_WORDS = ["all", "everyone", "group", "compare", "debate", "both", "together", "team"];

class LocalRoom {
  constructor() {
    this.resetInternal();
  }

  snapshot() {
    return JSON.parse(JSON.stringify({
      strict_mode: this.strictMode,
      paused: this.paused,
      pause_reason: this.pauseReason,
      pending_round: this.pendingRound,
      pending_reason: this.pendingReason,
      round_index: this.roundIndex,
      summary: this.summary,
      summary_message_count: this.summaryUptoIndex,
      last_event: this.lastEvent,
      hand_queue: this.handQueue,
      next_speaker: this.nextSpeaker,
      direct_target: this.directTarget,
      workspaces: this.agentOrder.map((agentId) => {
        const workspace = this.workspaces[agentId];
        const agent = this.agents[agentId];
        const latestShareable = this.latestWorkspaceAssistant(agentId);
        const requiredPrivateTokens = this.estimatePrivateCost(agent);
        return {
          agent_id: agentId,
          name: agent.name,
          messages: workspace.messages,
          last_event: workspace.lastEvent,
          share_count: workspace.shareCount,
          last_cost: workspace.lastCost,
          simulation_status: workspace.simulationStatus,
          simulation_request: workspace.simulationRequest,
          last_simulation_result: workspace.lastSimulationResult,
          simulation_request_count: workspace.simulationRequestCount,
          simulation_result_count: workspace.simulationResultCount,
          required_private_tokens: requiredPrivateTokens,
          can_send_private: agent.tokens_remaining >= requiredPrivateTokens,
          has_shareable_message: Boolean(
            latestShareable && latestShareable.id !== workspace.lastSharedMessageId,
          ),
        };
      }),
      agents: this.agentOrder.map((agentId) => {
        const agent = this.agents[agentId];
        const required = this.estimateCost(agent);
        return {
          ...agent,
          required_next_tokens: required,
          can_speak_next_round: agent.tokens_remaining >= required,
          is_next_speaker: agentId === this.nextSpeaker,
        };
      }),
      transcript: this.transcript,
    }));
  }

  reset() {
    this.resetInternal();
    return this.snapshot();
  }

  sendPrivateMessage(agentId, content) {
    const text = String(content || "").trim();
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Unknown agent: ${agentId}`);
    }
    if (!text) {
      throw new Error("Type a private note before sending.");
    }

    const required = this.estimatePrivateCost(agent, text);
    if (agent.tokens_remaining < required) {
      const deficit = required - agent.tokens_remaining;
      throw new Error(`${agent.name} needs ${required} tokens for this private turn but only has ${agent.tokens_remaining}. Add at least ${deficit} tokens first.`);
    }

    const workspace = this.workspaces[agentId];
    this.appendWorkspaceMessage(agentId, "user", "You", text);
    agent.tokens_remaining -= required;
    agent.last_cost = required;
    agent.messages_sent += 1;
    const reply = this.generatePrivateReply(agent, text, workspace);
    this.appendWorkspaceMessage(agentId, "assistant", agent.name, reply);
    workspace.lastEvent = `${agent.name} replied in its private box.`;
    workspace.lastCost = required;
    this.lastEvent = `${agent.name} did private work. The public queue is unchanged.`;
    return this.snapshot();
  }

  shareWorkspaceLatest(agentId) {
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Unknown agent: ${agentId}`);
    }
    if (this.paused) {
      throw new Error("The public room is paused. Resume it before sharing private work.");
    }

    const workspace = this.workspaces[agentId];
    const latest = this.latestWorkspaceAssistant(agentId);
    if (!latest) {
      throw new Error(`${agent.name} has no private result to share yet.`);
    }
    if (latest.id === workspace.lastSharedMessageId) {
      throw new Error("The latest private result is already in the room.");
    }

    this.directTarget = null;
    this.appendMessage("assistant", agent.name, agentId, `From private box: ${latest.content}`);
    this.updateSummary();
    workspace.shareCount += 1;
    workspace.lastSharedMessageId = latest.id;
    workspace.lastEvent = `Shared result ${workspace.shareCount} back to the room.`;
    this.prepareQueue("workspace_share");
    this.lastEvent = this.nextSpeaker
      ? `${agent.name} shared a private result to the room. ${this.agents[this.nextSpeaker].name} has the mic next.`
      : `${agent.name} shared a private result to the room. Nobody else wants the mic right now.`;
    return this.snapshot();
  }

  requestSimulation(agentId, request) {
    const text = String(request || "").trim();
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Unknown agent: ${agentId}`);
    }
    if (!text) {
      throw new Error("Describe the simulation before requesting it.");
    }

    const workspace = this.workspaces[agentId];
    workspace.simulationStatus = "waiting_on_user";
    workspace.simulationRequest = text;
    workspace.lastSimulationResult = "";
    workspace.simulationRequestCount += 1;
    this.appendWorkspaceMessage(agentId, "system", "Simulation Request", `${agent.name} needs you to run a simulation: ${text}`);
    workspace.lastEvent = "Simulation requested. Waiting on you to run it outside the room.";
    this.lastEvent = `${agent.name} asked for a simulation. The public queue is unchanged.`;
    return this.snapshot();
  }

  submitSimulationResult(agentId, result) {
    const text = String(result || "").trim();
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Unknown agent: ${agentId}`);
    }
    if (!text) {
      throw new Error("Paste a simulation result before sending it back.");
    }

    const workspace = this.workspaces[agentId];
    if (workspace.simulationStatus !== "waiting_on_user") {
      throw new Error(`${agent.name} does not have an open simulation request right now.`);
    }

    this.appendWorkspaceMessage(agentId, "user", "Simulation Result", text);
    const reply = this.generateSimulationReview(agent, text, workspace);
    this.appendWorkspaceMessage(agentId, "assistant", agent.name, reply);
    workspace.simulationStatus = "result_received";
    workspace.lastSimulationResult = text;
    workspace.simulationResultCount += 1;
    workspace.lastEvent = "Simulation result received and reviewed privately.";
    this.lastEvent = `${agent.name} reviewed a simulation result in its private box. The public queue is unchanged.`;
    return this.snapshot();
  }

  sendUserMessage(content) {
    const text = String(content || "").trim();
    if (!text) {
      throw new Error("Type a message before sending.");
    }
    if (this.paused) {
      throw new Error("The room is paused. Add tokens and resume first.");
    }
    this.clearQueue();
    this.directTarget = this.detectDirectTarget(text);
    this.appendMessage("user", "You", "user", text);
    this.updateSummary();
    this.prepareQueue("user");
    this.lastEvent = this.nextSpeaker
      ? this.directTarget
        ? `Message sent. Directed to ${this.agents[this.nextSpeaker].name}; ${this.agents[this.nextSpeaker].name} has the mic next.`
        : `Message sent. ${this.agents[this.nextSpeaker].name} has the mic next.`
      : "Message sent. Nobody raised a hand yet.";
    return this.snapshot();
  }

  continueRound() {
    if (this.paused) {
      throw new Error("The room is paused. Add tokens and resume first.");
    }
    if (this.handQueue.length === 0) {
      this.prepareQueue("continue");
      if (this.handQueue.length === 0) {
        this.lastEvent = "Nobody wants the mic right now.";
        return this.snapshot();
      }
    }

    while (this.handQueue.length > 0) {
      const speakerId = this.handQueue[0];
      const speaker = this.agents[speakerId];
      const required = this.estimateCost(speaker);
      if (speaker.tokens_remaining < required) {
        if (this.strictMode) {
          this.pendingRound = true;
          this.pendingReason = `${speaker.name} has the mic next.`;
          this.pause(speakerId);
          return this.snapshot();
        }
        this.handQueue.shift();
        if (speakerId === this.directTarget) {
          this.directTarget = null;
        }
        continue;
      }

      this.handQueue.shift();
      this.roundIndex += 1;
      this.pendingRound = this.handQueue.length > 0;
      this.pendingReason = "";
      speaker.tokens_remaining -= required;
      speaker.last_cost = required;
      speaker.messages_sent += 1;
      speaker.status = "speaking";
      this.directTarget = null;
      this.appendMessage("assistant", speaker.name, speaker.agent_id, this.generateReply(speaker));
      this.updateSummary();

      if (this.handQueue.length === 0) {
        this.prepareQueue("follow_up");
      } else {
        this.applyStatuses();
      }

      this.lastEvent = this.nextSpeaker
        ? `${speaker.name} spoke. ${this.agents[this.nextSpeaker].name} is up next.`
        : `${speaker.name} spoke. Nobody else wants the mic right now.`;
      return this.snapshot();
    }

    this.lastEvent = "Nobody wants the mic right now.";
    this.applyStatuses();
    return this.snapshot();
  }

  topUp(agentId, amount) {
    const numericAmount = Number(amount);
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Unknown agent: ${agentId}`);
    }
    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      throw new Error("Top-up amount must be positive.");
    }
    agent.tokens_remaining += numericAmount;
    this.lastEvent = `Added ${numericAmount} tokens to ${agent.name}.`;
    this.applyStatuses();
    return this.snapshot();
  }

  resume() {
    if (!this.paused) {
      this.lastEvent = "The room was already active.";
      return this.snapshot();
    }
    this.paused = false;
    this.pauseReason = "";
    this.lastEvent = "Room resumed. Let the next speaker take their turn.";
    this.applyStatuses();
    return this.snapshot();
  }

  setStrictMode(enabled) {
    this.strictMode = Boolean(enabled);
    this.lastEvent = `Switched to ${this.strictMode ? "strict pause" : "flexible skip"} mode.`;
    this.applyStatuses();
    return this.snapshot();
  }

  resetInternal() {
    this.strictMode = true;
    this.paused = false;
    this.pauseReason = "";
    this.pendingRound = false;
    this.pendingReason = "";
    this.roundIndex = 0;
    this.summary = "";
    this.summaryUptoIndex = 0;
    this.messageId = 1;
    this.lastEvent = "Room ready. Send a message to begin.";
    this.handQueue = [];
    this.nextSpeaker = null;
    this.directTarget = null;
    this.agents = {
      codex: { agent_id: "codex", name: "Codex", tagline: "builder", color: "#d78143", tokens_remaining: 420, base_cost: 120, last_cost: 0, messages_sent: 0, status: "waiting" },
      claude: { agent_id: "claude", name: "Claude", tagline: "guardrails", color: "#c95b36", tokens_remaining: 390, base_cost: 108, last_cost: 0, messages_sent: 0, status: "waiting" },
      gemini: { agent_id: "gemini", name: "Gemini", tagline: "product sense", color: "#2f7f6d", tokens_remaining: 360, base_cost: 102, last_cost: 0, messages_sent: 0, status: "waiting" },
      grok: { agent_id: "grok", name: "Grok", tagline: "stress tests", color: "#335c91", tokens_remaining: 330, base_cost: 96, last_cost: 0, messages_sent: 0, status: "waiting" },
      chatgpt: { agent_id: "chatgpt", name: "ChatGPT", tagline: "plain English", color: "#85634e", tokens_remaining: 405, base_cost: 110, last_cost: 0, messages_sent: 0, status: "waiting" },
    };
    this.agentOrder = ["codex", "claude", "gemini", "grok", "chatgpt"];
    this.workspaces = Object.fromEntries(this.agentOrder.map((agentId) => [agentId, {
      messages: [],
      nextMessageId: 1,
      lastEvent: `${this.agents[agentId].name}'s private box is idle.`,
      shareCount: 0,
      lastSharedMessageId: 0,
      lastCost: 0,
      simulationStatus: "idle",
      simulationRequest: "",
      lastSimulationResult: "",
      simulationRequestCount: 0,
      simulationResultCount: 0,
    }]));
    this.transcript = [];
    this.appendMessage(
      "system",
      "System",
      "system",
      "Room booted. One speaker talks at a time, agents can raise a hand or pass, and strict pause mode stops the room if the next speaker cannot afford a turn.",
    );
    this.applyStatuses();
  }

  clearQueue() {
    this.handQueue = [];
    this.nextSpeaker = null;
    this.pendingRound = false;
    this.pendingReason = "";
    this.applyStatuses();
  }

  prepareQueue(source) {
    void source;
    const latest = this.latestPublicMessage();
    if (!latest) {
      this.handQueue = [];
      this.nextSpeaker = null;
      this.pendingRound = false;
      this.pendingReason = "";
      this.applyStatuses();
      return;
    }

    const queue = this.decideQueue(latest);
    this.handQueue = queue;
    this.nextSpeaker = queue.length ? queue[0] : null;
    this.pendingRound = queue.length > 0;
    this.pendingReason = this.nextSpeaker ? `${this.agents[this.nextSpeaker].name} has the mic next.` : "";
    this.applyStatuses();
  }

  decideQueue(latest) {
    if (latest.role === "user" && this.directTarget) {
      return [this.directTarget];
    }

    const mentioned = this.detectMentions(latest.content, new Set([latest.agent_id]));
    const queue = [];

    if (latest.role === "user") {
      if (mentioned.length) {
        queue.push(...mentioned.slice(0, 3));
      } else {
        const primary = this.pickBestSpeaker(latest.content);
        if (primary) {
          queue.push(primary);
        }
        if (this.shouldAddSecondSpeaker(latest.content)) {
          const secondary = this.pickBestSpeaker(latest.content, new Set(queue));
          if (secondary) {
            queue.push(secondary);
          }
        }
      }
    } else {
      if (mentioned.length) {
        queue.push(...mentioned.slice(0, 2));
      } else {
        const depth = this.assistantDepth();
        if (depth < 3) {
          const followUp = this.pickFollowUpSpeaker(latest.agent_id, latest.content);
          if (followUp) {
            queue.push(followUp);
          }
          if (depth < 2 && this.shouldAddSecondSpeaker(latest.content)) {
            const exclude = new Set([latest.agent_id, ...queue]);
            const secondary = this.pickBestSpeaker(latest.content, exclude);
            if (secondary) {
              queue.push(secondary);
            }
          }
        }
      }
    }

    return this.dedupeAgentIds(queue);
  }

  applyStatuses() {
    const latestExists = Boolean(this.latestPublicMessage());
    const baseStatus = latestExists ? "passed" : "waiting";
    Object.values(this.agents).forEach((agent) => {
      agent.status = baseStatus;
    });

    if (this.handQueue.length) {
      this.nextSpeaker = this.handQueue[0];
      this.agents[this.handQueue[0]].status = this.paused ? "paused" : "thinking";
      for (const agentId of this.handQueue.slice(1)) {
        this.agents[agentId].status = "raised_hand";
      }
    } else {
      this.nextSpeaker = null;
    }
  }

  pause(agentId) {
    const agent = this.agents[agentId];
    const required = this.estimateCost(agent);
    const deficit = required - agent.tokens_remaining;
    this.paused = true;
    this.pauseReason = `${agent.name} has the mic next, but it needs ${required} tokens and only has ${agent.tokens_remaining}. Add at least ${deficit} tokens and then resume.`;
    this.lastEvent = "Turn queue paused because strict mode requires the next speaker to be ready.";
    this.applyStatuses();
  }

  estimateCost(agent) {
    const summaryTax = Math.min(26, Math.floor(this.summary.length / 90));
    const roundTax = Math.min(24, this.roundIndex * 2);
    return agent.base_cost + summaryTax + roundTax;
  }

  estimatePrivateCost(agent, text = "") {
    const workspace = this.workspaces[agent.agent_id];
    const base = Math.max(52, agent.base_cost - 42);
    const wordTax = Math.min(12, Math.floor(String(text).split(/\s+/).filter(Boolean).length / 6));
    const historyTax = Math.min(10, Math.floor(workspace.messages.length / 4));
    return base + wordTax + historyTax;
  }

  appendMessage(role, displayName, agentId, content) {
    this.transcript.push({
      id: this.messageId,
      role,
      display_name: displayName,
      agent_id: agentId,
      content,
      round: this.roundIndex,
    });
    this.messageId += 1;
  }

  appendWorkspaceMessage(agentId, role, displayName, content) {
    const workspace = this.workspaces[agentId];
    workspace.messages.push({
      id: workspace.nextMessageId,
      role,
      display_name: displayName,
      agent_id: agentId,
      content,
    });
    workspace.nextMessageId += 1;
  }

  updateSummary() {
    const recentWindow = 8;
    const summaryTrigger = 14;
    const maxSummaryLines = 14;

    if (this.transcript.length - this.summaryUptoIndex <= summaryTrigger) {
      return;
    }
    const archiveEnd = this.transcript.length - recentWindow;
    if (archiveEnd <= this.summaryUptoIndex) {
      return;
    }

    const lines = this.transcript
      .slice(this.summaryUptoIndex, archiveEnd)
      .filter((message) => message.role !== "system")
      .map((message) => `- ${message.display_name}: ${this.clipWords(message.content, 18)}`)
      .slice(-6);

    if (!lines.length) {
      this.summaryUptoIndex = archiveEnd;
      return;
    }

    const currentLines = this.summary ? this.summary.split("\n").filter(Boolean) : [];
    currentLines.push(...lines);
    this.summary = currentLines.length > maxSummaryLines
      ? ["- Earlier discussion compressed.", ...currentLines.slice(-(maxSummaryLines - 1))].join("\n")
      : currentLines.join("\n");
    this.summaryUptoIndex = archiveEnd;
  }

  clipWords(text, limit) {
    const words = String(text).split(/\s+/);
    const clipped = words.slice(0, limit).join(" ").trim();
    return words.length > limit ? `${clipped}...` : clipped;
  }

  latestPublicMessage() {
    for (let index = this.transcript.length - 1; index >= 0; index -= 1) {
      if (this.transcript[index].role !== "system") {
        return this.transcript[index];
      }
    }
    return null;
  }

  latestWorkspaceAssistant(agentId) {
    const workspace = this.workspaces[agentId];
    for (let index = workspace.messages.length - 1; index >= 0; index -= 1) {
      if (workspace.messages[index].role === "assistant") {
        return workspace.messages[index];
      }
    }
    return null;
  }

  assistantDepth() {
    let depth = 0;
    for (let index = this.transcript.length - 1; index >= 0; index -= 1) {
      const message = this.transcript[index];
      if (message.role === "assistant") {
        depth += 1;
        continue;
      }
      if (message.role === "user") {
        break;
      }
    }
    return depth;
  }

  detectMentions(text, exclude = new Set()) {
    const lowered = String(text).toLowerCase();
    const hits = [];
    for (const agentId of this.agentOrder) {
      if (exclude.has(agentId)) {
        continue;
      }
      const positions = AGENT_ALIASES[agentId]
        .map((alias) => lowered.indexOf(alias))
        .filter((position) => position !== -1);
      if (positions.length) {
        hits.push([Math.min(...positions), agentId]);
      }
    }
    hits.sort((left, right) => left[0] - right[0]);
    return hits.map((entry) => entry[1]);
  }

  detectDirectTarget(text) {
    const lowered = String(text).toLowerCase();
    const hits = [];
    for (const agentId of this.agentOrder) {
      for (const alias of AGENT_ALIASES[agentId]) {
        const escaped = alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const patterns = [
          new RegExp(`^\\s*@?${escaped}\\b(?:[\\s,:-]|$)`),
          new RegExp(`\\b(?:to|for|ask|tell|let|have)\\s+@?${escaped}\\b`),
        ];
        const positions = patterns
          .map((pattern) => lowered.search(pattern))
          .filter((position) => position !== -1);
        if (positions.length) {
          hits.push([Math.min(...positions), agentId]);
          break;
        }
      }
    }

    if (!hits.length) {
      return null;
    }
    hits.sort((left, right) => left[0] - right[0]);
    return hits[0][1];
  }

  pickBestSpeaker(text, exclude = new Set()) {
    const lowered = String(text).toLowerCase();
    let bestId = null;
    let bestScore = -1;

    this.agentOrder.forEach((agentId, offset) => {
      if (exclude.has(agentId)) {
        return;
      }
      let score = agentId === "chatgpt" ? 1 : 0;
      for (const keyword of SPEAKER_KEYWORDS[agentId]) {
        if (lowered.includes(keyword)) {
          score += 2;
        }
      }
      score += (this.agentOrder.length - ((this.roundIndex + offset) % this.agentOrder.length)) * 0.01;
      if (score > bestScore) {
        bestScore = score;
        bestId = agentId;
      }
    });

    return bestId;
  }

  pickFollowUpSpeaker(lastAgentId, text) {
    const mentioned = this.detectMentions(text, new Set([lastAgentId]));
    if (mentioned.length) {
      return mentioned[0];
    }
    return this.pickBestSpeaker(text, new Set([lastAgentId]));
  }

  shouldAddSecondSpeaker(text) {
    const lowered = String(text).toLowerCase();
    return BROAD_DISCUSSION_WORDS.some((word) => lowered.includes(word));
  }

  dedupeAgentIds(agentIds) {
    const seen = new Set();
    const ordered = [];
    for (const agentId of agentIds) {
      if (!this.agents[agentId] || seen.has(agentId)) {
        continue;
      }
      seen.add(agentId);
      ordered.push(agentId);
    }
    return ordered;
  }

  generateReply(agent) {
    const focus = this.focusPhrase();
    const previousSpeaker = this.previousSpeaker(agent.agent_id);
    const summarySentence = this.summarySentence();
    const queueSentence = this.queueSentence(agent.agent_id);

    if (agent.agent_id === "codex") {
      return `I can take this one. For ${focus}, I would keep the next step concrete and testable. ${queueSentence} ${summarySentence}`;
    }
    if (agent.agent_id === "claude") {
      return `I want to keep the rules clear here. ${previousSpeaker} covered the direction, and I would make sure the stop conditions stay visible to the user. ${queueSentence} ${summarySentence}`;
    }
    if (agent.agent_id === "gemini") {
      return `From the user's side, ${focus} should feel calm and readable. ${queueSentence} ${summarySentence}`;
    }
    if (agent.agent_id === "grok") {
      return `I'll stress-test it. If ${focus} gets vague, the room gets messy fast, so I would rather keep one clear turn at a time. ${queueSentence} ${summarySentence}`;
    }
    return `Here is the plain-English version. ${focus} works better when one speaker goes at a time and the others either wait or pass. ${queueSentence} ${summarySentence}`;
  }

  generatePrivateReply(agent, prompt, workspace) {
    const focus = this.focusFromText(prompt);
    const shareSentence = workspace.shareCount === 0
      ? "Nothing from this box reaches the room until you press Share Latest To Room."
      : `This box has already shared ${workspace.shareCount} result(s) to the room.`;

    if (agent.agent_id === "codex") {
      return `Private box note: I would treat ${focus} like a work item and break it into concrete steps, quick tests, and the smallest useful change. ${shareSentence}`;
    }
    if (agent.agent_id === "claude") {
      return `Private box note: I would look at edge cases, failure modes, and whether ${focus} needs clearer rules before it goes public. ${shareSentence}`;
    }
    if (agent.agent_id === "gemini") {
      return `Private box note: I would turn ${focus} into a cleaner user flow, better labels, and a calmer screen before sharing it with the room. ${shareSentence}`;
    }
    if (agent.agent_id === "grok") {
      return `Private box note: I would try to poke holes in ${focus}, find what breaks first, and come back with the sharpest objections. ${shareSentence}`;
    }
    return `Private box note: here is the simple version of ${focus}. I would turn it into a cleaner explanation before sending it back to everyone else. ${shareSentence}`;
  }

  generateSimulationReview(agent, result, workspace) {
    const focus = this.focusFromText(result);
    const request = this.clipWords(workspace.simulationRequest, 18);

    if (agent.agent_id === "codex") {
      return `Thanks. For the simulation request about ${request}, the signal I would pull forward is ${focus}. I would keep refining this privately, then share a short conclusion back to the room if it is useful.`;
    }
    if (agent.agent_id === "claude") {
      return `That result helps. For ${request}, the main thing I notice is ${focus}, and I would use it to tighten the guardrails before making a public recommendation.`;
    }
    if (agent.agent_id === "gemini") {
      return `Useful result. For ${request}, I would translate ${focus} into a simpler user-facing flow before sharing it outside this box.`;
    }
    if (agent.agent_id === "grok") {
      return `Good. For ${request}, the sharpest takeaway is ${focus}, and I would use that to pressure-test the idea before it goes back into the room.`;
    }
    return `Thanks. For ${request}, the simple takeaway is ${focus}. I can keep this private or turn it into a short plain-English summary for the room.`;
  }

  queueSentence(currentAgentId) {
    if (!this.handQueue.length) {
      return "Right now nobody else is asking for the mic.";
    }
    let nextId = this.handQueue[0];
    if (nextId === currentAgentId && this.handQueue.length > 1) {
      nextId = this.handQueue[1];
    }
    if (nextId === currentAgentId) {
      return "I do not see another raised hand after this.";
    }
    return `${this.agents[nextId].name} looks like the next speaker after me.`;
  }

  focusPhrase() {
    const latest = this.latestPublicMessage();
    const source = latest ? latest.content : "";
    return this.focusFromText(source);
  }

  focusFromText(source) {
    const words = [];
    const seen = new Set();
    const matches = String(source).toLowerCase().match(/[a-z][a-z'-]+/g) || [];
    for (const raw of matches) {
      const word = raw.replace(/^'+|'+$/g, "");
      if (word.length < 4 || STOPWORDS.has(word) || seen.has(word)) {
        continue;
      }
      words.push(word);
      seen.add(word);
      if (words.length === 3) {
        break;
      }
    }
    return words.length ? words.join(" / ") : "the shared room";
  }

  previousSpeaker(currentAgentId) {
    for (let index = this.transcript.length - 1; index >= 0; index -= 1) {
      const message = this.transcript[index];
      if (message.role === "assistant" && message.agent_id !== currentAgentId) {
        return message.display_name;
      }
      if (message.role === "user") {
        return "You";
      }
    }
    return "The room";
  }

  summarySentence() {
    if (this.summaryUptoIndex === 0) {
      return "The summary panel is still empty because the room has not gotten crowded yet.";
    }
    return `The summary panel already covers ${this.summaryUptoIndex} earlier messages, so older context stays short without disappearing.`;
  }
}

const localRoom = new LocalRoom();

async function api(path, options = {}) {
  if (state.mode === "local") {
    return localDispatch(path, options);
  }

  try {
    const response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw payload;
    }
    return payload;
  } catch (error) {
    if (error && typeof error === "object" && Object.prototype.hasOwnProperty.call(error, "error")) {
      throw error;
    }
    state.mode = "local";
    return localDispatch(path, options);
  }
}

async function localDispatch(path, options = {}) {
  const body = options.body ? JSON.parse(options.body) : {};

  try {
    if (path === "/api/state") {
      return localRoom.snapshot();
    }
    if (path === "/api/send") {
      return localRoom.sendUserMessage(body.message);
    }
    if (path === "/api/continue") {
      return localRoom.continueRound();
    }
    if (path === "/api/resume") {
      return localRoom.resume();
    }
    if (path === "/api/reset") {
      return localRoom.reset();
    }
    if (path === "/api/config") {
      return localRoom.setStrictMode(body.strict_mode);
    }
    const topUpMatch = path.match(/^\/api\/agents\/([a-z0-9_-]+)\/topup$/i);
    const workspaceSendMatch = path.match(/^\/api\/workspaces\/([a-z0-9_-]+)\/send$/i);
    const workspaceShareMatch = path.match(/^\/api\/workspaces\/([a-z0-9_-]+)\/share-latest$/i);
    const workspaceRequestSimMatch = path.match(/^\/api\/workspaces\/([a-z0-9_-]+)\/request-simulation$/i);
    const workspaceSubmitSimMatch = path.match(/^\/api\/workspaces\/([a-z0-9_-]+)\/submit-simulation$/i);
    if (topUpMatch) {
      return localRoom.topUp(topUpMatch[1], body.amount ?? 250);
    }
    if (workspaceSendMatch) {
      return localRoom.sendPrivateMessage(workspaceSendMatch[1], body.message);
    }
    if (workspaceShareMatch) {
      return localRoom.shareWorkspaceLatest(workspaceShareMatch[1]);
    }
    if (workspaceRequestSimMatch) {
      return localRoom.requestSimulation(workspaceRequestSimMatch[1], body.request);
    }
    if (workspaceSubmitSimMatch) {
      return localRoom.submitSimulationResult(workspaceSubmitSimMatch[1], body.result);
    }
    throw new Error("Not found");
  } catch (error) {
    throw {
      error: error.message || "Request failed.",
      state: localRoom.snapshot(),
    };
  }
}

function showBanner(message, kind = "warning") {
  const banner = document.getElementById("banner");
  banner.textContent = message;
  banner.dataset.kind = kind;
  banner.classList.remove("hidden");
}

function clearBanner() {
  const banner = document.getElementById("banner");
  banner.textContent = "";
  banner.classList.add("hidden");
}

function cancelAutoPlay() {
  if (state.autoPlayTimer !== null) {
    window.clearTimeout(state.autoPlayTimer);
    state.autoPlayTimer = null;
  }
}

function statusLabel(status) {
  const labels = {
    thinking: "thinking",
    raised_hand: "hand up",
    speaking: "speaking",
    passed: "passed",
    waiting: "waiting",
    paused: "paused",
  };
  return labels[status] || status;
}

function renderRoster(data) {
  const roster = document.getElementById("roster");
  roster.innerHTML = "";

  for (const agent of data.agents) {
    const card = document.createElement("section");
    card.className = "agent-card";
    card.style.setProperty("--accent", agent.color);

    const topUpButton = document.createElement("button");
    topUpButton.className = "ghost";
    topUpButton.textContent = "+250 tokens";
    topUpButton.addEventListener("click", async () => {
      try {
        const updated = await api(`/api/agents/${agent.agent_id}/topup`, {
          method: "POST",
          body: JSON.stringify({ amount: 250 }),
        });
        render(updated);
      } catch (error) {
        handleError(error);
      }
    });

    card.innerHTML = `
      <div class="agent-head">
        <div>
          <h3>${agent.name}</h3>
          <p>${agent.tagline}</p>
        </div>
        <span class="agent-status ${agent.status}">${statusLabel(agent.status)}</span>
      </div>
      <dl class="agent-stats">
        <div><dt>Tokens left</dt><dd>${agent.tokens_remaining}</dd></div>
        <div><dt>Next turn cost</dt><dd>${agent.required_next_tokens}</dd></div>
        <div><dt>Last cost</dt><dd>${agent.last_cost || "n/a"}</dd></div>
        <div><dt>Replies sent</dt><dd>${agent.messages_sent}</dd></div>
      </dl>
    `;
    card.appendChild(topUpButton);
    roster.appendChild(card);
  }
}

function renderQueue(data) {
  const queueMeta = document.getElementById("queue-meta");
  const queueList = document.getElementById("queue-list");
  const autoPlayMeta = document.getElementById("auto-play-meta");
  const namesById = Object.fromEntries(data.agents.map((agent) => [agent.agent_id, agent.name]));
  const queueNames = data.hand_queue.map((agentId) => namesById[agentId]).filter(Boolean);

  if (!queueNames.length) {
    queueMeta.textContent = data.direct_target
      ? `Directed to ${namesById[data.direct_target]}, but no hand is up right now.`
      : "No hands are up right now.";
    queueList.textContent = "Everyone is currently passing.";
    queueList.classList.add("empty");
    autoPlayMeta.textContent = state.autoPlay
      ? "Auto-play is on, but there is no queued speaker right now."
      : "Auto-play is off. Advance the room manually.";
    return;
  }

  if (data.direct_target && namesById[data.direct_target]) {
    queueMeta.textContent = `Directed to ${namesById[data.direct_target]}. ${namesById[data.next_speaker]} has the mic next.`;
  } else {
    queueMeta.textContent = data.next_speaker
      ? `${namesById[data.next_speaker]} has the mic next.`
      : "A turn is pending.";
  }
  queueList.textContent = queueNames.join(" -> ");
  queueList.classList.remove("empty");
  autoPlayMeta.textContent = state.autoPlay
    ? "Auto-play is on. The client will advance the next turn automatically."
    : "Auto-play is off. Use the button if you want to step through the queue.";
}

function renderSummary(data) {
  const summary = document.getElementById("summary");
  const meta = document.getElementById("summary-meta");
  if (data.summary) {
    summary.textContent = data.summary;
    summary.classList.remove("empty");
    meta.textContent = `${data.summary_message_count} earlier messages compressed into the checkpoint summary.`;
  } else {
    summary.textContent = "The prototype will summarize older messages here once the transcript gets long enough.";
    summary.classList.add("empty");
    meta.textContent = "No messages have been condensed yet.";
  }
}

function renderWorkspaces(data) {
  const tabs = document.getElementById("workspace-tabs");
  const title = document.getElementById("workspace-title");
  const event = document.getElementById("workspace-event");
  const meta = document.getElementById("workspace-meta");
  const transcript = document.getElementById("workspace-transcript");
  const hint = document.getElementById("workspace-hint");
  const simStatus = document.getElementById("workspace-sim-status");
  const simMeta = document.getElementById("workspace-sim-meta");
  const shareButton = document.getElementById("workspace-share-btn");
  const sendButton = document.getElementById("workspace-send-btn");
  const requestButton = document.getElementById("workspace-sim-request-btn");
  const resultButton = document.getElementById("workspace-sim-result-btn");
  const requestField = document.getElementById("workspace-sim-request");
  const resultField = document.getElementById("workspace-sim-result");
  const agentById = Object.fromEntries(data.agents.map((agent) => [agent.agent_id, agent]));
  const selected = data.workspaces.find((workspace) => workspace.agent_id === state.selectedWorkspace)
    || data.workspaces[0];

  if (!selected) {
    tabs.innerHTML = "";
    title.textContent = "Private Box";
    event.textContent = "No private boxes available.";
    meta.textContent = "";
    transcript.innerHTML = "";
    hint.textContent = "Private work boxes are unavailable.";
    simStatus.textContent = "No simulation request is open.";
    simMeta.textContent = "Run simulations outside this room, then paste the result back here.";
    shareButton.disabled = true;
    sendButton.disabled = true;
    requestButton.disabled = true;
    resultButton.disabled = true;
    requestField.disabled = true;
    resultField.disabled = true;
    return;
  }

  state.selectedWorkspace = selected.agent_id;
  const selectedAgent = agentById[selected.agent_id];
  const tokensLeft = selectedAgent ? selectedAgent.tokens_remaining : 0;
  const privateDeficit = Math.max(0, selected.required_private_tokens - tokensLeft);
  const requestPreview = selected.simulation_request.length > 160
    ? `${selected.simulation_request.slice(0, 157)}...`
    : selected.simulation_request;
  tabs.innerHTML = "";
  for (const workspace of data.workspaces) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = workspace.agent_id === selected.agent_id ? "workspace-tab active" : "workspace-tab ghost";
    button.textContent = workspace.name;
    button.addEventListener("click", () => {
      state.selectedWorkspace = workspace.agent_id;
      render(state.data);
    });
    tabs.appendChild(button);
  }

  title.textContent = `${selected.name} Private Box`;
  event.textContent = selected.last_event;
  meta.textContent = `Tokens left: ${tokensLeft} | Shares: ${selected.share_count} | Last private cost: ${selected.last_cost || "n/a"} | Next private turn: ${selected.required_private_tokens} tokens`;
  transcript.innerHTML = "";

  if (!selected.messages.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-empty";
    empty.textContent = "No private work yet. Send a note here and keep the result off the main room until you decide to share it.";
    transcript.appendChild(empty);
  } else {
    for (const message of selected.messages) {
      const node = document.createElement("article");
      node.className = "workspace-message";
      node.dataset.role = message.role;
      node.innerHTML = `
        <div class="message-header">
          <strong class="message-author">${message.display_name}</strong>
          <span class="message-round">private</span>
        </div>
        <p class="message-body"></p>
      `;
      node.querySelector(".message-body").textContent = message.content;
      transcript.appendChild(node);
    }
  }

  transcript.scrollTop = transcript.scrollHeight;
  if (selected.simulation_status === "waiting_on_user") {
    simStatus.textContent = `${selected.name} is waiting on you to run a simulation.`;
    simMeta.textContent = `Open request: ${requestPreview}`;
  } else if (selected.simulation_status === "result_received") {
    simStatus.textContent = `${selected.name} has a simulation result in this box and can work from it privately or share the conclusion.`;
    simMeta.textContent = `Requests: ${selected.simulation_request_count} | Results received: ${selected.simulation_result_count}`;
  } else {
    simStatus.textContent = "No simulation request is open.";
    simMeta.textContent = "Run simulations outside this room, then paste the result back here.";
  }
  if (!selected.can_send_private && privateDeficit > 0) {
    hint.textContent = `${selected.name} needs ${privateDeficit} more tokens before it can take another private turn.`;
  } else if (data.paused && selected.has_shareable_message) {
    hint.textContent = "The public room is paused. You can keep working here, but sharing waits until you resume the room.";
  } else if (selected.has_shareable_message) {
    hint.textContent = "This box has a fresh result ready to share back to the room.";
  } else {
    hint.textContent = "Private notes stay here until there is a new assistant result to share. Private work can continue even if the main room is paused.";
  }
  shareButton.disabled = !selected.has_shareable_message || data.paused;
  sendButton.disabled = !selected.can_send_private;
  requestButton.disabled = false;
  resultButton.disabled = selected.simulation_status !== "waiting_on_user";
  requestField.disabled = false;
  resultField.disabled = selected.simulation_status !== "waiting_on_user";
}

function renderTranscript(data) {
  const transcript = document.getElementById("transcript");
  const template = document.getElementById("message-template");
  transcript.innerHTML = "";

  for (const message of data.transcript) {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.role = message.role;
    node.querySelector(".message-author").textContent = message.display_name;
    node.querySelector(".message-round").textContent = message.role === "system" ? "system" : `turn ${message.round}`;
    node.querySelector(".message-body").textContent = message.content;
    transcript.appendChild(node);
  }

  transcript.scrollTop = transcript.scrollHeight;
}

function render(data) {
  state.data = data;
  const hasPublicMessages = data.transcript.some((message) => message.role !== "system");
  const selectedWorkspace = data.workspaces.find((workspace) => workspace.agent_id === state.selectedWorkspace)
    || data.workspaces[0]
    || null;
  document.getElementById("strict-mode").checked = Boolean(data.strict_mode);
  document.getElementById("auto-play").checked = state.autoPlay;
  document.getElementById("last-event").textContent = state.mode === "local"
    ? `${data.last_event} Running in browser-only mock mode.`
    : data.last_event;
  document.getElementById("resume-btn").disabled = !data.paused;
  document.getElementById("continue-btn").disabled = data.paused || !hasPublicMessages || state.continueInFlight;
  document.getElementById("message").disabled = data.paused;
  document.getElementById("workspace-message").disabled = !selectedWorkspace;
  document.getElementById("workspace-send-btn").disabled = !selectedWorkspace || !selectedWorkspace.can_send_private;
  document.getElementById("workspace-sim-request").disabled = !selectedWorkspace;
  document.getElementById("workspace-sim-request-btn").disabled = !selectedWorkspace;
  document.getElementById("workspace-sim-result").disabled = !selectedWorkspace || selectedWorkspace.simulation_status !== "waiting_on_user";
  document.getElementById("workspace-sim-result-btn").disabled = !selectedWorkspace || selectedWorkspace.simulation_status !== "waiting_on_user";

  renderRoster(data);
  renderQueue(data);
  renderSummary(data);
  renderTranscript(data);
  renderWorkspaces(data);

  if (data.paused) {
    cancelAutoPlay();
    showBanner(data.pause_reason, "warning");
  } else {
    clearBanner();
    scheduleAutoPlayIfNeeded();
  }
}

async function advanceOneTurn() {
  if (state.continueInFlight) {
    return;
  }
  state.continueInFlight = true;
  cancelAutoPlay();
  try {
    const data = await api("/api/continue", { method: "POST", body: "{}" });
    render(data);
  } catch (error) {
    handleError(error);
  } finally {
    state.continueInFlight = false;
    if (state.data && !state.data.paused) {
      render(state.data);
    }
  }
}

function scheduleAutoPlayIfNeeded() {
  cancelAutoPlay();
  if (!state.autoPlay || !state.data || state.data.paused || state.continueInFlight) {
    return;
  }
  if (!state.data.next_speaker) {
    return;
  }
  state.autoPlayTimer = window.setTimeout(async () => {
    state.autoPlayTimer = null;
    await advanceOneTurn();
  }, state.autoPlayDelayMs);
}

function handleError(error) {
  if (error && error.state) {
    render(error.state);
  }
  const message = error?.error || "Request failed.";
  showBanner(message, "error");
}

async function loadState() {
  try {
    const data = await api("/api/state");
    render(data);
  } catch (error) {
    handleError(error);
  }
}

document.getElementById("composer").addEventListener("submit", async (event) => {
  event.preventDefault();
  const field = document.getElementById("message");
  const message = field.value.trim();
  if (!message) {
    showBanner("Type a message before sending.", "error");
    return;
  }
  try {
    const data = await api("/api/send", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    field.value = "";
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("workspace-composer").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedWorkspace) {
    return;
  }
  const field = document.getElementById("workspace-message");
  const message = field.value.trim();
  if (!message) {
    showBanner("Type a private note before sending.", "error");
    return;
  }
  try {
    const data = await api(`/api/workspaces/${state.selectedWorkspace}/send`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    field.value = "";
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("workspace-sim-request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedWorkspace) {
    return;
  }
  const field = document.getElementById("workspace-sim-request");
  const request = field.value.trim();
  if (!request) {
    showBanner("Describe the simulation before requesting it.", "error");
    return;
  }
  try {
    const data = await api(`/api/workspaces/${state.selectedWorkspace}/request-simulation`, {
      method: "POST",
      body: JSON.stringify({ request }),
    });
    field.value = "";
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("workspace-sim-result-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedWorkspace) {
    return;
  }
  const field = document.getElementById("workspace-sim-result");
  const result = field.value.trim();
  if (!result) {
    showBanner("Paste a simulation result before sending it back.", "error");
    return;
  }
  try {
    const data = await api(`/api/workspaces/${state.selectedWorkspace}/submit-simulation`, {
      method: "POST",
      body: JSON.stringify({ result }),
    });
    field.value = "";
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("workspace-share-btn").addEventListener("click", async () => {
  if (!state.selectedWorkspace) {
    return;
  }
  try {
    const data = await api(`/api/workspaces/${state.selectedWorkspace}/share-latest`, {
      method: "POST",
      body: "{}",
    });
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("continue-btn").addEventListener("click", async () => {
  await advanceOneTurn();
});

document.getElementById("resume-btn").addEventListener("click", async () => {
  try {
    const data = await api("/api/resume", { method: "POST", body: "{}" });
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("reset-btn").addEventListener("click", async () => {
  try {
    const data = await api("/api/reset", { method: "POST", body: "{}" });
    render(data);
    clearBanner();
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("strict-mode").addEventListener("change", async (event) => {
  try {
    const data = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({ strict_mode: event.target.checked }),
    });
    render(data);
  } catch (error) {
    handleError(error);
  }
});

document.getElementById("auto-play").addEventListener("change", (event) => {
  state.autoPlay = Boolean(event.target.checked);
  if (!state.autoPlay) {
    cancelAutoPlay();
  }
  if (state.data) {
    render(state.data);
  }
});

loadState();
window.setInterval(loadState, 4000);
