# Workouter CLI

A command-line interface for the Workouter API - track your workouts from the terminal.

## Features

- 🤖 **AI-Agent Optimized**: JSON output, semantic exit codes, stateless operation
- 🎯 **Hybrid Commands**: Quick workflows + full GraphQL access
- 📊 **Rich Output**: Beautiful tables for humans, clean JSON for agents
- 🔒 **Secure**: API key authentication, no local storage
- ⚡ **Fast**: Built with async Python and efficient GraphQL queries
- 🧪 **Well-Tested**: 85%+ coverage with comprehensive test suite

## Quick Start

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set environment variables
export WORKOUTER_API_URL=http://localhost:8000/graphql
export WORKOUTER_API_KEY=your-api-key-here

# Run the CLI
uv run workouter-cli --help
```

### Self-contained Binary

You can build a single-file executable that doesn't require Python:

```bash
# Build for your current OS
make binary

# Use the binary
./dist/workouter-cli --help
```

For Linux distribution, the release pipeline publishes an AppImage artifact (`workouter-cli-linux-x86_64.AppImage`):

```bash
chmod +x workouter-cli-linux-x86_64.AppImage
./workouter-cli-linux-x86_64.AppImage --help
```

### Basic Usage

```bash
# View today's workout
workouter-cli workout today

# Start a workout
workouter-cli workout start

# List exercises
workouter-cli exercises list

# Get exercise details
workouter-cli exercises get <uuid>

# Create a new exercise
workouter-cli exercises create --name "Bench Press" --equipment "Barbell"
```

### For AI Agents

```bash
# All commands support JSON output
workouter-cli --json exercises list

# Get schema/example for any command
workouter-cli schema "exercises list"

# Semantic exit codes (0=success, 1=user error, 2=API error, 3=auth, 4=network)
workouter-cli --json exercises get <uuid> || echo "Exit code: $?"
```

## Command Groups

- **workout**: High-level workflows (start, log, complete, today)
- **exercises**: Manage exercises (list, create, update, delete)
- **routines**: Manage workout routines
- **mesocycles**: Manage training mesocycles
- **sessions**: Manage workout sessions
- **bodyweight**: Log and track bodyweight
- **insights**: View training insights (volume, intensity, progressive overload)
- **calendar**: View workout calendar
- **backup**: Trigger API backups

## Documentation

- **[DESIGN.md](./DESIGN.md)**: Comprehensive system design and architecture
- **[AGENTS.md](./AGENTS.md)**: Setup, commands, and workflows for AI coding agents
- **Agent Skill**: `cli/.agents/skills/workouter-coach/SKILL.md` for AI personal trainer workflows (planning, live tracking, bodyweight, progression, full command coverage)
- **[API Schema](../api/schema.graphql)**: GraphQL schema reference

## Development

```bash
# Run tests
make test

# Run linter
make lint

# Format code
make format

# Type check
make type-check

# See all commands
make help
```

## Requirements

- Python 3.14+
- Workouter API running and accessible
- API key from the Workouter API

## License

[Your License Here]

## Contributing

See [AGENTS.md](./AGENTS.md) for development setup and PR guidelines.
