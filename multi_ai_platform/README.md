# Multi-AI Room Prototype

This folder contains a small local prototype for the platform you described:

- one shared transcript
- five mock AI participants
- hand-raise turn order with one speaker at a time
- explicit direct addressing such as `Claude, answer this`
- optional auto-play so the queue can advance on its own
- private work boxes for each AI
- share-latest flow to publish private work back into the main room
- private simulation requests that wait on the user and accept pasted results
- separate token budgets per model
- automatic summarization of older context
- strict pause mode that stops the whole room if any required model runs out
- manual top-up and resume controls

## Run

Fastest option for a non-programmer:

- open `multi_ai_platform/static/index.html` directly in a browser
- the prototype will run entirely in the browser with mocked participants

If you want the local Python server version instead, from the workspace root run:

```powershell
.\start_multi_ai_platform.ps1
```

Then open `http://127.0.0.1:8008`.

To try the simulation workflow:

- open a private box
- enter a request in `Simulation Flow`
- run that simulation outside the room however you want
- paste the result back into the same box
- optionally share the reviewed conclusion back to the room

## What It Demonstrates

The agents are mocked, so this is not calling real OpenAI, Anthropic, Google, or xAI APIs yet. The goal is to prove the product behavior:

- fan one user message out to several AI participants
- direct a message to one specific AI and give it first priority
- let AIs raise a hand, wait, or pass
- advance the room one speaker at a time
- switch between manual stepping and auto-play
- do side work in an AI-specific private box
- keep private work moving even if the public room is paused
- mark a private box as `waiting on user` when an AI needs an external simulation
- paste a simulation result back into the same private box for review
- publish a finished private result back into the shared room
- pause the room when the next speaker cannot afford a turn
- keep the state and transcript intact
- resume after adding budget
- summarize older messages so the context stays manageable

## Real API Upgrade Path

To turn this into a real platform later, replace the mock reply generator in `server.py` with provider adapters that:

- map the shared transcript into each provider's message format
- enforce per-provider rate limits and billing
- capture usage returned by each API
- write provider failures back into the same pause/resume flow
