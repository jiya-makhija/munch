# munch

A macro-aware eating assistant for people who eat out a lot.
Set your daily goals, log meals, and get warm, personalized
advice on what to order, whether you've earned dessert, and
what snack fits your remaining macros. Tracks your patterns,
remembers your frequent meals, and keeps you on track without
the guilt trip.

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

Weekly AI insights:
```bash
munch insights
```