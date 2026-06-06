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

Set up your profile:
```bash
munch init --cal 2000 --protein 150 --location "Atlanta"
```

Update individual goals without resetting:
```bash
munch goal --cal 1800 --protein 140
```

Log a meal with auto-estimated macros:
```bash
munch log "chipotle chicken bowl"
munch log "pad thai" --cal 850 --protein 32
```

Log interactively using your frequent meals:
```bash
munch log
```
Shows your top meals by frequency — pick a number to log instantly, or type something new.

See today's progress:
```bash
munch status
```

View the past 7 days grouped by date:
```bash
munch history
```

Get ordering advice:
```bash
munch plan "Cava"
```

Dessert check:
```bash
munch dessert
```

Snack suggestion based on remaining macros:
```bash
munch snack
```

Rate a spot:
```bash
munch rate "Cava" 9 --notes "great macros"
```

List your most-logged meals:
```bash
munch faves
```
See which meals you reach for most, with their saved macros.

Weekly AI insights:
```bash
munch insights
```
Analyzes your week — are you hitting protein? Any patterns worth knowing? Honest, friendly feedback on how the week looked.
