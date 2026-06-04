import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

from utils.db import get_connection

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"

DAILY_SUMMARY_COLS = [
    "date", "body_weight_kg", "calories_eaten", "protein_g", "carbs_g", "fat_g",
    "water_liters", "steps", "sleep_hours", "notes",
]
WORKOUT_LOG_COLS = [
    "date", "day_name", "muscle_group", "exercise_name", "set_number",
    "weight_kg", "reps", "completed", "notes",
]
CARDIO_LOG_COLS = [
    "date", "cardio_type", "duration_minutes", "intensity",
    "calories_burned_estimate", "source", "notes",
]
SWIMMING_LOG_COLS = [
    "date", "swimming_minutes", "intensity", "calories_burned_estimate", "notes",
]
WEEKLY_REPORT_COLS = [
    "week_start", "week_end", "average_weight", "weight_change_kg",
    "average_calories", "average_protein", "total_cardio_minutes",
    "total_swimming_minutes", "total_steps", "total_workouts",
]


def _write_csv(path, columns, rows):
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in columns})


def export_daily_summary(conn):
    rows = conn.execute("""
        SELECT
            COALESCE(bw.log_date, f.log_date, d.log_date) AS date,
            bw.weight_kg AS body_weight_kg,
            f.calories AS calories_eaten,
            f.protein_g,
            f.carbs_g,
            f.fat_g,
            COALESCE(f.water_liters, d.water_liters) AS water_liters,
            d.steps,
            d.sleep_hours,
            TRIM(COALESCE(f.notes, '') || ' ' || COALESCE(d.notes, '')) AS notes
        FROM (
            SELECT log_date FROM body_weight
            UNION SELECT log_date FROM food_logs
            UNION SELECT log_date FROM daily_logs
        ) dates
        LEFT JOIN body_weight bw ON bw.log_date = dates.log_date
        LEFT JOIN food_logs f ON f.log_date = dates.log_date
        LEFT JOIN daily_logs d ON d.log_date = dates.log_date
        ORDER BY date DESC
    """).fetchall()
    data = [dict(r) for r in rows]
    _write_csv(EXPORTS_DIR / "daily_summary.csv", DAILY_SUMMARY_COLS, data)
    return data


def export_workout_log(conn):
    rows = conn.execute("""
        SELECT
            ws.session_date AS date,
            ws.day_name,
            ws.muscle_group,
            wset.exercise_name,
            wset.set_number,
            wset.weight_kg,
            wset.reps,
            wset.completed,
            wset.notes
        FROM workout_sets wset
        JOIN workout_sessions ws ON ws.id = wset.session_id
        ORDER BY ws.session_date DESC, wset.exercise_name, wset.set_number
    """).fetchall()
    data = [dict(r) for r in rows]
    _write_csv(EXPORTS_DIR / "workout_log.csv", WORKOUT_LOG_COLS, data)
    return data


def export_cardio_log(conn):
    rows = conn.execute("""
        SELECT log_date AS date, cardio_type, duration_minutes, intensity,
               calories_burned_estimate, source, notes
        FROM cardio_logs ORDER BY log_date DESC
    """).fetchall()
    data = [dict(r) for r in rows]
    _write_csv(EXPORTS_DIR / "cardio_log.csv", CARDIO_LOG_COLS, data)
    return data


def export_swimming_log(conn):
    rows = conn.execute("""
        SELECT log_date AS date, swimming_minutes, intensity,
               calories_burned_estimate, notes
        FROM swimming_logs ORDER BY log_date DESC
    """).fetchall()
    data = [dict(r) for r in rows]
    _write_csv(EXPORTS_DIR / "swimming_log.csv", SWIMMING_LOG_COLS, data)
    return data


def export_weekly_report(conn):
    rows = []
    dates = conn.execute("""
        SELECT DISTINCT log_date FROM body_weight
        UNION SELECT DISTINCT log_date FROM food_logs
        UNION SELECT DISTINCT session_date FROM workout_sessions
        ORDER BY log_date
    """).fetchall()
    if not dates:
        _write_csv(EXPORTS_DIR / "weekly_report.csv", WEEKLY_REPORT_COLS, [])
        return []

    all_dates = sorted(set(
        [r[0] for r in conn.execute("SELECT log_date FROM body_weight").fetchall()] +
        [r[0] for r in conn.execute("SELECT log_date FROM food_logs").fetchall()] +
        [r[0] for r in conn.execute("SELECT session_date FROM workout_sessions").fetchall()]
    ))
    if not all_dates:
        _write_csv(EXPORTS_DIR / "weekly_report.csv", WEEKLY_REPORT_COLS, [])
        return []

    start = datetime.strptime(all_dates[0], "%Y-%m-%d").date()
    end = datetime.strptime(all_dates[-1], "%Y-%m-%d").date()
    week_start = start - timedelta(days=start.weekday())

    while week_start <= end:
        week_end = week_start + timedelta(days=6)
        ws = week_start.isoformat()
        we = week_end.isoformat()

        weights = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchall()
        avg_w = round(sum(r[0] for r in weights) / len(weights), 2) if weights else ""

        first_w = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date >= ? ORDER BY log_date LIMIT 1",
            (ws,),
        ).fetchone()
        last_w = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date <= ? ORDER BY log_date DESC LIMIT 1",
            (we,),
        ).fetchone()
        change = ""
        if first_w and last_w:
            change = round(last_w[0] - first_w[0], 2)

        foods = conn.execute(
            "SELECT calories, protein_g FROM food_logs WHERE log_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchall()
        avg_cal = round(sum(r[0] or 0 for r in foods) / len(foods), 1) if foods else ""
        avg_prot = round(sum(r[1] or 0 for r in foods) / len(foods), 1) if foods else ""

        cardio = conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM cardio_logs WHERE log_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchone()[0]
        swim = conn.execute(
            "SELECT COALESCE(SUM(swimming_minutes), 0) FROM swimming_logs WHERE log_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchone()[0]
        steps = conn.execute(
            "SELECT COALESCE(SUM(steps), 0) FROM daily_logs WHERE log_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchone()[0]
        workouts = conn.execute(
            "SELECT COUNT(DISTINCT session_date) FROM workout_sessions WHERE session_date BETWEEN ? AND ?",
            (ws, we),
        ).fetchone()[0]

        rows.append({
            "week_start": ws,
            "week_end": we,
            "average_weight": avg_w,
            "weight_change_kg": change,
            "average_calories": avg_cal,
            "average_protein": avg_prot,
            "total_cardio_minutes": cardio,
            "total_swimming_minutes": swim,
            "total_steps": steps,
            "total_workouts": workouts,
        })
        week_start += timedelta(days=7)

    _write_csv(EXPORTS_DIR / "weekly_report.csv", WEEKLY_REPORT_COLS, rows)
    return rows


def export_all_csv():
    conn = get_connection()
    try:
        export_daily_summary(conn)
        export_workout_log(conn)
        export_cardio_log(conn)
        export_swimming_log(conn)
        export_weekly_report(conn)
    finally:
        conn.close()
    return EXPORTS_DIR


def append_daily_row_to_csv(log_date, row_data):
    """Append or update today's row in daily_summary.csv after each save."""
    export_all_csv()


def import_csv_file(filename, conn):
    path = EXPORTS_DIR / filename
    if not path.exists():
        return False, "File not found"

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if filename == "daily_summary.csv":
        for r in rows:
            d = r.get("date")
            if not d:
                continue
            if r.get("body_weight_kg"):
                conn.execute(
                    """INSERT INTO body_weight (log_date, weight_kg) VALUES (?, ?)
                       ON CONFLICT(user_id, log_date) DO UPDATE SET weight_kg=excluded.weight_kg""",
                    (d, float(r["body_weight_kg"])),
                )
            conn.execute(
                """INSERT INTO food_logs (log_date, calories, protein_g, carbs_g, fat_g, water_liters, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET
                   calories=excluded.calories, protein_g=excluded.protein_g,
                   carbs_g=excluded.carbs_g, fat_g=excluded.fat_g,
                   water_liters=excluded.water_liters, notes=excluded.notes""",
                (d, r.get("calories_eaten") or None, r.get("protein_g") or None,
                 r.get("carbs_g") or None, r.get("fat_g") or None,
                 r.get("water_liters") or None, r.get("notes") or None),
            )
            conn.execute(
                """INSERT INTO daily_logs (log_date, steps, sleep_hours, water_liters, notes)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET
                   steps=excluded.steps, sleep_hours=excluded.sleep_hours,
                   water_liters=excluded.water_liters, notes=excluded.notes""",
                (d, r.get("steps") or None, r.get("sleep_hours") or None,
                 r.get("water_liters") or None, r.get("notes") or None),
            )
    elif filename == "workout_log.csv":
        for r in rows:
            d, ex = r.get("date"), r.get("exercise_name")
            if not d or not ex:
                continue
            sess = conn.execute(
                "SELECT id FROM workout_sessions WHERE session_date=? AND day_name=?",
                (d, r.get("day_name", "")),
            ).fetchone()
            if not sess:
                cur = conn.execute(
                    """INSERT INTO workout_sessions (session_date, day_name, muscle_group)
                       VALUES (?, ?, ?)""",
                    (d, r.get("day_name", ""), r.get("muscle_group", "")),
                )
                sid = cur.lastrowid
            else:
                sid = sess[0]
            conn.execute(
                """INSERT INTO workout_sets (session_id, exercise_name, set_number, weight_kg, reps, completed, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sid, ex, int(r.get("set_number") or 1), r.get("weight_kg") or None,
                 r.get("reps") or None, 1 if str(r.get("completed")).lower() in ("1", "true", "yes") else 0,
                 r.get("notes") or ""),
            )
    elif filename == "cardio_log.csv":
        for r in rows:
            if not r.get("date"):
                continue
            conn.execute(
                """INSERT INTO cardio_logs (log_date, cardio_type, duration_minutes, intensity,
                   calories_burned_estimate, source, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (r["date"], r.get("cardio_type", ""), r.get("duration_minutes") or 0,
                 r.get("intensity", "moderate"), r.get("calories_burned_estimate") or None,
                 r.get("source", "import"), r.get("notes") or ""),
            )
    elif filename == "swimming_log.csv":
        for r in rows:
            if not r.get("date"):
                continue
            conn.execute(
                """INSERT INTO swimming_logs (log_date, swimming_minutes, intensity,
                   calories_burned_estimate, notes) VALUES (?, ?, ?, ?, ?)""",
                (r["date"], r.get("swimming_minutes") or 0, r.get("intensity", "moderate"),
                 r.get("calories_burned_estimate") or None, r.get("notes") or ""),
            )

    conn.commit()
    return True, f"Imported {len(rows)} rows from {filename}"


def generate_chatgpt_report():
    export_all_csv()
    lines = ["# Gym Tracker Report", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    for fname, title in [
        ("daily_summary.csv", "## Daily Summary (last 14 days)"),
        ("workout_log.csv", "## Workout Log (last 7 days)"),
        ("cardio_log.csv", "## Cardio Log (last 7 days)"),
        ("swimming_log.csv", "## Swimming Log (last 7 days)"),
        ("weekly_report.csv", "## Weekly Reports"),
    ]:
        path = EXPORTS_DIR / fname
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        limit = 14 if "daily" in fname else 7 if fname != "weekly_report.csv" else 4
        recent = reader[:limit] if fname != "weekly_report.csv" else reader[-4:]
        lines.append(title)
        if not recent:
            lines.append("(no data)")
        else:
            for row in recent:
                parts = [f"{k}: {v}" for k, v in row.items() if v]
                lines.append("- " + " | ".join(parts))
        lines.append("")

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id=1").fetchone()
    conn.close()
    if user:
        lines.insert(1, f"Profile: {user['gender']}, {user['age']}y, {user['height_cm']}cm, "
                        f"Goal: {user['goal_weight_kg']}kg by {user['goal_date']}, "
                        f"Current target: fat loss. Restrictions: {user['restrictions']}")
        lines.insert(2, "")

    return "\n".join(lines)
