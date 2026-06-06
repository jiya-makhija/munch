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


_VIBE = """You're a warm, supportive older sister who's into fitness. You genuinely care. Talk like a real person — short sentences, casual, encouraging. Celebrate wins, never guilt-trip. Use "okayy", "you've got this" energy. No bullet points, no robot speak, no preaching."""


def estimate_macros(meal_name: str) -> tuple[int, int]:
    prompt = f"""{_VIBE}

hey so \"{meal_name}\" — gimme a rough estimate. respond with ONLY valid json, no other text at all:
{{"calories": <int>, "protein": <int>}}"""
    raw = _ask(prompt)
    # strip any markdown fences
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    return int(data["calories"]), int(data["protein"])


def suggest_order(restaurant: str, remaining_cal: int, remaining_protein: int) -> str:
    prompt = f"""{_VIBE}

okay so you're at {restaurant} with {remaining_cal} cal and {remaining_protein}g protein left today. what should you grab? recommend 1-2 things that'll actually keep you on track. keep it real and specific."""
    return _ask(prompt)


def dessert_recommendation(
    today_cal: int, today_protein: int,
    goal_cal: int, goal_protein: int,
    week_balance: int,
) -> str:
    cal_left = goal_cal - today_cal
    protein_left = goal_protein - today_protein
    prompt = f"""{_VIBE}

okay let's talk dessert. today you're at {today_cal} cal / {today_protein}g protein (goal was {goal_cal} / {goal_protein}). so you've got {cal_left} cal and {protein_left}g protein left. weekly balance is {week_balance}.

here's what we're working with:
- the usual: barebells protein bar (200cal, 20g protein) + fage yogurt bowl with berries and a lil pb (180cal, 18g protein) = ~380cal total. this is the move if there's room.
- david protein bar (150cal, 28g protein) — only if they're over on calories but still short on protein (cal_left < 200 AND protein_left > 20g)

if they've got >=380cal left, tell them to go for the combo. if they're over calories but need protein, david bar's there. if there's no room, just say skip it tonight. keep it warm and under 4 sentences."""
    return _ask(prompt)


def analyze_insights(meals_json: str) -> str:
    prompt = f"""{_VIBE}

take a look at this week's meals and tell me what's up:
{meals_json}

what patterns do you see? what's working, what's not? any surprises? give one practical tip for next week. keep it real and supportive — no lecture, just honest vibes. 4-6 sentences."""
    return _ask(prompt)
