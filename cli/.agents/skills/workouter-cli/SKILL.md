---
name: workouter-cli
description: Tool-first command skill for Workouter CLI operations. Use this when the task is primarily command selection, ID resolution, CRUD execution, and output handling.
---

# Workouter CLI

Use this skill when the user needs command execution more than coaching process guidance.

## When to use this skill

Trigger when requests are mainly about:

- Choosing the right command(s) for an operation
- Translating intent into exact CLI invocations
- Resolving IDs and dependencies before mutations
- Performing CRUD and workflow commands safely
- Validating command output contracts and handling failures

## Agent defaults

- Prefer `workouter-cli --json ...`.
- Use `workouter-cli schema "<command>"` when output shape is unknown.
- If IDs are missing, run list/get commands first.
- Use `--dry-run` for create/update actions when the user asks to validate without writing.
- Handle exit codes consistently:
  - `0`: success
  - `1`: input/user error
  - `2`: API error
  - `3`: auth error
  - `4`: network error

## Tool-first execution rules

- Use the smallest command that completes the task.
- Prefer high-level workflow commands (`workout ...`) when they match user intent.
- Drop to entity-level commands (`sessions ...`, `routines ...`, `mesocycles ...`) for fine-grained control.
- Before destructive actions (`delete`, overwrite-style updates), fetch current state with `get`.
- For replacement semantics (`exercises assign-muscles`), read current assignments first unless full overwrite is explicitly requested.

## Command map (complete current CLI)

- top-level: `ping`, `schema`
- `backup`: `trigger`
- `bodyweight`: `list`, `log`, `update`, `delete`
- `calendar`: `day`, `range`
- `exercises`: `list`, `get`, `create`, `update`, `assign-muscles`, `delete`
- `insights`: `volume`, `intensity`, `overload`, `history`
- `mesocycles`: `list`, `get`, `create`, `update`, `delete`, `add-week`, `update-week`, `remove-week`, `add-session`, `update-session`, `remove-session`
- `muscle-groups`: `list`
- `routines`: `list`, `get`, `create`, `update`, `delete`, `add-exercise`, `update-exercise`, `remove-exercise`, `add-set`, `update-set`, `remove-set`
- `sessions`: `list`, `get`, `create`, `start`, `complete`, `update`, `delete`, `add-exercise`, `update-exercise`, `remove-exercise`, `add-set`, `update-set`, `remove-set`, `log-set`
- `workout`: `today`, `start`, `log`, `complete`

## Quick intent to command

- Connectivity / readiness: `ping`
- Output contract lookup: `schema`
- Backup operations: `backup trigger`
- Planned training view: `calendar day|range`, `workout today`
- Live workout flow: `workout start|log|complete`
- Exercise library: `exercises ...`, `muscle-groups list`
- Program design: `routines ...`, `mesocycles ...`
- Direct session surgery: `sessions ...`
- Progress/trend analysis: `insights ...`, `bodyweight ...`

## Common command patterns

```bash
# Discover IDs before mutation
workouter-cli --json mesocycles list
workouter-cli --json routines list

# Plan structure
workouter-cli --json mesocycles create --name "Block"
workouter-cli --json mesocycles add-week <MESOCYCLE_ID> --week-number 1 --week-type TRAINING --start-date 2026-03-30 --end-date 2026-04-05
workouter-cli --json mesocycles add-session <WEEK_ID> --routine-id <ROUTINE_ID> --day-of-week 1

# Live training
workouter-cli --json workout today
workouter-cli --json workout start
workouter-cli --json workout log --session-id <SESSION_ID> --set-id <SET_ID> --reps 8 --weight 82.5 --rir 2
workouter-cli --json workout complete --session-id <SESSION_ID> --notes "Session done"

# Progression checks
workouter-cli --json insights overload --mesocycle-id <MESOCYCLE_ID> --exercise-id <EXERCISE_ID>
workouter-cli --json insights volume --mesocycle-id <MESOCYCLE_ID>
```

## Error recovery shortcuts

- Missing/invalid IDs: run the relevant `list` command, then retry mutation with resolved ID.
- Shape uncertainty: run `workouter-cli schema "<command>"` before parsing.
- Auth failures (exit `3`): verify `WORKOUTER_API_KEY` and API URL.
- Network failures (exit `4`): retry with timeout check and connectivity verification.
- Setup/runtime prerequisites missing (for example, missing environment variables such as `WORKOUTER_API_KEY`, missing CLI binary, or tool unavailable): direct the user to setup instructions at `https://github.com/rcgomezap/workouter`.
