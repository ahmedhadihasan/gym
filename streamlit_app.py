"""
Streamlit Cloud entry point.
In Streamlit Cloud settings, set Main file path to: streamlit_app.py
"""
from datetime import date

import streamlit as st

import services as svc
from data.course_i18n import LANGS, get_course_plan
from utils.csv_export import export_all_csv, generate_chatgpt_report, import_csv_file

st.set_page_config(
    page_title="Gym Tracker",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .block-container { padding-top: 1rem; max-width: 480px; }
    div[data-testid="stMetric"] {
        background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 12px;
    }
    h1, h2, h3, p, label { color: #e6edf3 !important; }
    .stButton > button {
        width: 100%; min-height: 48px; border-radius: 12px;
        background: #2ea043; color: white; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

svc.ensure_database()

if "lang" not in st.session_state:
    st.session_state.lang = "en"

lang_options = {code: LANGS[code]["label"] for code in LANGS}
st.session_state.lang = st.sidebar.selectbox(
    "Language / زمان / اللغة",
    options=list(lang_options.keys()),
    format_func=lambda c: lang_options[c],
    index=list(lang_options.keys()).index(st.session_state.lang),
    key="lang_select",
)
lang = st.session_state.lang

today = st.sidebar.date_input("Today’s date", value=date.today())
today_s = today.isoformat()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Course Plan", "Weight", "Workout", "Cardio", "Swimming", "Food", "Report"],
)

if menu == "Dashboard":
    st.title("Dashboard")
    d = svc.get_dashboard(local_date=today_s)
    st.subheader(f"{d['day_name']} — {d['muscle_group']}")
    if d["is_rest_day"]:
        st.info("Rest day: walking 6k–10k steps, optional easy swim.")

    st.markdown("**Today's plan**")
    for p in d["plan"]:
        st.checkbox(f"{p['exercise_name']} — {p['sets_target']}×{p['reps_target']}", value=False, key=f"plan_{p['id']}")

    c1, c2 = st.columns(2)
    c1.metric("Weight", f"{d['current_weight']} kg")
    c2.metric("Goal", f"{d['goal_weight']} kg")
    st.progress(d["progress_percent"] / 100, text=f"{d['progress_percent']}% to goal")
    st.caption(f"7-day avg: {d['weight_7day_avg'] or '—'} kg · {d['pace_message']}")

    c3, c4, c5 = st.columns(3)
    c3.metric("Calories", d["calories"] or "—")
    c4.metric("Protein", f"{d['protein'] or '—'} g")
    c5.metric("Deficit", d["estimated_deficit"] or "—")
    c6, c7, c8 = st.columns(3)
    c6.metric("Cardio", f"{int(d['cardio_minutes'])} min")
    c7.metric("Swim", f"{int(d['swimming_minutes'])} min")
    c8.metric("Burn est.", d["calories_burned_estimate"])

elif menu == "Course Plan":
    plan = get_course_plan(lang)
    ui = plan["ui"]
    dir_attr = 'dir="rtl"' if plan["dir"] == "rtl" else ""
    st.markdown(f'<div {dir_attr}>', unsafe_allow_html=True)
    st.title(ui["page_title"])
    st.caption(ui["subtitle"])
    st.markdown(f"#### {ui['nutrition_title']}")
    st.markdown(
        f"- {ui['nutrition_cal']}\n- {ui['nutrition_protein']}\n"
        f"- {ui['nutrition_water']}\n- {ui['nutrition_steps']}\n\n*{ui['rest_note']}*"
    )
    for day in plan["days"]:
        with st.expander(f"{day['day_name']} — {day['muscle_group']}", expanded=not day["is_rest"]):
            st.caption(day["summary"])
            if day["is_rest"]:
                st.info(ui["friday_rest"])
            lines = []
            for ex in day["exercises"]:
                tag = f" ({ex['tag_label']})" if ex.get("tag_label") else ""
                lines.append(f"- **{ex['name']}**{tag} — {ex['detail']}")
            st.markdown("\n".join(lines))
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Weight":
    st.title("Body Weight")
    log_date = st.date_input("Date", value=date.today())
    log_date_s = log_date.isoformat()
    weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0, step=0.1, value=86.0)
    if st.button("Save weight"):
        svc.save_weight(log_date_s, weight)
        st.success("Saved!")
        st.rerun()
    history, avg7 = svc.get_weight_history()
    st.metric("7-day average", f"{avg7 or '—'} kg")
    if history:
        import pandas as pd
        df = pd.DataFrame(history).sort_values("log_date")
        st.line_chart(df.set_index("log_date")["weight_kg"])
        st.dataframe(history[:14], use_container_width=True)

elif menu == "Workout":
    st.title("Workout")
    data = svc.get_workout_today(local_date=today_s)
    st.subheader(f"{data['day_name']}")
    if not data["exercises"]:
        st.info("Rest day or no weight exercises today.")
    for ex in data["exercises"]:
        with st.expander(f"{ex['exercise_name']} — target {ex['sets_target']}×{ex['reps_target']}", expanded=True):
            if ex["last_weight_kg"]:
                st.caption(f"Last: {ex['last_weight_kg']} kg × {ex['last_reps']} reps")
            notes = st.text_input("Notes", key=f"notes_{ex['exercise_name']}")
            for s in range(1, (ex["sets_target"] or 3) + 1):
                logged = next((x for x in ex["sets_logged"] if x["set_number"] == s), {})
                c1, c2, c3 = st.columns([2, 2, 1])
                w = c1.number_input(
                    f"Set {s} kg",
                    value=float(logged.get("weight_kg") or 0.0),
                    min_value=0.0, step=0.5, key=f"w_{ex['exercise_name']}_{s}",
                )
                r = c2.number_input("Reps", value=int(logged.get("reps") or 12), min_value=0, key=f"r_{ex['exercise_name']}_{s}")
                done = c3.checkbox("Done", value=bool(logged.get("completed")), key=f"d_{ex['exercise_name']}_{s}")
                if st.button(f"Save set {s}", key=f"save_{ex['exercise_name']}_{s}"):
                    svc.save_workout_set(
                        data["session_id"], ex["exercise_name"], s,
                        w if w > 0 else None, r if r > 0 else None, done, notes,
                    )
                    st.success(f"Set {s} saved")
                    st.rerun()

elif menu == "Cardio":
    st.title("Cardio")
    log_date = st.date_input("Date").isoformat()
    ctype = st.selectbox("Type", ["bicycle", "treadmill", "elliptical", "stair_climber", "walking"])
    mins = st.number_input("Minutes", min_value=0, value=20)
    intensity = st.selectbox("Intensity", ["easy", "moderate", "hard"])
    steps = st.number_input("Steps (if walking)", min_value=0, value=0)
    cal = st.number_input("Calories override (0 = auto)", min_value=0.0, value=0.0)
    notes = st.text_area("Notes")
    if st.button("Save cardio"):
        c = svc.save_cardio(
            log_date, ctype, mins, intensity,
            cal if cal > 0 else None, notes, steps if steps > 0 else None,
        )
        st.success(f"Saved · ~{c} kcal")

elif menu == "Swimming":
    st.title("Swimming")
    log_date = st.date_input("Date").isoformat()
    mins = st.number_input("Minutes", min_value=0, value=25)
    intensity = st.selectbox("Intensity", ["easy", "moderate", "hard"])
    cal = st.number_input("Calories override (0 = auto)", min_value=0.0, value=0.0)
    notes = st.text_area("Notes")
    if st.button("Save swimming"):
        c = svc.save_swimming(log_date, mins, intensity, cal if cal > 0 else None, notes)
        st.success(f"Saved · ~{c} kcal")

elif menu == "Food":
    st.title("Food & Daily")
    log_date = st.date_input("Date").isoformat()
    food, daily = svc.get_food(log_date)
    food = food or {}
    daily = daily or {}
    cal = st.number_input("Calories", value=float(food.get("calories") or 0), min_value=0.0)
    prot = st.number_input("Protein (g)", value=float(food.get("protein_g") or 0), min_value=0.0)
    carbs = st.number_input("Carbs (g)", value=float(food.get("carbs_g") or 0), min_value=0.0)
    fat = st.number_input("Fat (g)", value=float(food.get("fat_g") or 0), min_value=0.0)
    water = st.number_input("Water (L)", value=float(food.get("water_liters") or daily.get("water_liters") or 0), min_value=0.0)
    steps = st.number_input("Steps", value=int(daily.get("steps") or 0), min_value=0)
    sleep = st.number_input("Sleep (hours)", value=float(daily.get("sleep_hours") or 0), min_value=0.0)
    notes = st.text_area("Notes", value=food.get("notes") or daily.get("notes") or "")
    if st.button("Save daily log"):
        svc.save_food(
            log_date,
            cal or None, prot or None, carbs or None, fat or None, water or None,
            steps or None, sleep or None, notes,
        )
        st.success("Saved!")

elif menu == "Report":
    st.title("Weekly Report")
    r = svc.get_weekly_report(7)
    c1, c2 = st.columns(2)
    c1.metric("Avg weight", f"{r['average_weight'] or '—'} kg")
    c2.metric("Workouts", r["total_workouts"])
    c3, c4 = st.columns(2)
    c3.metric("Cardio min", int(r["total_cardio_minutes"]))
    c4.metric("Swim min", int(r["total_swimming_minutes"]))
    c5, c6 = st.columns(2)
    c5.metric("Avg calories", r["average_calories"] or "—")
    c6.metric("Avg protein", f"{r['average_protein'] or '—'} g")

    st.divider()
    if st.button("Export CSV"):
        export_all_csv()
        st.success("CSV files updated in exports/")
    fname = st.selectbox("Import file", [
        "daily_summary.csv", "workout_log.csv", "cardio_log.csv", "swimming_log.csv",
    ])
    if st.button("Import CSV"):
        from utils.db import get_connection
        conn = get_connection()
        ok, msg = import_csv_file(fname, conn)
        conn.close()
        st.success(msg) if ok else st.error(msg)
    if st.button("Generate ChatGPT Report"):
        st.text_area("Copy this report", generate_chatgpt_report(), height=400)

st.sidebar.caption("Streamlit Cloud · Data resets on redeploy unless you add persistent storage.")
