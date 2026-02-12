# Agent Handoff Protocol

> How ACCU agents coordinate without stepping on each other.

## Core Principle

**Agents don't talk to each other directly.**
All communication happens through `/state/` files.

```
Agent A → writes to /state/ → Agent B reads from /state/
```

This ensures:
- No context is lost between sessions
- Any agent can pick up where another left off
- Human can always see what's happening
- Decisions are documented

---

## The Handoff Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                         HUMAN                                │
│                    (Ultimate authority)                      │
└─────────────────────────────┬───────────────────────────────┘
                              │ Sets priorities
                              │ Makes irreversible decisions
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CONDUCTOR                              │
│         Reads priorities → Creates tasks → Assigns           │
└──────────┬─────────────────────────────────────┬────────────┘
           │                                     │
           ▼                                     ▼
┌─────────────────────┐                ┌─────────────────────┐
│       SCOUT         │                │       BUILDER       │
│  Discovers repos    │                │   Writes code       │
│  Writes reports     │                │   Deploys           │
└─────────┬───────────┘                └──────────┬──────────┘
          │                                       │
          │ findings                              │ code
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        CRITIC                                │
│            Reviews code │ Analyzes candidates                │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CHRONICLER                              │
│            Documents everything │ Maintains memory           │
└─────────────────────────────────────────────────────────────┘
```

---

## Handoff File: `/state/active-tasks.md`

This is the central coordination point.

### Task Assignment Format

```markdown
## Handoff Queue

### [TASK-001] For: Builder
**From:** Conductor
**Priority:** P0
**Description:** Release yapsy 1.13.0 from fork
**Context:** PR #26 has no response after 5 days
**Acceptance Criteria:**
- [ ] Version bumped to 1.13.0
- [ ] CHANGELOG updated
- [ ] Published to PyPI
**Blocked By:** Need PyPI credentials from Human
```

### Picking Up a Task

When an agent picks up a task:

```markdown
## Builder
- Status: working
- Current Task: [TASK-001] Release yapsy 1.13.0
- Started: 2026-02-12 14:30 UTC
- Notes: Waiting for PyPI credentials
```

### Completing a Task

```markdown
## Completed Today

- [TASK-001] Builder: Released yapsy 1.13.0
  - Published to PyPI: https://pypi.org/project/yapsy/1.13.0
  - Took 45 minutes
  - No issues
```

---

## Cross-Agent Requests

### Scout → Critic (Request Analysis)

Scout adds to Handoff Queue:
```markdown
### [TASK-002] For: Critic
**From:** Scout
**Priority:** P1
**Description:** Deep technical analysis of CaseRecommender
**Context:** Discovery found this with score 0.59, highest in batch
**Link:** https://github.com/caserec/CaseRecommender
**Output:** /docs/candidates/003_caserecommender_technical_analysis.md
```

### Builder → Critic (Request Review)

Builder adds to Handoff Queue:
```markdown
### [TASK-003] For: Critic
**From:** Builder
**Priority:** P1
**Description:** Review Discovery Agent README fix
**Context:** Added readme fetching to _process_repository
**Files Changed:** src/accu/agents/discovery/agent.py
**Commit:** 7569428
```

### Critic → Builder (Review Complete)

Critic adds to Handoff Queue:
```markdown
### [TASK-004] For: Builder
**From:** Critic
**Priority:** P2
**Description:** Address review feedback
**Context:** Review of commit 7569428
**Feedback:**
- MUST FIX: Add error handling for failed README fetch
- SHOULD FIX: Add timeout parameter
**Original Task:** [TASK-003]
```

---

## Escalation Protocol

### To Conductor
Any agent can escalate by adding:
```markdown
## Escalation Queue

### [ESC-001] From: Builder
**Issue:** Unclear whether to wait for PR or release from fork
**Options:**
1. Wait 2 more days
2. Release from fork now
3. Contact maintainer directly
**Needs Decision By:** 2026-02-13
```

### To Human
Only Conductor escalates to Human:
```markdown
## Human Required

### [HUMAN-001] From: Conductor
**Issue:** Need PyPI credentials for yapsy release
**Urgency:** Blocking P0 task
**Action Needed:** Provide or create PyPI API token
```

---

## State File Locking

**There is no locking.** Agents must:

1. **Read before write** — always check current state
2. **Append, don't overwrite** — add to lists, don't replace
3. **Use clear section headers** — so merges are possible
4. **Timestamp changes** — so conflicts can be resolved

If two agents write conflicting info:
- Conductor resolves
- Most recent timestamp wins for status
- Both items preserved for history

---

## Session Boundaries

### Starting a Session
```
1. Pull latest code (git pull)
2. Read ALL /state/*.md files
3. Read your profile (.claude/profiles/your-role.md)
4. Check Handoff Queue for your tasks
5. Update your status in active-tasks.md
```

### Ending a Session
```
1. Update your status to "idle"
2. Move completed tasks to "Completed Today"
3. Add any new tasks to Handoff Queue
4. Commit state changes (git commit -m "state: [agent] session update")
5. Push (git push)
```

---

## Emergency Protocol

If something is broken and blocking all work:

1. **Builder** tries to fix if it's code
2. **Builder** rolls back if fix isn't quick
3. **Conductor** is notified via Escalation Queue
4. **Human** is contacted if system is down >1 hour

---

## Anti-Patterns

### DON'T: Chain long conversations
```
BAD: Scout asks Critic who asks Builder who asks Conductor
GOOD: Scout writes task → Critic picks up → writes result → done
```

### DON'T: Assume another agent remembers
```
BAD: "As we discussed..."
GOOD: "See [TASK-001] and decision log entry 2026-02-12"
```

### DON'T: Work without updating state
```
BAD: Do work, forget to log it
GOOD: Update active-tasks.md BEFORE starting, AFTER finishing
```

### DON'T: Make decisions outside your role
```
BAD: Builder decides to add a new feature while fixing a bug
GOOD: Builder finishes bug fix, suggests feature in Handoff Queue for Conductor
```

---

## Quick Reference

| Action | File | Who |
|--------|------|-----|
| Assign task | /state/active-tasks.md | Conductor |
| Report finding | /docs/candidates/*.md | Scout |
| Request review | /state/active-tasks.md | Builder |
| Log decision | /state/decisions.md | Any (esp. Conductor) |
| Update priorities | /state/priorities.md | Conductor only |
| Archive old items | /docs/archive/ | Chronicler |
