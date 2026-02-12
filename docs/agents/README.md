# ACCU Multi-Agent System

> A team of specialized AI agents working together to build and maintain ACCU.

## Why Multi-Agent?

One agent doing everything leads to:
- Context loss as conversations grow
- Priority drift and scope creep
- No separation of concerns
- No checks and balances

Multiple specialized agents provide:
- Clear responsibilities
- Persistent memory through files
- Parallel work capability
- Built-in review process

---

## The Team

| Agent | Model | Role | Cost |
|-------|-------|------|------|
| **Conductor** | Opus | Strategy, priorities, decisions | $$$ (rare) |
| **Builder** | Sonnet | Code, deploy, ship | $$ |
| **Scout** | Haiku | Discovery, monitoring | $ |
| **Critic** | Sonnet | Review, analysis | $$ |
| **Chronicler** | Haiku | Documentation, memory | $ |

---

## How They Work Together

```
Human sets direction
       ↓
Conductor creates tasks → /state/active-tasks.md
       ↓
Agents pick up tasks based on role
       ↓
Work is done, results written to /state/ or /docs/
       ↓
Chronicler documents everything
       ↓
Loop continues
```

---

## Key Files

### State (Live Coordination)
- `/state/priorities.md` — What matters now
- `/state/active-tasks.md` — Who's doing what
- `/state/decisions.md` — Why we did what we did

### Profiles (Agent Identity)
- `/.claude/profiles/conductor.md`
- `/.claude/profiles/builder.md`
- `/.claude/profiles/scout.md`
- `/.claude/profiles/critic.md`
- `/.claude/profiles/chronicler.md`

### Protocol
- `/docs/agents/handoff-protocol.md` — How agents coordinate

---

## Running Agents

### On VPS with tmux
```bash
# Create sessions for each agent
tmux new-session -d -s conductor
tmux new-session -d -s builder
tmux new-session -d -s scout
tmux new-session -d -s critic
tmux new-session -d -s chronicler

# Start an agent (example: builder)
tmux send-keys -t builder 'cd ~/accu && claude --profile builder' Enter

# Attach to see what's happening
tmux attach -t builder
```

### Locally for Testing
```bash
cd /path/to/accu
claude --profile conductor
```

---

## Cost Management

Agents use different models based on task complexity:

| Model | Input $/1M | Output $/1M | Use For |
|-------|-----------|-------------|---------|
| Haiku | $0.25 | $1.25 | High-volume, simple tasks |
| Sonnet | $3.00 | $15.00 | Coding, analysis |
| Opus | $15.00 | $75.00 | Critical decisions only |

**Budget Guidelines:**
- Scout + Chronicler (Haiku): Run frequently
- Builder + Critic (Sonnet): Run for specific tasks
- Conductor (Opus): Run once per day max, or for major decisions

---

## Principles

### 1. Files Are Memory
Agents have no memory between sessions.
Everything important must be written to files.

### 2. Roles Are Boundaries
Each agent has clear DO and DON'T lists.
Stepping outside your role = asking Conductor first.

### 3. Humans Decide, Agents Execute
AI augments judgment; it doesn't replace responsibility.
Irreversible actions require Human approval.

### 4. Transparency Over Efficiency
Log everything. Future agents need to understand WHY.
A well-documented slow decision > undocumented fast decision.

### 5. Simple Over Clever
Straightforward solutions that anyone can understand.
Future contributors (human or AI) will thank you.

---

## Adding a New Agent

1. Create profile: `/.claude/profiles/new-agent.md`
2. Define: Identity, Model, Responsibilities, Boundaries, Workflow
3. Update this README
4. Update handoff-protocol.md if new interactions needed
5. Test locally before deploying to VPS

---

## Troubleshooting

### Agent stuck in "working" status
- Check if session crashed
- Manually update status to "idle"
- Check for uncommitted work

### Conflicting state files
- Most recent timestamp wins
- Conductor resolves ambiguity
- Chronicler cleans up

### Agent doing wrong task
- Check if reading correct profile
- Verify /state/active-tasks.md is current
- Re-pull from git

---

## Evolution

This system will evolve. When changing it:

1. Discuss with Conductor first
2. Document the change and WHY
3. Update affected profiles
4. Test before deploying
5. Chronicler records the evolution

Remember: We're building the system that builds ACCU.
Meta-stability matters.
