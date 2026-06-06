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
    prompt = f"""Today I've consumed {today_cal} cal / {today_protein}g protein (goal: {goal_cal} cal / {goal_protein}g protein).
My weekly calorie balance (total consumed - total goal) is {week_balance}.

Tell me if I've earned dessert today and what I should get. Consider:
- If I'm under my daily goal by 200+ cal, I've earned it
- If my weekly balance is negative (under budget), bonus points
- Suggest a specific dessert (ice cream, cookie, etc.)
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
