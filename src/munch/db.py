import sqlite3
import os
from datetime import date, datetime
from typing import Optional

DB_DIR = os.path.expanduser("~/.munch")
DB_PATH = os.path.join(DB_DIR, "munch.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db():
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                daily_calories INTEGER NOT NULL,
                daily_protein INTEGER NOT NULL,
                location TEXT
            );
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein INTEGER NOT NULL,
                logged_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 10),
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
        """)


def get_profile() -> Optional[dict]:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        return dict(row) if row else None


def save_profile(calories: int, protein: int, location: str):
    with _conn() as conn:
        conn.execute("""
            INSERT INTO profile (id, daily_calories, daily_protein, location)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                daily_calories=excluded.daily_calories,
                daily_protein=excluded.daily_protein,
                location=excluded.location
        """, (calories, protein, location))


def log_meal(name: str, calories: int, protein: int):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO meals (name, calories, protein) VALUES (?, ?, ?)",
            (name, calories, protein),
        )


def get_today_meals() -> list[dict]:
    today = date.today().isoformat()
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM meals WHERE logged_at >= ? ORDER BY logged_at",
            (today,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_week_meals() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT * FROM meals
            WHERE logged_at >= datetime('now', '-7 days', 'localtime')
            ORDER BY logged_at
        """).fetchall()
        return [dict(r) for r in rows]


def save_rating(restaurant: str, rating: int, notes: Optional[str]):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO ratings (restaurant, rating, notes) VALUES (?, ?, ?)",
            (restaurant, rating, notes),
        )


def get_history_meals(days: int = 7) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT * FROM meals
            WHERE logged_at >= datetime('now', ? || ' days', 'localtime')
            ORDER BY logged_at DESC
        """, (-days,)).fetchall()
        return [dict(r) for r in rows]


def update_profile(calories: int | None = None, protein: int | None = None, location: str | None = None):
    fields = []
    vals = []
    if calories is not None:
        fields.append("daily_calories = ?")
        vals.append(calories)
    if protein is not None:
        fields.append("daily_protein = ?")
        vals.append(protein)
    if location is not None:
        fields.append("location = ?")
        vals.append(location)
    if not fields:
        return
    vals.append(1)
    with _conn() as conn:
        conn.execute(
            f"UPDATE profile SET {', '.join(fields)} WHERE id = ?",
            vals,
        )


def get_frequent_meals(limit: int = 5) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT name, calories, protein, COUNT(*) as cnt
            FROM meals
            GROUP BY name, calories, protein
            ORDER BY cnt DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def find_meal_by_name(name: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT name, calories, protein FROM meals WHERE name = ? ORDER BY logged_at DESC LIMIT 1",
            (name,),
        ).fetchone()
        return dict(row) if row else None
