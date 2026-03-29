---
name: workouter-coach
description: General coaching workflow skill for Workouter CLI. Use this for planning and training guidance, then call CLI commands as needed.
---

# Workouter Coach

Use this skill for higher-level coaching requests where the user wants planning help, weekly structure, live guidance, or progression recommendations.

## When to use this skill

Trigger for requests like:

- "Plan my next block"
- "Build my weekly routine"
- "Track my workout live"
- "What should I progress next week?"

## Planning order (required)

When planning routines and weekly training, follow this order:

1. Create a mesocycle first.
2. Create routines, or add/update existing routines if the user asks to reuse existing ones.
3. Plan weeks in the mesocycle.
4. Plan sessions inside those weeks using the routines.

Do not schedule sessions before the mesocycle and routine structure exists.

## Default execution style

- Prefer `workouter-cli --json ...`.
- Resolve missing IDs with list commands before mutations.
- Use `schema` when output format is uncertain.
- Keep coaching replies concise: what is planned now, what to do today, and what changes next.

## Core command flows

```bash
# 1) Mesocycle first
workouter-cli --json mesocycles create --name "Block"

# 2) Routines next (create or reuse existing)
workouter-cli --json routines list
workouter-cli --json routines create --name "Upper A"

# 3) Plan weeks
workouter-cli --json mesocycles add-week <MESOCYCLE_ID> --week-number 1 --week-type TRAINING --start-date 2026-03-30 --end-date 2026-04-05

# 4) Plan sessions inside weeks
workouter-cli --json mesocycles add-session <WEEK_ID> --routine-id <ROUTINE_ID> --day-of-week 1

# Live tracking and completion
workouter-cli --json workout start
workouter-cli --json workout log --session-id <SESSION_ID> --set-id <SET_ID> --reps 8 --weight 80 --rir 2
workouter-cli --json workout complete --session-id <SESSION_ID> --notes "Good session"

# Progression review
workouter-cli --json insights overload --mesocycle-id <MESOCYCLE_ID> --exercise-id <EXERCISE_ID>
```

## Coaching guardrails

- If recovery or pain flags appear, reduce stress before increasing load.
- If reps and RIR targets are consistently exceeded, progress load or reps next session.
- Keep recommendations simple and tied to recent logged data.
