import click
from datetime import datetime
from . import db
from . import ai


@click.group()
def cli():
    pass


@cli.command()
@click.option("--cal", type=int, required=True, help="Daily calorie goal")
@click.option("--protein", type=int, required=True, help="Daily protein goal (g)")
@click.option("--location", type=str, required=True, help="Your city/location")
def init(cal: int, protein: int, location: str):
    """Set up your profile and daily macro goals."""
    db.init_db()
    db.save_profile(cal, protein, location)
    click.echo(f"Profile saved: {cal} cal, {protein}g protein, {location}")


@cli.command()
@click.option("--cal", type=int, default=None, help="New daily calorie goal")
@click.option("--protein", type=int, default=None, help="New daily protein goal (g)")
@click.option("--location", default=None, help="New location")
def goal(cal: int | None, protein: int | None, location: str | None):
    """Update individual goals without resetting everything."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return
    db.update_profile(calories=cal, protein=protein, location=location)
    updated = db.get_profile()
    click.echo(f"Goals updated: {updated['daily_calories']} cal, {updated['daily_protein']}g protein, {updated['location']}")


@cli.command()
@click.argument("meal", required=False)
@click.option("--cal", type=int, default=None, help="Calories (skips AI guess)")
@click.option("--protein", type=int, default=None, help="Protein in grams (skips AI guess)")
def log(meal: str | None, cal: int | None, protein: int | None):
    """Log a meal. Macros auto-estimated via AI if not provided.
    Run with no arguments for interactive favorite selection."""

    if meal is None:
        faves = db.get_frequent_meals(5)
        if not faves:
            click.echo("No frequent meals yet. Run `munch log \"meal name\"` to start.")
            return
        click.echo("Your frequent meals:")
        for i, m in enumerate(faves, 1):
            click.echo(f"  [{i}] {m['name']} — {m['calories']} cal, {m['protein']}g protein")
        click.echo("  Or type a new meal:")
        choice = click.prompt("", default="")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(faves):
                m = faves[idx]
                db.init_db()
                db.log_meal(m["name"], m["calories"], m["protein"])
                click.echo(f"Logged: {m['name']} — {m['calories']} cal, {m['protein']}g protein")
                return
            else:
                click.echo("Invalid choice.")
                return
        meal = choice.strip()
        if not meal:
            return

    if cal is not None and protein is not None:
        db.init_db()
        db.log_meal(meal, cal, protein)
        click.echo(f"Logged: {meal} — {cal} cal, {protein}g protein")
        return

    saved = db.find_meal_by_name(meal)
    if saved:
        cal, protein = saved["calories"], saved["protein"]
        click.echo(f"Found saved macros for \"{meal}\": {cal} cal, {protein}g protein")
    else:
        click.echo(f"Estimating macros for \"{meal}\"...")
        cal, protein = ai.estimate_macros(meal)

    db.init_db()
    db.log_meal(meal, cal, protein)
    click.echo(f"Logged: {meal} — {cal} cal, {protein}g protein")


@cli.command()
def faves():
    """Show your top 5 most logged meals."""
    meals = db.get_frequent_meals(5)
    if not meals:
        click.echo("No meals logged yet. Start logging to build favorites!")
        return
    click.echo("Your top meals:")
    for i, m in enumerate(meals, 1):
        click.echo(f"  {i}. {m['name']} — {m['calories']} cal, {m['protein']}g protein (logged {m['cnt']}x)")


@cli.command()
def status():
    """Show today's logged meals and progress toward goals."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return
    meals = db.get_today_meals()
    total_cal = sum(m["calories"] for m in meals)
    total_protein = sum(m["protein"] for m in meals)
    goal_cal = profile["daily_calories"]
    goal_protein = profile["daily_protein"]

    cal_left = goal_cal - total_cal
    protein_left = goal_protein - total_protein

    click.echo(f"Goals: {goal_cal} cal, {goal_protein}g protein")
    click.echo(f"Logged: {total_cal} cal, {total_protein}g protein")
    click.echo(f"Remaining: {cal_left} cal, {protein_left}g protein")
    click.echo("")
    if meals:
        click.echo("Meals today:")
        for m in meals:
            click.echo(f"  {m['name']} — {m['calories']} cal, {m['protein']}g protein")
    else:
        click.echo("No meals logged today.")

    if cal_left > 500 and datetime.now().hour >= 15:
        click.echo("")
        click.echo("Looks like you have room for a snack \U0001f440 run munch snack")


@cli.command()
@click.argument("restaurant")
@click.option("--goal", default=None, help="Optional goal (e.g. 'high protein')")
def plan(restaurant: str, goal: str | None):
    """Suggest what to order given today's remaining macros."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return
    meals = db.get_today_meals()
    total_cal = sum(m["calories"] for m in meals)
    total_protein = sum(m["protein"] for m in meals)
    remaining_cal = profile["daily_calories"] - total_cal
    remaining_protein = profile["daily_protein"] - total_protein

    if remaining_cal <= 0:
        click.echo("You've already hit your calorie goal — maybe skip this meal!")
        return

    click.echo(f"Remaining budget: {remaining_cal} cal, {remaining_protein}g protein")
    if goal:
        click.echo(f"Goal: {goal}")
    click.echo("")
    suggestion = ai.suggest_order(restaurant, remaining_cal, remaining_protein)
    click.echo(suggestion)


@cli.command()
def dessert():
    """Check if you've earned dessert today."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return

    meals_today = db.get_today_meals()
    total_cal = sum(m["calories"] for m in meals_today)
    total_protein = sum(m["protein"] for m in meals_today)
    goal_cal = profile["daily_calories"]
    goal_protein = profile["daily_protein"]

    week_meals = db.get_week_meals()
    week_total_cal = sum(m["calories"] for m in week_meals)
    week_goal_cal = goal_cal * 7
    week_balance = week_total_cal - week_goal_cal

    verdict = ai.dessert_recommendation(
        total_cal, total_protein, goal_cal, goal_protein, week_balance,
    )
    click.echo(verdict)


SNACKS = [
    ("Almonds (20g handful)", 120, 4, 2),
    ("Walnuts (20g handful)", 130, 3, 1),
    ("Pistachios (30g)", 160, 6, 3),
    ("Baby carrots + 1 tbsp hummus", 70, 2, 3),
    ("Apple slices + 1 tsp PB", 130, 2, 4),
    ("Rice cakes (2)", 70, 1, 0),
    ("Celery + 1 tbsp PB", 100, 3, 2),
    ("Mixed berries (1 cup)", 70, 1, 4),
    ("Edamame (half cup)", 90, 9, 4),
]


@cli.command()
def snack():
    """Suggest a low-cal, high-fiber snack based on remaining macros."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return
    meals = db.get_today_meals()
    total_cal = sum(m["calories"] for m in meals)
    total_protein = sum(m["protein"] for m in meals)
    cal_left = profile["daily_calories"] - total_cal
    protein_left = profile["daily_protein"] - total_protein

    if cal_left <= 0:
        click.echo("You're at or over your calorie goal — maybe skip the snack tonight.")
        return

    click.echo(f"Remaining budget: {cal_left} cal, {protein_left}g protein")
    click.echo("")

    suggestions = []

    if protein_left > 30:
        suggestions.append(("Edamame (half cup) — 90 cal, 9g protein, 4g fiber", (90, 9, 4)))
        suggestions.append(("Pistachios (30g) — 160 cal, 6g protein, 3g fiber", (160, 6, 3)))

    if cal_left < 150:
        suggestions.append(("Baby carrots + 1 tbsp hummus — 70 cal, 2g protein, 3g fiber", (70, 2, 3)))
        suggestions.append(("Celery + 1 tbsp PB — 100 cal, 3g protein, 2g fiber", (100, 3, 2)))

    suggestions.append(("Almonds (20g handful) — 120 cal, 4g protein, 2g fiber", (120, 4, 2)))
    suggestions.append(("Rice cakes (2) — 70 cal, 1g protein, 0g fiber", (70, 1, 0)))

    seen = set()
    for label, _ in suggestions:
        name = label.split(" —")[0]
        if name not in seen:
            seen.add(name)
            click.echo(f"  \u2022 {label}")

    click.echo("")
    click.echo("Tip: prioritize fiber + satiety over pure calorie count.")


@cli.command()
@click.argument("restaurant")
@click.argument("rating", type=int)
@click.option("--notes", default=None, help="Optional notes")
def rate(restaurant: str, rating: int, notes: str | None):
    """Rate a restaurant (1-10)."""
    db.init_db()
    db.save_rating(restaurant, rating, notes)
    click.echo(f"Rated {restaurant}: {rating}/10" + (f" — {notes}" if notes else ""))


@cli.command()
def insights():
    """Analyze this week's meal patterns with AI."""
    profile = db.get_profile()
    if not profile:
        click.echo("Run `munch init` first to set your goals.")
        return
    meals = db.get_week_meals()
    if not meals:
        click.echo("No meals logged this week. Start logging to get insights!")
        return

    import json as _json
    meals_json = _json.dumps(meals, default=str)
    analysis = ai.analyze_insights(meals_json)
    click.echo(analysis)


@cli.command()
def history():
    """Show meals from the past 7 days, grouped by date with daily totals."""
    meals = db.get_history_meals(7)
    if not meals:
        click.echo("No meals logged in the past 7 days.")
        return

    from collections import defaultdict
    by_date = defaultdict(list)
    for m in meals:
        day = m["logged_at"][:10]
        by_date[day].append(m)

    for day in sorted(by_date, reverse=True):
        day_meals = by_date[day]
        total_cal = sum(m["calories"] for m in day_meals)
        total_protein = sum(m["protein"] for m in day_meals)
        click.echo(f"── {day} ──")
        for m in day_meals:
            click.echo(f"  {m['name']} — {m['calories']} cal, {m['protein']}g protein")
        click.echo(f"  Total: {total_cal} cal, {total_protein}g protein")
        click.echo("")


def main():
    db.init_db()
    cli()
