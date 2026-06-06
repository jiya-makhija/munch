import json
import os
from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            _client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )
        else:
            _client = OpenAI()
    return _client


_MODEL = os.environ.get("MUNCH_MODEL", "llama-3.3-70b-versatile")


def _ask(prompt: str) -> str:
    client = _get_client()
    r = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content.strip()


def estimate_macros(meal_name: str) -> tuple[int, int]:
    prompt = f"""You are a nutrition expert. Estimate the calories and protein in "{meal_name}" 
as ordered from a typical US chain restaurant. Respond ONLY with a JSON object like:
{{"calories": <int>, "protein": <int>}}"""
    raw = _ask(prompt)
    data = json.loads(raw)
    return int(data["calories"]), int(data["protein"])


def suggest_order(restaurant: str, remaining_cal: int, remaining_protein: int) -> str:
    prompt = f"""I have {remaining_cal} calories and {remaining_protein}g of protein remaining 
today. Recommend what to order at {restaurant} to stay within my budget. 
Suggest 1-2 items with estimated macros. Keep it concise and practical."""
    return _ask(prompt)


def dessert_recommendation(
    today_cal: int, today_protein: int,
    goal_cal: int, goal_protein: int,
    week_balance: int,
) -> str:
    cal_left = goal_cal - today_cal
    protein_left = goal_protein - today_protein
    prompt = f"""Today I've consumed {today_cal} cal / {today_protein}g protein (goal: {goal_cal} cal / {goal_protein}g protein). Remaining: {cal_left} cal / {protein_left}g protein. Weekly balance: {week_balance}.

Available treat options:
1. DEFAULT COMBO (recommend first if there's room):
   - Barebells Protein Bar (200cal, 20g protein)
   - Fage yogurt bowl + strawberries/blueberries + 1 tbsp PB (180cal, 18g protein)
   - Combined: ~380cal, 38g protein

2. BACKUP ONLY — David Protein Bar (150cal, 28g protein)
   Only recommend this when cal_left < 200 AND protein_left > 20g (over on calories, still short on protein).

Rules:
- Always recommend option 1 (the combo) if the user has >= 380 cal remaining
- Never recommend the David bar as default — only when the backup condition is met
- If there's no room for either, say to skip tonight
Keep it fun and under 4 sentences."""
    return _ask(prompt)


def analyze_insights(meals_json: str) -> str:
    prompt = f"""Analyze this week's meal data (JSON array) and provide insights:
{meals_json}

Highlight:
1. Most common meals/restaurants
2. Average daily calories and protein
3. Any patterns or trends
4. One actionable suggestion

Keep it concise, 4-6 sentences."""
    return _ask(prompt)
