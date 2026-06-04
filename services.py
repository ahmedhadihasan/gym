"""Shared business logic for Flask and Streamlit."""
import os
from datetime import date, timedelta

from utils.csv_export import export_all_csv, generate_chatgpt_report, import_csv_file
from utils.db import BASE_DIR, get_connection, init_db, row_to_dict
from utils.dates import today_iso, weekday_index
from utils.met import (
    estimate_cardio_calories,
    estimate_swimming_calories,
    estimate_weight_training_calories,
)

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

WEIGHT_EXERCISES = {
    "Chest Press", "Incline Chest Press", "Pec Deck Fly", "Lat Pulldown",
    "Seated Row", "Low Row", "Leg Press", "Leg Curl", "Leg Extension",
    "Calf Raise", "Shoulder Press", "Lateral Raise", "Rear Delt", "Shrugs",
    "Biceps Curl", "Hammer Curl", "Triceps Pushdown", "Overhead Triceps Extension",
    "Overhead Extension",
}

CARDIO_SKIP = {"Bicycle", "Elliptical", "Incline Walk", "Stair Climber", "Walking"}


def ensure_database():
    if not os.path.exists(BASE_DIR / "gym_tracker.db"):
        init_db()


def get_user(conn):
    return row_to_dict(conn.execute("SELECT * FROM users WHERE id = 1").fetchone())


def get_latest_weight(conn):
    return row_to_dict(
        conn.execute(
            "SELECT weight_kg, log_date FROM body_weight ORDER BY log_date DESC LIMIT 1"
        ).fetchone()
    )


def weight_7day_avg(conn):
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    rows = conn.execute(
        "SELECT weight_kg FROM body_weight WHERE log_date >= ? ORDER BY log_date",
        (week_ago,),
    ).fetchall()
    if not rows:
        return None
    return round(sum(r[0] for r in rows) / len(rows), 2)


def progress_pct(current, goal, start):
    if start == goal:
        return 100
    total = start - goal
    done = start - current
    return round(max(0, min(100, (done / total) * 100 if total else 0)), 1)


def loss_pace_feedback(weekly_change_kg):
    if weekly_change_kg is None:
        return "unknown", "Log more weight entries"
    if weekly_change_kg < -1.0:
        return "too_fast", "Losing too fast — consider more calories"
    if weekly_change_kg > -0.25:
        return "too_slow", "Losing slowly — check deficit and consistency"
    return "good", "Good pace for fat loss (0.25–1 kg/week)"


def get_dashboard(local_date=None):
    ensure_database()
    conn = get_connection()
    try:
        user = get_user(conn)
        t = today_iso(explicit_date=local_date)
        wd = weekday_index(explicit_date=local_date)
        plan = conn.execute(
            "SELECT * FROM weekly_plan WHERE day_of_week = ? ORDER BY sort_order", (wd,)
        ).fetchall()
        plan_list = [row_to_dict(p) for p in plan]
        latest = get_latest_weight(conn)
        current_w = latest["weight_kg"] if latest else user["current_weight_kg"]
        goal_w = user["goal_weight_kg"]
        pct = progress_pct(current_w, goal_w, user["current_weight_kg"])
        avg7 = weight_7day_avg(conn)
        food_d = row_to_dict(conn.execute("SELECT * FROM food_logs WHERE log_date = ?", (t,)).fetchone()) or {}
        daily_d = row_to_dict(conn.execute("SELECT * FROM daily_logs WHERE log_date = ?", (t,)).fetchone()) or {}
        cardio_min = conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM cardio_logs WHERE log_date = ?", (t,)
        ).fetchone()[0]
        swim_min = conn.execute(
            "SELECT COALESCE(SUM(swimming_minutes), 0) FROM swimming_logs WHERE log_date = ?", (t,)
        ).fetchone()[0]
        weight_kg = current_w or 86
        burn_cardio = sum(
            r[0] or 0
            for r in conn.execute(
                "SELECT calories_burned_estimate FROM cardio_logs WHERE log_date = ?", (t,)
            ).fetchall()
        )
        burn_swim = sum(
            r[0] or 0
            for r in conn.execute(
                "SELECT calories_burned_estimate FROM swimming_logs WHERE log_date = ?", (t,)
            ).fetchall()
        )
        sets_today = conn.execute(
            """SELECT COUNT(*) FROM workout_sets ws
               JOIN workout_sessions s ON s.id = ws.session_id
               WHERE s.session_date = ? AND ws.completed = 1""",
            (t,),
        ).fetchone()[0]
        burn_weights = estimate_weight_training_calories(weight_kg, min(sets_today * 3, 50)) if sets_today else 0
        total_burn = round(burn_cardio + burn_swim + burn_weights, 1)
        calories_eaten = food_d.get("calories") or 0
        deficit = round(2200 + total_burn - calories_eaten, 1) if calories_eaten else None
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        w_start = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date >= ? ORDER BY log_date LIMIT 1",
            (week_ago,),
        ).fetchone()
        w_end = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date <= ? ORDER BY log_date DESC LIMIT 1",
            (t,),
        ).fetchone()
        weekly_change = round(w_end[0] - w_start[0], 2) if w_start and w_end else None
        pace_status, pace_msg = loss_pace_feedback(weekly_change)
        session = conn.execute("SELECT id FROM workout_sessions WHERE session_date = ?", (t,)).fetchone()
        return {
            "day_name": DAY_NAMES[wd],
            "is_rest_day": wd == 4,
            "muscle_group": plan_list[0]["muscle_group"] if plan_list else "Rest",
            "plan": plan_list,
            "current_weight": current_w,
            "goal_weight": goal_w,
            "progress_percent": pct,
            "weight_7day_avg": avg7,
            "calories": food_d.get("calories"),
            "protein": food_d.get("protein_g"),
            "cardio_minutes": cardio_min,
            "swimming_minutes": swim_min,
            "steps": daily_d.get("steps"),
            "calories_burned_estimate": total_burn,
            "estimated_deficit": deficit,
            "pace_message": pace_msg,
            "session_id": session[0] if session else None,
        }
    finally:
        conn.close()


def save_weight(log_date, weight_kg):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO body_weight (log_date, weight_kg) VALUES (?, ?)
               ON CONFLICT(user_id, log_date) DO UPDATE SET weight_kg = excluded.weight_kg""",
            (log_date, float(weight_kg)),
        )
        conn.execute("UPDATE users SET current_weight_kg = ? WHERE id = 1", (float(weight_kg),))
        conn.commit()
        export_all_csv()
    finally:
        conn.close()


def get_weight_history():
    conn = get_connection()
    try:
        history = [row_to_dict(r) for r in conn.execute(
            "SELECT log_date, weight_kg FROM body_weight ORDER BY log_date DESC LIMIT 90"
        ).fetchall()]
        return history, weight_7day_avg(conn)
    finally:
        conn.close()


def _previous_sets_by_number(conn, exercise_name, before_date):
    """Most recent past session's sets for this exercise (per set_number)."""
    row = conn.execute(
        """SELECT s.id, s.session_date FROM workout_sessions s
           JOIN workout_sets ws ON ws.session_id = s.id
           WHERE ws.exercise_name = ? AND s.session_date < ?
           AND ws.completed = 1
           ORDER BY s.session_date DESC LIMIT 1""",
        (exercise_name, before_date),
    ).fetchone()
    if not row:
        return None, {}
    sid, session_date = row[0], row[1]
    sets = conn.execute(
        """SELECT set_number, weight_kg, reps FROM workout_sets
           WHERE session_id = ? AND exercise_name = ? ORDER BY set_number""",
        (sid, exercise_name),
    ).fetchall()
    by_num = {
        s[0]: {"weight_kg": s[1], "reps": s[2], "session_date": session_date}
        for s in sets
    }
    return session_date, by_num


def ensure_workout_session(local_date=None, muscle_group=None):
    """Create workout session for a calendar day if missing."""
    ensure_database()
    conn = get_connection()
    try:
        wd = weekday_index(explicit_date=local_date)
        t = today_iso(explicit_date=local_date)
        plan_list = [row_to_dict(p) for p in conn.execute(
            "SELECT * FROM weekly_plan WHERE day_of_week = ? ORDER BY sort_order", (wd,)
        ).fetchall()]
        session = conn.execute("SELECT * FROM workout_sessions WHERE session_date = ?", (t,)).fetchone()
        if session:
            return row_to_dict(session)["id"]
        mg = muscle_group or (plan_list[0].get("muscle_group") if plan_list else "Workout")
        session_id = conn.execute(
            "INSERT INTO workout_sessions (session_date, day_name, muscle_group) VALUES (?, ?, ?)",
            (t, DAY_NAMES[wd], mg),
        ).lastrowid
        conn.commit()
        return session_id
    finally:
        conn.close()


def get_workout_today(local_date=None):
    ensure_database()
    conn = get_connection()
    try:
        wd = weekday_index(explicit_date=local_date)
        t = today_iso(explicit_date=local_date)
        plan_list = [row_to_dict(p) for p in conn.execute(
            "SELECT * FROM weekly_plan WHERE day_of_week = ? ORDER BY sort_order", (wd,)
        ).fetchall()]
        session = conn.execute("SELECT * FROM workout_sessions WHERE session_date = ?", (t,)).fetchone()
        session_id = row_to_dict(session)["id"] if session else None
        seen = set()
        exercises = []

        def append_exercise(p):
            ex = p["exercise_name"]
            if ex in seen:
                return
            seen.add(ex)
            if ex in ("Swimming", "Easy Swimming"):
                return
            if "min" in (p.get("reps_target") or "") and ex in CARDIO_SKIP:
                return
            _prev_date, prev_by_set = _previous_sets_by_number(conn, ex, t)
            last = conn.execute(
                """SELECT weight_kg, reps FROM workout_sets
                   WHERE exercise_name = ? AND weight_kg IS NOT NULL ORDER BY id DESC LIMIT 1""",
                (ex,),
            ).fetchone()
            sets_done = []
            if session_id:
                sets_done = conn.execute(
                    """SELECT * FROM workout_sets WHERE session_id = ? AND exercise_name = ?
                       ORDER BY set_number""",
                    (session_id, ex),
                ).fetchall()
            target_sets = int(p.get("sets_target") or 3)
            if ex in WEIGHT_EXERCISES or target_sets > 1 or sets_done:
                exercises.append({
                    **p,
                    "sets_target": target_sets,
                    "last_weight_kg": last["weight_kg"] if last else None,
                    "last_reps": last["reps"] if last else None,
                    "previous_session_date": _prev_date,
                    "previous_sets": prev_by_set,
                    "sets_logged": [row_to_dict(s) for s in sets_done],
                })

        for p in plan_list:
            append_exercise(p)

        if session_id:
            extra_names = conn.execute(
                """SELECT DISTINCT exercise_name FROM workout_sets WHERE session_id = ?""",
                (session_id,),
            ).fetchall()
            for (ex_name,) in extra_names:
                if ex_name in seen:
                    continue
                append_exercise({
                    "exercise_name": ex_name,
                    "sets_target": 3,
                    "reps_target": "12",
                    "muscle_group": "Custom",
                })

        return {
            "day_name": DAY_NAMES[wd],
            "session_date": t,
            "is_rest_day": wd == 4,
            "session_id": session_id,
            "exercises": exercises,
            "plan": plan_list,
        }
    finally:
        conn.close()


def save_workout_set(session_id, exercise_name, set_number, weight_kg, reps, completed, notes=""):
    conn = get_connection()
    try:
        existing = conn.execute(
            """SELECT id FROM workout_sets WHERE session_id=? AND exercise_name=? AND set_number=?""",
            (session_id, exercise_name, int(set_number)),
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE workout_sets SET weight_kg=?, reps=?, completed=?, notes=? WHERE id=?""",
                (weight_kg, reps, 1 if completed else 0, notes, existing[0]),
            )
        else:
            conn.execute(
                """INSERT INTO workout_sets (session_id, exercise_name, set_number, weight_kg, reps, completed, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, exercise_name, int(set_number), weight_kg, reps, 1 if completed else 0, notes),
            )
        conn.commit()
        export_all_csv()
    finally:
        conn.close()


def save_cardio(log_date, cardio_type, duration_minutes, intensity, calories=None, notes="", steps=None):
    conn = get_connection()
    try:
        user = get_user(conn)
        latest = get_latest_weight(conn)
        w = float(latest["weight_kg"] if latest else user["current_weight_kg"])
        cal = calories if calories is not None else estimate_cardio_calories(cardio_type, w, duration_minutes, intensity)
        conn.execute(
            """INSERT INTO cardio_logs (log_date, cardio_type, duration_minutes, intensity,
               calories_burned_estimate, source, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (log_date, cardio_type, duration_minutes, intensity, cal, "manual", notes),
        )
        if steps:
            conn.execute(
                """INSERT INTO daily_logs (log_date, steps) VALUES (?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET steps=excluded.steps""",
                (log_date, int(steps)),
            )
        conn.commit()
        export_all_csv()
        return cal
    finally:
        conn.close()


def save_swimming(log_date, minutes, intensity, calories=None, notes=""):
    conn = get_connection()
    try:
        user = get_user(conn)
        latest = get_latest_weight(conn)
        w = float(latest["weight_kg"] if latest else user["current_weight_kg"])
        cal = calories if calories is not None else estimate_swimming_calories(w, minutes, intensity)
        conn.execute(
            """INSERT INTO swimming_logs (log_date, swimming_minutes, intensity,
               calories_burned_estimate, notes) VALUES (?, ?, ?, ?, ?)""",
            (log_date, minutes, intensity, cal, notes),
        )
        conn.commit()
        export_all_csv()
        return cal
    finally:
        conn.close()


def save_food(log_date, calories, protein_g, carbs_g, fat_g, water_liters, steps, sleep_hours, notes):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO food_logs (log_date, calories, protein_g, carbs_g, fat_g, water_liters, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, log_date) DO UPDATE SET
               calories=excluded.calories, protein_g=excluded.protein_g,
               carbs_g=excluded.carbs_g, fat_g=excluded.fat_g,
               water_liters=excluded.water_liters, notes=excluded.notes""",
            (log_date, calories, protein_g, carbs_g, fat_g, water_liters, notes),
        )
        conn.execute(
            """INSERT INTO daily_logs (log_date, steps, sleep_hours, water_liters, notes)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(user_id, log_date) DO UPDATE SET
               steps=excluded.steps, sleep_hours=excluded.sleep_hours,
               water_liters=COALESCE(excluded.water_liters, daily_logs.water_liters),
               notes=excluded.notes""",
            (log_date, steps, sleep_hours, water_liters, notes),
        )
        conn.commit()
        export_all_csv()
    finally:
        conn.close()


def get_food(log_date):
    conn = get_connection()
    try:
        food = row_to_dict(conn.execute("SELECT * FROM food_logs WHERE log_date = ?", (log_date,)).fetchone())
        daily = row_to_dict(conn.execute("SELECT * FROM daily_logs WHERE log_date = ?", (log_date,)).fetchone())
        return food, daily
    finally:
        conn.close()


def get_weekly_report(days=7):
    conn = get_connection()
    try:
        since = (date.today() - timedelta(days=days)).isoformat()
        weights = conn.execute("SELECT weight_kg FROM body_weight WHERE log_date >= ?", (since,)).fetchall()
        avg_w = round(sum(r[0] for r in weights) / len(weights), 2) if weights else None
        workouts = conn.execute(
            "SELECT COUNT(DISTINCT session_date) FROM workout_sessions WHERE session_date >= ?", (since,)
        ).fetchone()[0]
        swim = conn.execute(
            "SELECT COALESCE(SUM(swimming_minutes), 0) FROM swimming_logs WHERE log_date >= ?", (since,)
        ).fetchone()[0]
        cardio = conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM cardio_logs WHERE log_date >= ?", (since,)
        ).fetchone()[0]
        foods = conn.execute(
            "SELECT calories, protein_g FROM food_logs WHERE log_date >= ?", (since,)
        ).fetchall()
        avg_cal = round(sum(r[0] or 0 for r in foods) / len(foods), 1) if foods else None
        avg_prot = round(sum(r[1] or 0 for r in foods) / len(foods), 1) if foods else None
        return {
            "average_weight": avg_w,
            "total_workouts": workouts,
            "total_swimming_minutes": swim,
            "total_cardio_minutes": cardio,
            "average_calories": avg_cal,
            "average_protein": avg_prot,
        }
    finally:
        conn.close()
