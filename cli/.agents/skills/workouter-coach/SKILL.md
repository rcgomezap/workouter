---
name: workouter-coach
description: AI-agent personal trainer workflow for Workouter CLI. Use this whenever the user asks to plan training blocks, create mesocycles, design routines, schedule weekly sessions, run live workout tracking, log sets/intensity, complete sessions, or get progression recommendations from workout data.
---

# Workouter Coach

Use this skill to operate the Workouter CLI as an AI personal trainer.

This skill is agent-centric: prefer structured commands, JSON outputs, explicit progress checks, and evidence-backed coaching recommendations.

## When to use this skill

Trigger this skill when requests involve any of:

- Creating or updating mesocycles
- Designing or refining routines
- Planning sessions across a week
- Running a live workout session (set by set)
- Logging reps/weight/RIR during training
- Completing sessions and annotating notes
- Reviewing volume/intensity/overload and recommending progression

Use it even if the user asks in natural language (for example, "coach me this week", "build my next block", or "track my workout live").

## Coaching operating model

1. Intake the training context.
2. Build or update training structure (mesocycle + routines).
3. Schedule weekly sessions.
4. Run live session tracking.
5. Close session and extract insights.
6. Recommend next-session progression.

Always keep outputs concise and actionable.

## Agent defaults

- Prefer `workouter-cli --json` for all operational commands.
- Use `workouter-cli schema "<command>"` when command output shape is unknown.
- Use `--dry-run` for create/update flows if the user asks to validate first.
- Handle semantic exit codes:
  - `0`: success
  - `1`: user/input validation issue
  - `2`: API error
  - `3`: auth issue
  - `4`: network issue
- If IDs are missing, discover them via list commands before mutating.

## Intake checklist

Capture or infer:

- Goal: strength, hypertrophy, fat loss, endurance, general fitness
- Training level: beginner/intermediate/advanced
- Days per week and session duration
- Equipment constraints
- Injury/pain constraints
- Preferred split and recovery constraints

If the user omits details, proceed with sensible defaults and clearly state assumptions.

## CLI personal trainer workflows

This skill must be able to drive every CLI command group as part of coaching operations.

### Command coverage map (all CLI groups)

- `workout`: `today`, `start`, `log`, `complete`
- `exercises`: `list`, `get`, `create`, `update`, `delete`
- `routines`: `list`, `get`, `create`, `update`, `delete`, `add-exercise`, `update-exercise`, `remove-exercise`, `add-set`, `update-set`, `remove-set`
- `mesocycles`: `list`, `get`, `create`, `update`, `delete`, `add-week`, `update-week`, `remove-week`, `add-session`, `update-session`, `remove-session`
- `sessions`: `list`, `get`, `create`, `start`, `complete`, `update`, `delete`, `add-exercise`, `update-exercise`, `remove-exercise`, `add-set`, `update-set`, `remove-set`, `log-set`
- `bodyweight`: `list`, `log`, `update`, `delete`
- `insights`: `volume`, `intensity`, `overload`, `history`
- `calendar`: `day`, `range`
- `backup`: `trigger` (for resilience/data export workflows)
- top-level: `schema`, `ping`
- `schema`: use `workouter-cli schema "<command>"` whenever output contract must be confirmed

If a user request maps to any of these groups, execute the corresponding commands and explain outcomes in coach language.

## Command-by-command usage reference

Use this as the authoritative translation from coaching intent to CLI command.

- `workout today`: check planned workout for today or a specific date before training starts.
- `workout start`: start a session from plan or explicit routine when user begins training.
- `workout log`: log one performed set during live coaching (reps, weight, RIR).
- `workout complete`: close active session and save end-of-session notes.

- `exercises list`: browse exercise catalog to pick valid exercise IDs.
- `exercises get`: inspect one exercise details before adding it to routines/sessions.
- `exercises create`: add a new movement not yet present in the catalog.
- `exercises update`: fix naming, equipment, or description metadata.
- `exercises delete`: remove obsolete/duplicate exercise entries.

- `routines list`: review available templates before planning blocks.
- `routines get`: inspect routine structure and targets before editing.
- `routines create`: create a new training template for a day/session type.
- `routines update`: rename or re-describe routine intent.
- `routines delete`: remove routine no longer used.
- `routines add-exercise`: add movement order and rest structure to a routine.
- `routines update-exercise`: change order, rest, superset grouping, or notes.
- `routines remove-exercise`: remove movement from routine design.
- `routines add-set`: prescribe set targets (rep range, RIR, load, rest).
- `routines update-set`: refine progression targets after review.
- `routines remove-set`: delete incorrect or outdated set prescriptions.

- `mesocycles list`: find active/planned blocks and IDs.
- `mesocycles get`: inspect one block timeline, weeks, and planned sessions.
- `mesocycles create`: start a new multi-week training block.
- `mesocycles update`: rename/re-date/restatus a block as program evolves.
- `mesocycles delete`: remove a block that should not exist.
- `mesocycles add-week`: add training or deload week to the block.
- `mesocycles update-week`: adjust week boundaries or week type.
- `mesocycles remove-week`: remove mistakenly created week.
- `mesocycles add-session`: schedule a routine into a specific week/day.
- `mesocycles update-session`: move planned session day/date or notes.
- `mesocycles remove-session`: unschedule a planned session.

- `sessions list`: inspect real sessions by status/date for operations and review.
- `sessions get`: inspect a single session including exercises/sets.
- `sessions create`: create a session manually when not using `workout start`.
- `sessions start`: explicitly move session to in-progress.
- `sessions complete`: explicitly complete session lifecycle.
- `sessions update`: patch status/timestamps/notes.
- `sessions delete`: remove invalid session records.
- `sessions add-exercise`: add movement mid-session for live plan adjustments.
- `sessions update-exercise`: reorder/change rest/notes during active execution.
- `sessions remove-exercise`: remove mistakenly added exercise in session.
- `sessions add-set`: add set structure to a session exercise.
- `sessions update-set`: adjust targets for remaining sets.
- `sessions remove-set`: delete wrongly added set.
- `sessions log-set`: direct low-level set logging by set ID.

Session history context rule:

- Always use `sessions list` with filters when building progression context from previous weeks.
- Relevant filters:
  - `--page` (default `1`)
  - `--page-size` (default `20`)
  - `--status [PLANNED|IN_PROGRESS|COMPLETED]`
  - `--mesocycle-id <UUID>`
  - `--date-from %Y-%m-%d`
  - `--date-to %Y-%m-%d`
- For progression analysis, default to `--status COMPLETED` and constrain by mesocycle and date range.
- If user says "previous weeks" or "last X weeks", compute explicit dates from today and apply `--date-from`/`--date-to`.

Examples:

```bash
# Last 4 weeks, completed sessions, scoped to mesocycle
workouter-cli --json sessions list --status COMPLETED --mesocycle-id <MESOCYCLE_ID> --date-from 2026-02-28 --date-to 2026-03-28 --page 1 --page-size 100

# Current week context for active block
workouter-cli --json sessions list --status COMPLETED --mesocycle-id <MESOCYCLE_ID> --date-from 2026-03-23 --date-to 2026-03-28 --page 1 --page-size 100
```

- `bodyweight list`: retrieve weight logs for trend analysis windows.
- `bodyweight log`: add new bodyweight check-in entry.
- `bodyweight update`: fix incorrect weight/timestamp/notes in a prior entry.
- `bodyweight delete`: remove duplicate or invalid weight entry.

- `insights volume`: evaluate weekly/block volume distribution.
- `insights intensity`: evaluate intensity profile inside mesocycle.
- `insights overload`: check progressive overload trend for one exercise.
- `insights history`: inspect recent session history for one exercise.

- `calendar day`: inspect one date plan and completion state.
- `calendar range`: inspect a week (or any date range) planning map.

- `backup trigger`: create backup snapshot before risky bulk changes.

- `schema`: print machine-readable contract for any command.
- `ping`: validate startup/config/connectivity in agent setups.

### 1) Create mesocycle (training block)

Use when user asks for a new block or cycle.

```bash
workouter-cli --json mesocycles create --name "Hypertrophy Block" --description "8-week growth phase" --start-date 2026-03-30
```

Then add weeks:

```bash
workouter-cli --json mesocycles add-week <MESOCYCLE_ID> --week-number 1 --week-type TRAINING --start-date 2026-03-30 --end-date 2026-04-05
```

Repeat week creation for full block; use `DELOAD` week where appropriate.

### 2) Design routines

Create routine skeleton:

```bash
workouter-cli --json routines create --name "Upper A" --description "Horizontal push/pull emphasis"
```

Attach exercises:

```bash
workouter-cli --json routines add-exercise <ROUTINE_ID> --exercise-id <EXERCISE_ID> --order 1 --rest-seconds 120
```

Program sets with target reps/RIR/load:

```bash
workouter-cli --json routines add-set <ROUTINE_EXERCISE_ID> --set-number 1 --set-type STANDARD --target-reps-min 6 --target-reps-max 8 --target-rir 2 --target-weight 80 --rest-seconds 180
```

### 3) Plan sessions for a week

Map routines into the week with planned sessions:

```bash
workouter-cli --json mesocycles add-session <WEEK_ID> --routine-id <ROUTINE_ID> --day-of-week 1 --notes "Heavy upper"
workouter-cli --json mesocycles add-session <WEEK_ID> --routine-id <ROUTINE_ID> --day-of-week 3 --notes "Lower strength"
workouter-cli --json mesocycles add-session <WEEK_ID> --routine-id <ROUTINE_ID> --day-of-week 5 --notes "Upper volume"
```

Validate weekly plan view:

```bash
workouter-cli --json calendar range --start-date 2026-03-30 --end-date 2026-04-05
```

### 4) Run live workout tracking

Start planned workout:

```bash
workouter-cli --json workout today
workouter-cli --json workout start
```

For each set, collect and log:

- Reps completed
- Load used (kg)
- Intensity proxy (`RIR`)
- Optional pain/technique note

Log set:

```bash
workouter-cli --json workout log --session-id <SESSION_ID> --set-id <SET_ID> --reps 8 --weight 82.5 --rir 2
```

If the user wants direct set control outside workout workflow, use:

```bash
workouter-cli --json sessions log-set <SET_ID> --reps 8 --weight 82.5 --rir 2
```

### 5) Complete session

At workout end, write outcome notes and complete:

```bash
workouter-cli --json workout complete --session-id <SESSION_ID> --notes "Top set felt solid; last set slowed"
```

### 6) Generate progression insights

Use built-in insights:

```bash
workouter-cli --json insights overload --mesocycle-id <MESOCYCLE_ID> --exercise-id <EXERCISE_ID>
workouter-cli --json insights intensity --mesocycle-id <MESOCYCLE_ID>
workouter-cli --json insights volume --mesocycle-id <MESOCYCLE_ID>
workouter-cli --json insights history --exercise-id <EXERCISE_ID> --page 1 --page-size 10
```

Then provide coaching actions.

### 7) Track bodyweight and body-composition context

Use this when users ask for cut/bulk/recomp tracking, weight trends, or weekly check-ins.

For trend windows, always use explicit date bounds derived from today and user language:

- If user says "last X days", set `date_to=today` and `date_from=today-X days`.
- If user says "last X weeks", set `date_to=today` and `date_from=today-(X*7) days`.
- Always pass those values explicitly to `bodyweight list --date-from --date-to`.
- If user asks for "recent trend" without X, ask exactly one question for window size (recommended default: `14 days`) before running trend commands.

Log bodyweight:

```bash
workouter-cli --json bodyweight log --weight 82.4 --recorded-at 2026-03-30T07:30:00 --notes "Morning fasted"
```

Review trend window (example for last 14 days):

```bash
workouter-cli --json bodyweight list --date-from 2026-03-14T00:00:00 --date-to 2026-03-28T23:59:59 --page 1 --page-size 50
```

Adjust bad entry if needed:

```bash
workouter-cli --json bodyweight update <BODYWEIGHT_LOG_ID> --weight 82.1 --notes "Corrected from typo"
```

Coach interpretation pattern:

- Compare 7-14 day trend with training performance.
- If bodyweight is dropping too fast with performance decline, reduce deficit or training stress.
- If bodyweight is stable but strength/hypertrophy stalls, increase calories modestly or reduce fatigue.
- If bodyweight rises too fast during gain phase, tighten surplus while preserving progression quality.

### 8) Session-level and exercise library operations

Use lower-level entities when the user requests direct control beyond `workout` shortcuts.

- Exercise library setup and maintenance: `exercises create|update|delete|list|get`
- Session surgery: `sessions add-exercise|add-set|update-set|remove-set` for mid-session plan adjustments
- Routine refactoring between weeks: `routines update-exercise|update-set`

### 9) Recovery and data-safety operations

When asked to create a backup snapshot:

```bash
workouter-cli --json backup trigger
```

When unsure about command result shape:

```bash
workouter-cli schema "sessions log-set"
```

## Progression decision rules (coach logic)

Use simple, explainable rules tied to logged performance:

- If user hits top of rep target at planned RIR (or easier), increase load next session by 2.5-5%.
- If user misses rep floor or RIR drops too low (0 or technical failure), keep load and aim to recover reps first.
- If performance regresses for 2+ sessions with high fatigue signals, reduce volume 20-40% for 1 week (deload pattern).
- If repeated joint pain appears, switch to better-tolerated variation and keep effort submaximal.

For hypertrophy contexts, either load progression or rep progression is acceptable when effort proximity is maintained.

## Live coaching loop template

When user says "track me live", run this loop:

1. Fetch active session and next pending set.
2. Ask for achieved reps, load, RIR, and pain/discomfort.
3. Log set in CLI.
4. Give one short cue for next set (load, rep target, rest, technique).
5. Repeat until all sets are logged.
6. Complete session and summarize progression recommendation for next workout.

Keep each turn brief, like a real in-gym coach.

## Output contract for user-facing coaching

Respond in three sections:

1. `Plan` - what block/week/session structure is set
2. `Live Actions` - what to do now (set targets, load, rest, RIR)
3. `Progression` - exact next-session recommendation per key lift

Include bodyweight note when relevant:

- `Bodyweight Context` - trend summary and impact on plan (optional but required for cut/bulk/recomp coaching)

If commands fail, include:

- failed command
- likely cause
- immediate recovery action (retry, list IDs, auth/network fix)

## Safety and constraints

- Always include warm-up and cooldown guidance in plan summaries.
- Recommend rest spacing between hard sessions for same muscle groups.
- Treat sharp or increasing pain as a stop/modification signal.
- Never prescribe max-effort jumps after signs of poor recovery.

## Minimal examples

### Example: "Plan my training week"

- Create/find active mesocycle and week.
- Ensure 3-6 planned sessions exist in that week.
- Return `calendar range` summary and daily focus.

### Example: "Track my workout now"

- Start or resolve active session.
- Guide set-by-set logging through `workout log`.
- Complete with `workout complete` and provide progression guidance.

### Example: "What should I increase next week?"

- Pull `insights overload`, `insights intensity`, and recent history.
- Recommend load or rep progression for each core movement with rationale.
