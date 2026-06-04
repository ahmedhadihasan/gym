import os
from datetime import date, datetime, timedelta

from flask import Flask, jsonify, render_template, request, send_from_directory

from utils.csv_export import export_all_csv, generate_chatgpt_report, import_csv_file
from utils.db import get_connection, init_db, row_to_dict
from utils.met import (
    estimate_cardio_calories,
    estimate_swimming_calories,
    estimate_weight_training_calories,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "gym-tracker-local"

from utils.dates import resolve_today, today_iso, weekday_index

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_user(conn):
    row = conn.execute("SELECT * FROM users WHERE id = 1").fetchone()
    return row_to_dict(row)


def get_latest_weight(conn):
    row = conn.execute(
        "SELECT weight_kg, log_date FROM body_weight ORDER BY log_date DESC LIMIT 1"
    ).fetchone()
    return row_to_dict(row)


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
    pct = (done / total) * 100 if total else 0
    return round(max(0, min(100, pct)), 1)


def loss_pace_feedback(weekly_change_kg):
    if weekly_change_kg is None:
        return "unknown", "Log more weight entries"
    if weekly_change_kg < -1.0:
        return "too_fast", "Losing too fast — consider more calories"
    if weekly_change_kg > -0.25:
        return "too_slow", "Losing slowly — check deficit and consistency"
    return "good", "Good pace for fat loss (0.25–1 kg/week)"


@app.before_request
def ensure_db():
    if not os.path.exists(os.path.join(app.root_path, "gym_tracker.db")):
        init_db()


# --- Pages ---

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/weight")
def weight_page():
    return render_template("weight.html")


@app.route("/workout")
def workout_page():
    return render_template("workout.html")


@app.route("/cardio")
def cardio_page():
    return render_template("cardio.html")


@app.route("/swimming")
def swimming_page():
    return render_template("swimming.html")


@app.route("/food")
def food_page():
    return render_template("food.html")


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/settings")
def settings_page():
    return render_template("settings.html")


@app.route("/course-plan")
def course_plan_page():
    return render_template("course_plan.html", active="plan")


@app.route("/api/course-plan")
def api_course_plan():
    from data.course_i18n import get_course_plan
    lang = request.args.get("lang", "en")
    return jsonify(get_course_plan(lang))


# --- API: Dashboard ---

@app.route("/api/dashboard")
def api_dashboard():
    conn = get_connection()
    try:
        user = get_user(conn)
        t = today_iso(request)
        wd = weekday_index(request)
        plan = conn.execute(
            "SELECT * FROM weekly_plan WHERE day_of_week = ? ORDER BY sort_order",
            (wd,),
        ).fetchall()
        plan_list = [row_to_dict(p) for p in plan]

        latest = get_latest_weight(conn)
        current_w = latest["weight_kg"] if latest else user["current_weight_kg"]
        goal_w = user["goal_weight_kg"]
        start_w = user["current_weight_kg"]
        pct = progress_pct(current_w, goal_w, start_w)
        avg7 = weight_7day_avg(conn)

        food = conn.execute("SELECT * FROM food_logs WHERE log_date = ?", (t,)).fetchone()
        daily = conn.execute("SELECT * FROM daily_logs WHERE log_date = ?", (t,)).fetchone()
        food_d = row_to_dict(food) or {}
        daily_d = row_to_dict(daily) or {}

        cardio_min = conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM cardio_logs WHERE log_date = ?",
            (t,),
        ).fetchone()[0]
        swim_min = conn.execute(
            "SELECT COALESCE(SUM(swimming_minutes), 0) FROM swimming_logs WHERE log_date = ?",
            (t,),
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
        if sets_today > 0:
            burn_weights = estimate_weight_training_calories(weight_kg, min(sets_today * 3, 50))
        else:
            burn_weights = 0

        total_burn = round(burn_cardio + burn_swim + burn_weights, 1)
        calories_eaten = food_d.get("calories") or 0
        deficit = round(total_burn - calories_eaten + 2000, 1) if calories_eaten else None
        # TDEE rough estimate ~ weight*24 for sedentary+activity; use 2200 base + burn - eaten
        tdee_est = 2200
        if calories_eaten:
            deficit = round(tdee_est + total_burn - calories_eaten, 1)

        week_ago = (date.today() - timedelta(days=7)).isoformat()
        w_start = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date >= ? ORDER BY log_date LIMIT 1",
            (week_ago,),
        ).fetchone()
        w_end = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date <= ? ORDER BY log_date DESC LIMIT 1",
            (t,),
        ).fetchone()
        weekly_change = None
        if w_start and w_end:
            weekly_change = round(w_end[0] - w_start[0], 2)
        pace_status, pace_msg = loss_pace_feedback(weekly_change)

        session = conn.execute(
            "SELECT id FROM workout_sessions WHERE session_date = ?", (t,)
        ).fetchone()

        return jsonify({
            "day_name": DAY_NAMES[wd],
            "day_of_week": wd,
            "is_rest_day": wd == 4,
            "muscle_group": plan_list[0]["muscle_group"] if plan_list else "Rest",
            "plan": plan_list,
            "user": user,
            "current_weight": current_w,
            "goal_weight": goal_w,
            "progress_percent": pct,
            "weight_7day_avg": avg7,
            "calories": food_d.get("calories"),
            "protein": food_d.get("protein_g"),
            "cardio_minutes": cardio_min,
            "swimming_minutes": swim_min,
            "steps": daily_d.get("steps"),
            "water": food_d.get("water_liters") or daily_d.get("water_liters"),
            "calories_burned_estimate": total_burn,
            "estimated_deficit": deficit,
            "weekly_avg_weight": avg7,
            "weekly_weight_change": weekly_change,
            "pace_status": pace_status,
            "pace_message": pace_msg,
            "session_id": session[0] if session else None,
            "nutrition_targets": {
                "calories_min": 1700, "calories_max": 1900,
                "protein_min": 150, "protein_max": 180,
                "water_min": 3, "water_max": 4,
                "steps_min": 7000, "steps_max": 10000,
            },
        })
    finally:
        conn.close()


# --- API: Body weight ---

@app.route("/api/weight", methods=["GET", "POST"])
def api_weight():
    conn = get_connection()
    try:
        if request.method == "POST":
            data = request.json
            conn.execute(
                """INSERT INTO body_weight (log_date, weight_kg) VALUES (?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET weight_kg = excluded.weight_kg""",
                (data.get("log_date", today_iso(request)), float(data["weight_kg"])),
            )
            conn.execute(
                "UPDATE users SET current_weight_kg = ? WHERE id = 1",
                (float(data["weight_kg"]),),
            )
            conn.commit()
            export_all_csv()
            return jsonify({"ok": True})

        history = conn.execute(
            "SELECT log_date, weight_kg FROM body_weight ORDER BY log_date DESC LIMIT 90"
        ).fetchall()
        history = [row_to_dict(r) for r in history]
        avg7 = weight_7day_avg(conn)
        return jsonify({"history": history, "avg_7day": avg7})
    finally:
        conn.close()


# --- API: Workout ---

@app.route("/api/workout/today")
def api_workout_today():
    conn = get_connection()
    try:
        wd = weekday_index(request)
        t = today_iso(request)
        plan = conn.execute(
            "SELECT * FROM weekly_plan WHERE day_of_week = ? ORDER BY sort_order",
            (wd,),
        ).fetchall()
        plan_list = [row_to_dict(p) for p in plan]

        session = conn.execute(
            "SELECT * FROM workout_sessions WHERE session_date = ?", (t,)
        ).fetchone()
        session_id = None
        if not session and plan_list and wd != 4:
            mg = plan_list[0].get("muscle_group", "")
            cur = conn.execute(
                "INSERT INTO workout_sessions (session_date, day_name, muscle_group) VALUES (?, ?, ?)",
                (t, DAY_NAMES[wd], mg),
            )
            session_id = cur.lastrowid
            conn.commit()
        elif session:
            session_id = session["id"]

        exercises = []
        weight_exercises = {
            "Chest Press", "Incline Chest Press", "Pec Deck Fly", "Lat Pulldown",
            "Seated Row", "Low Row", "Leg Press", "Leg Curl", "Leg Extension",
            "Calf Raise", "Shoulder Press", "Lateral Raise", "Rear Delt", "Shrugs",
            "Biceps Curl", "Hammer Curl", "Triceps Pushdown", "Overhead Triceps Extension",
            "Overhead Extension",
        }
        for p in plan_list:
            ex = p["exercise_name"]
            if ex in ("Swimming", "Easy Swimming") or "min" in (p.get("reps_target") or "") and ex in (
                "Bicycle", "Elliptical", "Incline Walk", "Stair Climber", "Walking"
            ):
                continue
            last = conn.execute(
                """SELECT weight_kg, reps FROM workout_sets
                   WHERE exercise_name = ? AND weight_kg IS NOT NULL
                   ORDER BY id DESC LIMIT 1""",
                (ex,),
            ).fetchone()
            sets_done = []
            if session_id:
                sets_done = conn.execute(
                    """SELECT * FROM workout_sets WHERE session_id = ? AND exercise_name = ?
                       ORDER BY set_number""",
                    (session_id, ex),
                ).fetchall()
            exercises.append({
                **p,
                "last_weight_kg": last["weight_kg"] if last else None,
                "last_reps": last["reps"] if last else None,
                "sets_logged": [row_to_dict(s) for s in sets_done],
                "is_weight_exercise": ex in weight_exercises or p.get("sets_target", 0) > 1,
            })

        return jsonify({
            "day_name": DAY_NAMES[wd],
            "session_id": session_id,
            "exercises": exercises,
            "plan": plan_list,
        })
    finally:
        conn.close()


@app.route("/api/workout/set", methods=["POST"])
def api_workout_set():
    data = request.json
    conn = get_connection()
    try:
        session_id = data["session_id"]
        existing = conn.execute(
            """SELECT id FROM workout_sets WHERE session_id=? AND exercise_name=? AND set_number=?""",
            (session_id, data["exercise_name"], int(data["set_number"])),
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE workout_sets SET weight_kg=?, reps=?, completed=?, notes=? WHERE id=?""",
                (data.get("weight_kg"), data.get("reps"),
                 1 if data.get("completed") else 0, data.get("notes", ""), existing[0]),
            )
        else:
            conn.execute(
                """INSERT INTO workout_sets (session_id, exercise_name, set_number, weight_kg, reps, completed, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, data["exercise_name"], int(data["set_number"]),
                 data.get("weight_kg"), data.get("reps"),
                 1 if data.get("completed") else 0, data.get("notes", "")),
            )
        conn.commit()
        export_all_csv()
        return jsonify({"ok": True})
    finally:
        conn.close()


@app.route("/api/workout/last-weight/<exercise_name>")
def api_last_weight(exercise_name):
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT weight_kg, reps, notes FROM workout_sets
               WHERE exercise_name = ? AND weight_kg IS NOT NULL ORDER BY id DESC LIMIT 1""",
            (exercise_name,),
        ).fetchone()
        return jsonify(row_to_dict(row) or {})
    finally:
        conn.close()


# --- API: Cardio ---

@app.route("/api/cardio", methods=["GET", "POST"])
def api_cardio():
    conn = get_connection()
    try:
        if request.method == "POST":
            data = request.json
            user = get_user(conn)
            w = float(data.get("body_weight_kg") or get_latest_weight(conn)["weight_kg"] if get_latest_weight(conn) else user["current_weight_kg"])
            ctype = data["cardio_type"]
            mins = float(data["duration_minutes"])
            intensity = data.get("intensity", "moderate")
            cal = data.get("calories_burned_estimate")
            if cal is None or cal == "":
                cal = estimate_cardio_calories(ctype, w, mins, intensity)
            conn.execute(
                """INSERT INTO cardio_logs (log_date, cardio_type, duration_minutes, intensity,
                   calories_burned_estimate, source, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data.get("log_date", today_iso(request)), ctype, mins, intensity, cal,
                 data.get("source", "manual"), data.get("notes", "")),
            )
            conn.commit()
            export_all_csv()
            return jsonify({"ok": True, "calories_estimate": cal})

        t = request.args.get("date") or today_iso(request)
        rows = conn.execute(
            "SELECT * FROM cardio_logs WHERE log_date = ? ORDER BY id", (t,)
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


# --- API: Swimming ---

@app.route("/api/swimming", methods=["GET", "POST"])
def api_swimming():
    conn = get_connection()
    try:
        if request.method == "POST":
            data = request.json
            user = get_user(conn)
            latest = get_latest_weight(conn)
            w = float(data.get("body_weight_kg") or (latest["weight_kg"] if latest else user["current_weight_kg"]))
            mins = float(data["swimming_minutes"])
            intensity = data.get("intensity", "moderate")
            cal = data.get("calories_burned_estimate")
            if cal is None or cal == "":
                cal = estimate_swimming_calories(w, mins, intensity)
            conn.execute(
                """INSERT INTO swimming_logs (log_date, swimming_minutes, intensity,
                   calories_burned_estimate, notes) VALUES (?, ?, ?, ?, ?)""",
                (data.get("log_date", today_iso(request)), mins, intensity, cal, data.get("notes", "")),
            )
            conn.commit()
            export_all_csv()
            return jsonify({"ok": True, "calories_estimate": cal})

        t = request.args.get("date") or today_iso(request)
        rows = conn.execute(
            "SELECT * FROM swimming_logs WHERE log_date = ? ORDER BY id", (t,)
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


# --- API: Food & daily ---

@app.route("/api/food", methods=["GET", "POST"])
def api_food():
    conn = get_connection()
    try:
        if request.method == "POST":
            data = request.json
            t = data.get("log_date", today_iso(request))
            conn.execute(
                """INSERT INTO food_logs (log_date, calories, protein_g, carbs_g, fat_g, water_liters, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET
                   calories=excluded.calories, protein_g=excluded.protein_g,
                   carbs_g=excluded.carbs_g, fat_g=excluded.fat_g,
                   water_liters=excluded.water_liters, notes=excluded.notes""",
                (t, data.get("calories"), data.get("protein_g"), data.get("carbs_g"),
                 data.get("fat_g"), data.get("water_liters"), data.get("notes", "")),
            )
            conn.execute(
                """INSERT INTO daily_logs (log_date, steps, sleep_hours, water_liters, notes)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, log_date) DO UPDATE SET
                   steps=excluded.steps, sleep_hours=excluded.sleep_hours,
                   water_liters=COALESCE(excluded.water_liters, daily_logs.water_liters),
                   notes=CASE WHEN excluded.notes != '' THEN excluded.notes ELSE daily_logs.notes END""",
                (t, data.get("steps"), data.get("sleep_hours"),
                 data.get("water_liters"), data.get("daily_notes", data.get("notes", ""))),
            )
            conn.commit()
            export_all_csv()
            return jsonify({"ok": True})

        t = request.args.get("date") or today_iso(request)
        food = conn.execute("SELECT * FROM food_logs WHERE log_date = ?", (t,)).fetchone()
        daily = conn.execute("SELECT * FROM daily_logs WHERE log_date = ?", (t,)).fetchone()
        return jsonify({
            "food": row_to_dict(food),
            "daily": row_to_dict(daily),
        })
    finally:
        conn.close()


# --- API: Weekly report ---

@app.route("/api/report/weekly")
def api_weekly_report():
    conn = get_connection()
    try:
        days = int(request.args.get("days", 7))
        since = (date.today() - timedelta(days=days)).isoformat()
        t = today_str()

        weights = conn.execute(
            "SELECT weight_kg FROM body_weight WHERE log_date >= ?", (since,)
        ).fetchall()
        avg_w = round(sum(r[0] for r in weights) / len(weights), 2) if weights else None

        workouts = conn.execute(
            "SELECT COUNT(DISTINCT session_date) FROM workout_sessions WHERE session_date >= ?",
            (since,),
        ).fetchone()[0]

        swim = conn.execute(
            "SELECT COALESCE(SUM(swimming_minutes), 0) FROM swimming_logs WHERE log_date >= ?",
            (since,),
        ).fetchone()[0]

        cardio = conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM cardio_logs WHERE log_date >= ?",
            (since,),
        ).fetchone()[0]

        foods = conn.execute(
            "SELECT calories, protein_g FROM food_logs WHERE log_date >= ?", (since,)
        ).fetchall()
        avg_cal = round(sum(r[0] or 0 for r in foods) / len(foods), 1) if foods else None
        avg_prot = round(sum(r[1] or 0 for r in foods) / len(foods), 1) if foods else None

        return jsonify({
            "period_days": days,
            "average_weight": avg_w,
            "total_workouts": workouts,
            "total_swimming_minutes": swim,
            "total_cardio_minutes": cardio,
            "average_calories": avg_cal,
            "average_protein": avg_prot,
        })
    finally:
        conn.close()


# --- CSV & ChatGPT ---

@app.route("/api/export-csv", methods=["POST"])
def api_export_csv():
    path = export_all_csv()
    return jsonify({"ok": True, "path": str(path)})


@app.route("/api/import-csv", methods=["POST"])
def api_import_csv():
    filename = request.json.get("filename", "daily_summary.csv")
    conn = get_connection()
    try:
        ok, msg = import_csv_file(filename, conn)
        if ok:
            export_all_csv()
        return jsonify({"ok": ok, "message": msg})
    finally:
        conn.close()


@app.route("/api/chatgpt-report", methods=["GET"])
def api_chatgpt_report():
    text = generate_chatgpt_report()
    return jsonify({"report": text})


@app.route("/exports/<path:filename>")
def download_export(filename):
    return send_from_directory(
        os.path.join(app.root_path, "exports"), filename, as_attachment=True
    )


# --- PWA static ---

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")


def _running_under_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" and not _running_under_streamlit():
    if not os.path.exists(os.path.join(app.root_path, "gym_tracker.db")):
        init_db()
    else:
        export_all_csv()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
