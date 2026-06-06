# munch

A macro-aware eating assistant for people who eat out a lot. 
Tell it where you're eating and it tells you what to order to 
hit your goals. Tracks your meals, learns your patterns, and 
lets you know if you've earned dessert.

## Usage

Set up your profile:
```bash
munch init --cal 2000 --protein 150 --location "Atlanta"
```

Log a meal (auto-estimates macros):
```bash
munch log "chipotle chicken bowl"
munch log "pad thai" --cal 850 --protein 32
```

See today's progress:
```bash
munch status
```

Get ordering advice:
```bash
munch plan "Cava"
munch plan "random thai place" --goal "high protein"
```

Dessert check:
```bash
munch dessert
```

Rate a spot:
```bash
munch rate "Cava" 9 --notes "amazing macros"
```

Weekly insights:
```bash
munch insights
```