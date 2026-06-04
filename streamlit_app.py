"""
Streamlit Cloud entry point — mirrors the Flask PWA layout.
Settings → Main file path: streamlit_app.py
"""
from datetime import date
from urllib.parse import quote

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

NAV_ITEMS = [
    ("Home", "🏠", "Home"),
    ("Dashboard", "📊", "Stats"),
    ("Report", "📈", "Report"),
    ("Profile", "👤", "Profile"),
]

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    nav.gym-bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        display: flex;
        flex-direction: row;
        align-items: stretch;
        justify-content: space-around;
        max-width: 540px;
        margin: 0 auto;
        padding: 0.4rem 0.25rem calc(0.55rem + env(safe-area-inset-bottom, 0px));
        background: rgba(14, 18, 26, 0.97);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.45);
        box-sizing: border-box;
    }
    nav.gym-bottom-nav a.gym-nav-item {
        flex: 1 1 0;
        min-width: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.15rem;
        padding: 0.35rem 0.1rem;
        text-decoration: none;
        color: #8b9cb3;
        font-size: 0.58rem;
        font-weight: 600;
        line-height: 1.1;
        text-align: center;
        position: relative;
        -webkit-tap-highlight-color: transparent;
    }
    nav.gym-bottom-nav a.gym-nav-item .gym-nav-icon {
        font-size: 1.15rem;
        line-height: 1;
    }
    nav.gym-bottom-nav a.gym-nav-item.active {
        color: #22c55e;
    }
    nav.gym-bottom-nav a.gym-nav-item.active::before {
        content: '';
        position: absolute;
        top: 0;
        left: 18%;
        right: 18%;
        height: 3px;
        background: #22c55e;
        border-radius: 0 0 3px 3px;
    }

    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], .stDeployButton { display: none !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0a0e14;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,197,94,0.12), transparent);
        color: #f0f4f8;
    }
    .block-container {
        padding-top: 0.25rem !important;
        max-width: 540px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px)) !important;
    }

    .app-topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.65rem 0 0.85rem; margin-bottom: 0.25rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .app-topbar .app-title {
        font-size: 1.05rem; font-weight: 700; letter-spacing: -0.02em; margin: 0;
    }
    .app-topbar .app-date { font-size: 0.72rem; color: #8b9cb3; margin: 0; }

    h1 { font-size: 1.35rem !important; font-weight: 700 !important; letter-spacing: -0.02em; }
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
    .hero h2 { color: #f0f4f8 !important; font-size: 1.5rem !important;
               text-transform: none !important; letter-spacing: -0.03em !important; margin: 0 !important; }
    .hero p { color: rgba(255,255,255,0.8); margin: 0.25rem 0 0; font-size: 0.9rem; }

    .card-box {
        background: #161d27; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 1rem 1.15rem; margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .card-box .section-label {
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #22c55e; margin-bottom: 0.85rem;
    }

    .block-container .stButton > button {
        border-radius: 10px; font-weight: 600; border: none;
        background: linear-gradient(135deg, #16a34a, #22c55e); color: #052e16;
        width: 100%;
    }
    .block-container .stButton > button[kind="secondary"] {
        background: #121820; color: #f0f4f8;
        border: 1px solid rgba(255,255,255,0.08);
    }

    @media (max-width: 480px) {
        .block-container { padding-left: 0.85rem !important; padding-right: 0.85rem !important; }
    }
</style>
""",
    unsafe_allow_html=True,
)

svc.ensure_database()

PAGE_KEYS = [p[0] for p in NAV_ITEMS]

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "lang" not in st.session_state:
    st.session_state.lang = "en"

_nav_qp = st.query_params.get("p")
if _nav_qp:
    _nav_val = _nav_qp[0] if isinstance(_nav_qp, list) else _nav_qp
    if _nav_val in PAGE_KEYS:
        st.session_state.page = _nav_val

today_s = date.today().isoformat()


def nav_bar():
    """Pure HTML bottom bar — avoids Streamlit columns breaking on Cloud/mobile."""
    current = st.session_state.page
    links = []
    for page, icon, short in NAV_ITEMS:
        active = " active" if page == current else ""
        href = f"?p={quote(page)}"
        links.append(
            f'<a class="gym-nav-item{active}" href="{href}">'
            f'<span class="gym-nav-icon">{icon}</span><span>{short}</span></a>'
        )
    st.markdown(
        f'<nav class="gym-bottom-nav" aria-label="Main">{"".join(links)}</nav>',
        unsafe_allow_html=True,
    )


def app_header():
    titles = {
        "Home": "Home",
        "Dashboard": "Dashboard",
        "Report": "Report",
        "Profile": "Profile",
    }
    title = titles.get(st.session_state.page, "Gym Tracker")
    today_label = date.today().strftime("%a, %d %b")
    st.markdown(
        f'<div class="app-topbar">'
        f'<p class="app-title">{title}</p>'
        f'<p class="app-date">{today_label}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def page_home():
    d = svc.get_dashboard(local_date=today_s)
    rest = ' <span style="opacity:0.85">· Rest day</span>' if d["is_rest_day"] else ""
    st.markdown(
        f'<div class="hero"><h2>{d["day_name"]}</h2>'
        f'<p>{d["muscle_group"]}{rest}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-box"><div class="section-label">Quick log</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="card-box"><div class="section-label">Today\'s exercises</div>', unsafe_allow_html=True)
    for p in d["plan"]:
        st.markdown(f"- {p['exercise_name']} · {p['sets_target']}×{p['reps_target']}")
    st.markdown("</div>", unsafe_allow_html=True)


def page_dashboard():
    d = svc.get_dashboard(local_date=today_s)

    c1, c2, c3 = st.columns(3)
    c1.metric("Current", f"{d['current_weight']} kg")
    c2.metric("Goal", f"{d['goal_weight']} kg")
    c3.metric("Progress", f"{d['progress_percent']}%")
    st.progress(d["progress_percent"] / 100)
    st.caption(f"7-day avg: {d['weight_7day_avg'] or '—'} kg · {d['pace_message']}")

    st.markdown('<div class="card-box"><div class="section-label">Today at a glance</div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    r1.metric("Calories", d["calories"] or "—")
    r2.metric("Protein", d["protein"] or "—")
    r3.metric("Deficit", d["estimated_deficit"] or "—")
    r4, r5, r6 = st.columns(3)
    r4.metric("Cardio", f"{int(d['cardio_minutes'])} min")
    r5.metric("Swim", f"{int(d['swimming_minutes'])} min")
    r6.metric("Burned", d["calories_burned_estimate"])
    st.markdown("</div>", unsafe_allow_html=True)

    history, avg7 = svc.get_weight_history()
    if history:
        st.markdown('<div class="card-box"><div class="section-label">Weight chart</div>', unsafe_allow_html=True)
        df = pd.DataFrame(history).sort_values("log_date")
        st.line_chart(df.set_index("log_date")["weight_kg"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card-box"><div class="section-label">Workout</div>', unsafe_allow_html=True)
    data = svc.get_workout_today(local_date=today_s)
    st.caption(f"{data['day_name']} · {data['plan'][0]['muscle_group'] if data['plan'] else ''}")
    for ex in (data["exercises"] or [])[:5]:
        st.markdown(f"- **{ex['exercise_name']}** {ex['sets_target']}×{ex['reps_target']}")
    if data["exercises"] and st.button("Log workout sets →"):
        st.session_state.page = "Profile"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_report():
    r = svc.get_weekly_report(7)
    st.markdown('<div class="card-box"><div class="section-label">Weekly summary</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg weight", f"{r['average_weight'] or '—'} kg")
    c2.metric("Workouts", r["total_workouts"])
    c3.metric("Swim min", int(r["total_swimming_minutes"]))
    c4, c5, c6 = st.columns(3)
    c4.metric("Cardio min", int(r["total_cardio_minutes"]))
    c5.metric("Avg kcal", r["average_calories"] or "—")
    c6.metric("Avg protein", f"{r['average_protein'] or '—'} g")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Export CSV"):
        export_all_csv()
        st.success("CSV updated in exports/")
    if st.button("Generate ChatGPT report"):
        st.text_area("Copy this", generate_chatgpt_report(), height=350)


def page_profile():
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
        label_visibility="collapsed",
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


# --- Render: content first, tab bar last (pinned via JS on Streamlit Cloud) ---
app_header()

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Dashboard":
    page_dashboard()
elif st.session_state.page == "Report":
    page_report()
else:
    page_profile()

nav_bar()
