# munch

A macro-aware eating assistant for people who eat out a lot.
You don't have to eat the same boring thing every day — munch
helps you eat what you actually want while keeping your goals
in check. Log whatever you're craving, and it'll tell you how
the rest of your day should look.

## How it works

**Log what you eat** — type a meal name and munch estimates the macros
using AI. Or pass exact numbers if you know them. Over time it learns
your frequent meals and surfaces them as quick picks.

**See where you stand** — check your day's progress, your week at a
glance, and which meals you reach for the most.

**Get real-time guidance** — heading to Cava with 700 cal left?
`munch plan` tells you what fits. Done with dinner and wondering
if you've got room for something sweet? `munch dessert` checks.
Have room for a snack but don't know what? `munch snack` picks
something based on fiber, protein, and what you've got left.

**The point is freedom, not restriction.** You log what you eat,
see the numbers, and decide from there. No guilt, no meal plans,
no "good" or "bad" foods — just awareness and a sister who's
got your back.

## Install

Requires Python 3.11+. Install with pip (or uv):

```bash
pip install munch
```

Or clone and install locally:

```bash
git clone https://github.com/your-username/munch && cd munch
pip install -e .
```

## Usage

### Profile

| Command | Description |
|---------|-------------|
| `munch init --cal 2000 --protein 150 --location "Atlanta"` | Set up your profile |
| `munch goal --cal 1800 --protein 140` | Update individual goals |

### Logging

| Command | Description |
|---------|-------------|
| `munch log "chipotle chicken bowl"` | Log with auto-estimated macros |
| `munch log "pad thai" --cal 850 --protein 32` | Log with exact macros |
| `munch log` | Interactive mode — shows your top meals by frequency; pick a number to log instantly, or type something new |

### Tracking

| Command | Description |
|---------|-------------|
| `munch status` | See today's progress |
| `munch history` | View the past 7 days grouped by date |
| `munch faves` | Shows which meals you reach for most, with their saved macros |
| `munch insights` | Analyzes your week — are you hitting protein? Any patterns worth knowing? Honest, friendly feedback |

### Guidance

| Command | Description |
|---------|-------------|
| `munch plan "Cava"` | Get ordering advice at a specific spot |
| `munch dessert` | Dessert check — see if you've got room |
| `munch snack` | Snack suggestion based on remaining macros |
| `munch rate "Cava" 9 --notes "great macros"` | Rate a spot and save notes |
