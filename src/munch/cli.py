import click
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
@click.argument("meal")
@click.option("--cal", type=int, default=None, help="Calories (skips AI guess)")
@click.option("--protein", type=int, default=None, help="Protein in grams (skips AI guess)")
def log(meal: str, cal: int | None, protein: int | None):
    """Log a meal. Macros auto-estimated via AI if not provided."""
    if cal is None or protein is None:
        click.echo(f"Estimating macros for \"{meal}\"...")
        cal, protein = ai.estimate_macros(meal)
    db.init_db()
    db.log_meal(meal, cal, protein)
    click.echo(f"Logged: {meal} — {cal} cal, {protein}g protein")


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

    click.echo(f"Goals: {goal_cal} cal, {goal_protein}g protein")
    click.echo(f"Logged: {total_cal} cal, {total_protein}g protein")
    click.echo(f"Remaining: {goal_cal - total_cal} cal, {goal_protein - total_protein}g protein")
    click.echo("")
    if meals:
        click.echo("Meals today:")
        for m in meals:
            click.echo(f"  {m['name']} — {m['calories']} cal, {m['protein']}g protein")
    else:
        click.echo("No meals logged today.")


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
