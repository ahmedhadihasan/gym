"""
Streamlit Cloud entry point — mirrors the Flask PWA layout.
Settings → Main file path: streamlit_app.py
"""
from datetime import date

import pandas as pd
import streamlit as st

import services as svc
from data.course_i18n import LANGS, get_course_plan
from utils.csv_export import export_all_csv, generate_chatgpt_report, import_csv_file
from utils.db import get_connection

st.set_page_config(
    page_title="Gym Tracker",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    .stApp {
        background: #0a0e14;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,197,94,0.12), transparent);
        color: #f0f4f8;
    }
    .block-container { padding-top: 0.5rem; max-width: 540px; padding-bottom: 5rem; }
    h1 { font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    h2, h3 { color: #8b9cb3 !important; font-size: 0.75rem !important;
              text-transform: uppercase; letter-spacing: 0.08em; }
    div[data-testid="stMetric"] {
        background: #121820; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 12px;
    }
    .hero {
        background: linear-gradient(135deg, #0d4f3c, #1e3a5f, #1a1f2e);
        border: 1px solid rgba(34,197,94,0.25);
        border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem;
    }
    .hero h2 { color: #f0f4f8 !important; font-size: 1.4rem !important;
               text-transform: none !important; letter-spacing: -0.03em !important; }
    .hero p { color: rgba(255,255,255,0.8); margin: 0.25rem 0 0; font-size: 0.9rem; }
    .card-box {
        background: #161d27; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 1rem 1.15rem; margin-bottom: 1rem;
    }
    .stButton > button {
        border-radius: 10px; font-weight: 600; border: none;
        background: linear-gradient(135deg, #16a34a, #22c55e); color: #052e16;
    }
    .stButton > button[kind="secondary"] {
        background: #121820; color: #f0f4f8;
        border: 1px solid rgba(255,255,255,0.08);
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] .stButton > button {
        min-height: 52px; font-size: 0.72rem;
    }
    .nav-active button { background: rgba(34,197,94,0.2) !important;
                          color: #22c55e !important;
                          border: 1px solid rgba(34,197,94,0.4) !important; }
    .caption-muted { color: #8b9cb3; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

svc.ensure_database()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "lang" not in st.session_state:
    st.session_state.lang = "en"

today_s = date.today().isoformat()


def nav_bar():
    pages = ["Home", "Dashboard", "Report", "Profile"]
    icons = {"Home": "🏠", "Dashboard": "📊", "Report": "📈", "Profile": "👤"}
    cols = st.columns(4)
    for col, name in zip(cols, pages):
        with col:
            cls = "nav-active" if st.session_state.page == name else ""
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(f"{icons[name]}\n{name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def page_home():
    d = svc.get_dashboard(local_date=today_s)
    st.markdown(
        f'<div class="hero"><h2>{d["day_name"]}</h2>'
        f'<p>{d["muscle_group"]}'
        f'{" · Rest day" if d["is_rest_day"] else ""}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("**QUICK LOG**")
    c1, c2 = st.columns(2)
    with c1:
        w = st.number_input("Weight (kg)", value=float(d["current_weight"] or 86.0), step=0.1, key="qh_w")
        if st.button("Save weight", key="qh_w_btn"):
            svc.save_weight(today_s, w)
            st.success("Saved!")
            st.rerun()
        cal = st.number_input("Calories", value=float(d["calories"] or 0), step=1.0, key="qh_cal")
        if st.button("Save calories", key="qh_cal_btn"):
            food, daily = svc.get_food(today_s)
            food, daily = food or {}, daily or {}
            svc.save_food(today_s, cal, food.get("protein_g"), food.get("carbs_g"),
                          food.get("fat_g"), food.get("water_liters"),
                          daily.get("steps"), daily.get("sleep_hours"), daily.get("notes") or "")
            st.success("Saved!")
            st.rerun()
    with c2:
        prot = st.number_input("Protein (g)", value=float(d["protein"] or 0), step=1.0, key="qh_p")
        if st.button("Save protein", key="qh_p_btn"):
            food, daily = svc.get_food(today_s)
            food, daily = food or {}, daily or {}
            svc.save_food(today_s, food.get("calories"), prot, food.get("carbs_g"),
                          food.get("fat_g"), food.get("water_liters"),
                          daily.get("steps"), daily.get("sleep_hours"), daily.get("notes") or "")
            st.success("Saved!")
            st.rerun()
        bike = st.number_input("Bicycle (min)", min_value=0, value=0, key="qh_bike")
        if st.button("Save bicycle", key="qh_bike_btn") and bike > 0:
            svc.save_cardio(today_s, "bicycle", bike, "moderate")
            st.success("Saved!")
            st.rerun()
        swim = st.number_input("Swim (min)", min_value=0, value=0, key="qh_swim")
        if st.button("Save swim", key="qh_swim_btn") and swim > 0:
            svc.save_swimming(today_s, swim, "moderate")
            st.success("Saved!")
            st.rerun()
        steps = st.number_input("Steps", min_value=0, value=int(d.get("steps") or 0), key="qh_steps")
        if st.button("Save steps", key="qh_steps_btn") and steps > 0:
            food, daily = svc.get_food(today_s)
            food, daily = food or {}, daily or {}
            svc.save_food(today_s, food.get("calories"), food.get("protein_g"), food.get("carbs_g"),
                          food.get("fat_g"), food.get("water_liters"), steps,
                          daily.get("sleep_hours"), daily.get("notes") or "")
            st.success("Saved!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("**TODAY'S EXERCISES**")
    for p in d["plan"]:
        st.markdown(f"- {p['exercise_name']} · {p['sets_target']}×{p['reps_target']}")
    st.markdown("</div>", unsafe_allow_html=True)


def page_dashboard():
    d = svc.get_dashboard(local_date=today_s)
    st.title("Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current", f"{d['current_weight']} kg")
    c2.metric("Goal", f"{d['goal_weight']} kg")
    c3.metric("Progress", f"{d['progress_percent']}%")
    st.progress(d["progress_percent"] / 100)
    st.caption(f"7-day avg: {d['weight_7day_avg'] or '—'} kg · {d['pace_message']}")

    st.markdown("**TODAY AT A GLANCE**")
    r1, r2, r3 = st.columns(3)
    r1.metric("Calories", d["calories"] or "—")
    r2.metric("Protein", d["protein"] or "—")
    r3.metric("Deficit", d["estimated_deficit"] or "—")
    r4, r5, r6 = st.columns(3)
    r4.metric("Cardio", f"{int(d['cardio_minutes'])} min")
    r5.metric("Swim", f"{int(d['swimming_minutes'])} min")
    r6.metric("Burned", d["calories_burned_estimate"])

    history, avg7 = svc.get_weight_history()
    if history:
        st.markdown("**WEIGHT CHART**")
        df = pd.DataFrame(history).sort_values("log_date")
        st.line_chart(df.set_index("log_date")["weight_kg"])

    st.markdown("**WORKOUT**")
    data = svc.get_workout_today(local_date=today_s)
    st.caption(f"{data['day_name']} · {data['plan'][0]['muscle_group'] if data['plan'] else ''}")
    for ex in (data["exercises"] or [])[:5]:
        st.markdown(f"- **{ex['exercise_name']}** {ex['sets_target']}×{ex['reps_target']}")
    if data["exercises"] and st.button("Log workout sets →"):
        st.session_state.page = "Profile"
        st.rerun()


def page_report():
    st.title("Report")
    r = svc.get_weekly_report(7)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg weight", f"{r['average_weight'] or '—'} kg")
    c2.metric("Workouts", r["total_workouts"])
    c3.metric("Swim min", int(r["total_swimming_minutes"]))
    c4, c5, c6 = st.columns(3)
    c4.metric("Cardio min", int(r["total_cardio_minutes"]))
    c5.metric("Avg kcal", r["average_calories"] or "—")
    c6.metric("Avg protein", f"{r['average_protein'] or '—'} g")

    if st.button("Export CSV"):
        export_all_csv()
        st.success("CSV updated in exports/")
    if st.button("Generate ChatGPT report"):
        st.text_area("Copy this", generate_chatgpt_report(), height=350)


def page_profile():
    st.title("Profile")
    conn = get_connection()
    user = svc.get_user(conn)
    conn.close()

    st.markdown(
        f'<div class="hero"><h2>{user.get("name", "User")}</h2>'
        f'<p>Goal {user.get("goal_weight_kg")} kg by {user.get("goal_date", "—")}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**Age** {user.get('age')} · **Height** {user.get('height_cm')} cm · **Focus** {user.get('main_goal')}")
    st.caption(user.get("restrictions") or "")

    tab = st.radio(
        "Section",
        ["Course plan", "Workout", "Food", "Weight"],
        horizontal=True,
        key="profile_section",
    )

    lang = st.selectbox("Course plan language", list(LANGS.keys()),
                        format_func=lambda c: LANGS[c]["label"])

    if tab == "Course plan":
        plan = get_course_plan(lang)
        ui = plan["ui"]
        st.caption(ui["subtitle"])
        for day in plan["days"]:
            with st.expander(f"{day['day_name']} — {day['muscle_group']}"):
                for ex in day["exercises"]:
                    tag = f" ({ex['tag_label']})" if ex.get("tag_label") else ""
                    st.markdown(f"- {ex['name']}{tag} — {ex['detail']}")

    elif tab == "Workout":
        data = svc.get_workout_today(local_date=today_s)
        for ex in data["exercises"]:
            with st.expander(ex["exercise_name"]):
                if ex["last_weight_kg"]:
                    st.caption(f"Last: {ex['last_weight_kg']} kg × {ex['last_reps']}")
                c1, c2, c3 = st.columns([2, 2, 1])
                kg = c1.number_input("kg", min_value=0.0, step=0.5, key=f"pw_{ex['exercise_name']}")
                reps = c2.number_input("reps", min_value=0, value=12, key=f"pr_{ex['exercise_name']}")
                if c3.button("Save", key=f"ps_{ex['exercise_name']}"):
                    svc.save_workout_set(data["session_id"], ex["exercise_name"], 1,
                                         kg or None, reps or None, True)
                    st.success("Saved!")
                    st.rerun()

    elif tab == "Food":
        food, daily = svc.get_food(today_s)
        food, daily = food or {}, daily or {}
        cal = st.number_input("Calories", value=float(food.get("calories") or 0))
        prot = st.number_input("Protein", value=float(food.get("protein_g") or 0))
        carbs = st.number_input("Carbs", value=float(food.get("carbs_g") or 0))
        fat = st.number_input("Fat", value=float(food.get("fat_g") or 0))
        water = st.number_input("Water (L)", value=float(food.get("water_liters") or 0))
        steps = st.number_input("Steps", value=int(daily.get("steps") or 0))
        sleep = st.number_input("Sleep (h)", value=float(daily.get("sleep_hours") or 0))
        notes = st.text_area("Notes", value=food.get("notes") or daily.get("notes") or "")
        if st.button("Save all"):
            svc.save_food(today_s, cal or None, prot or None, carbs or None, fat or None,
                          water or None, steps or None, sleep or None, notes)
            st.success("Saved!")

    elif tab == "Weight":
        w = st.number_input("Weight today (kg)", value=float(user.get("current_weight_kg") or 86.0), step=0.1)
        if st.button("Save weight"):
            svc.save_weight(today_s, w)
            st.success("Saved!")
            st.rerun()
        history, avg7 = svc.get_weight_history()
        st.metric("7-day avg", f"{avg7 or '—'} kg")
        if history:
            df = pd.DataFrame(history).sort_values("log_date")
            st.line_chart(df.set_index("log_date")["weight_kg"])

    st.markdown("---")
    st.caption("Streamlit Cloud · For the full PWA with phone footer, run Flask locally: python app.py")


# --- Render ---
st.caption(date.today().strftime("%A, %d %b %Y"))
nav_bar()

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Dashboard":
    page_dashboard()
elif st.session_state.page == "Report":
    page_report()
else:
    page_profile()
