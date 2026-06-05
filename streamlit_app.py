"""
Streamlit Cloud entry point — mirrors the Flask PWA layout.
Settings → Main file path: streamlit_app.py
"""
import json
from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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

    .gym-nav-hooks-marker { display: none !important; }
    div[data-testid="stVerticalBlock"]:has(.gym-nav-hooks-marker) {
        position: fixed !important;
        left: -9999px !important;
        width: 1px !important;
        height: 1px !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        z-index: -1 !important;
    }

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
        width: 100%;
        padding: 0.4rem 0.15rem calc(0.55rem + env(safe-area-inset-bottom, 0px));
        background: rgba(14, 18, 26, 0.97);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.45);
        box-sizing: border-box;
    }
    nav.gym-bottom-nav button.gym-nav-item {
        flex: 1 1 0;
        min-width: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.15rem;
        padding: 0.35rem 0.05rem;
        border: none;
        background: transparent;
        color: #8b9cb3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.58rem;
        font-weight: 600;
        line-height: 1.1;
        cursor: pointer;
        position: relative;
        -webkit-tap-highlight-color: transparent;
    }
    nav.gym-bottom-nav .gym-nav-icon {
        font-size: 1.15rem;
        line-height: 1;
    }
    nav.gym-bottom-nav button.gym-nav-item.active {
        color: #22c55e;
    }
    nav.gym-bottom-nav button.gym-nav-item.active::before {
        content: '';
        position: absolute;
        top: 0;
        left: 18%;
        right: 18%;
        height: 3px;
        background: #22c55e;
        border-radius: 0 0 3px 3px;
    }

    section.main .block-container {
        transition: opacity 0.12s ease-out;
    }
    .set-last-note {
        color: #38bdf8;
        font-size: 0.72rem;
        margin: -0.15rem 0 0.35rem 0;
        display: block;
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

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "workout_date" not in st.session_state:
    st.session_state.workout_date = date.today()
if "profile_section" not in st.session_state:
    st.session_state.profile_section = "Workout"

today_s = date.today().isoformat()


def nav_bar():
    """HTML tab bar (clean on Cloud) + hidden buttons for smooth in-app navigation."""
    st.markdown('<span class="gym-nav-hooks-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    for page, _icon, _short in NAV_ITEMS:
        if st.button("·", key=f"navhook_{page}"):
            if st.session_state.page != page:
                st.session_state.page = page
                st.rerun()

    current = st.session_state.page
    tabs = []
    for page, icon, short in NAV_ITEMS:
        active = " active" if page == current else ""
        tabs.append(
            f'<button type="button" class="gym-nav-item{active}" data-page="{page}">'
            f'<span class="gym-nav-icon">{icon}</span>'
            f'<span class="gym-nav-label">{short}</span></button>'
        )
    st.markdown(
        f'<nav class="gym-bottom-nav" aria-label="Main">{"".join(tabs)}</nav>',
        unsafe_allow_html=True,
    )

    page_index = json.dumps({p[0]: i for i, p in enumerate(NAV_ITEMS)})
    components.html(
        f"""
<script>
(function () {{
  const doc = window.parent.document;
  const PAGE_INDEX = {page_index};
  function hooks() {{
    const block = doc.querySelector('div[data-testid="stVerticalBlock"]:has(.gym-nav-hooks-marker)');
    return block ? Array.from(block.querySelectorAll("button")) : [];
  }}
  function wire() {{
    doc.querySelectorAll("nav.gym-bottom-nav button.gym-nav-item[data-page]").forEach((tab) => {{
      if (tab.dataset.wired) return;
      tab.dataset.wired = "1";
      tab.addEventListener("click", (e) => {{
        e.preventDefault();
        const page = tab.getAttribute("data-page");
        const idx = PAGE_INDEX[page];
        const btns = hooks();
        if (btns[idx]) btns[idx].click();
      }});
    }});
  }}
  wire();
  setTimeout(wire, 80);
  setTimeout(wire, 400);
  new MutationObserver(wire).observe(doc.body, {{ childList: true, subtree: true }});
}})();
</script>
        """,
        height=0,
    )


def _set_defaults(logged, prev_set):
    kg = float(logged.get("weight_kg") or 0) if logged else 0.0
    reps = int(logged.get("reps") or 0) if logged else 0
    if not logged.get("weight_kg") and prev_set and prev_set.get("weight_kg"):
        kg = float(prev_set["weight_kg"])
    if not logged.get("reps") and prev_set and prev_set.get("reps"):
        reps = int(prev_set["reps"])
    if reps <= 0:
        reps = 12
    return kg, reps


def render_workout_log():
    st.markdown('<div class="card-box"><div class="section-label">Workout log</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        picked = st.date_input(
            "Choose day",
            value=st.session_state.workout_date,
            max_value=date.today(),
            key="workout_date_input",
        )
    with c2:
        if st.button("Today", use_container_width=True, key="workout_today_btn"):
            st.session_state.workout_date = date.today()
            st.rerun()
    st.session_state.workout_date = picked
    workout_d = picked.isoformat()

    data = svc.get_workout_today(local_date=workout_d)
    mg = data["plan"][0]["muscle_group"] if data.get("plan") else "—"
    st.caption(f"{data['day_name']} · {mg} · {workout_d}")

    session_id = data.get("session_id")
    if not session_id:
        if st.button("Start workout for this day", key=f"start_{workout_d}"):
            session_id = svc.ensure_workout_session(local_date=workout_d)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    extra_key = f"extra_exercises_{workout_d}"
    if extra_key not in st.session_state:
        st.session_state[extra_key] = []

    with st.expander("Add exercise to this day"):
        new_name = st.text_input("Exercise name", key=f"new_ex_name_{workout_d}")
        n_sets = st.number_input("Sets", min_value=1, max_value=8, value=3, key=f"new_ex_sets_{workout_d}")
        if st.button("Add exercise", key=f"new_ex_btn_{workout_d}") and new_name.strip():
            entry = {
                "exercise_name": new_name.strip(),
                "sets_target": int(n_sets),
                "reps_target": "12",
                "muscle_group": "Custom",
            }
            names = {e["exercise_name"] for e in st.session_state[extra_key]}
            if entry["exercise_name"] not in names:
                st.session_state[extra_key].append(entry)
            st.rerun()

    exercises = list(data.get("exercises") or [])
    seen = {e["exercise_name"] for e in exercises}
    for ex in st.session_state[extra_key]:
        if ex["exercise_name"] not in seen:
            exercises.append({
                **ex,
                "previous_sets": {},
                "previous_session_date": None,
                "sets_logged": [],
            })

    if not exercises:
        st.info("No exercises for this day. Add one above or pick another date.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for ex in exercises:
        ex_name = ex["exercise_name"]
        target_sets = int(ex.get("sets_target") or 3)
        prev_sets = ex.get("previous_sets") or {}
        prev_date = ex.get("previous_session_date")
        logged_by_num = {s["set_number"]: s for s in (ex.get("sets_logged") or [])}

        with st.expander(f"{ex_name} · {target_sets}×{ex.get('reps_target', '')}", expanded=False):
            if prev_date:
                st.caption(f"Last session: {prev_date}")

            for set_num in range(1, target_sets + 1):
                logged = logged_by_num.get(set_num) or {}
                prev_set = prev_sets.get(set_num)
                if prev_set:
                    st.markdown(
                        f'<span class="set-last-note">Set {set_num} last time: '
                        f'{prev_set.get("weight_kg") or "—"} kg × {prev_set.get("reps") or "—"} reps</span>',
                        unsafe_allow_html=True,
                    )
                kg_def, reps_def = _set_defaults(logged, prev_set)
                ckg, creps, csave = st.columns([2, 2, 1])
                kg = ckg.number_input(
                    f"Set {set_num} kg",
                    min_value=0.0,
                    step=0.5,
                    value=kg_def,
                    key=f"w_{workout_d}_{ex_name}_{set_num}",
                )
                reps = creps.number_input(
                    f"Set {set_num} reps",
                    min_value=0,
                    value=reps_def,
                    key=f"r_{workout_d}_{ex_name}_{set_num}",
                )
                if csave.button("Save", key=f"s_{workout_d}_{ex_name}_{set_num}"):
                    svc.save_workout_set(
                        session_id, ex_name, set_num, kg or None, reps or None, True
                    )
                    st.toast(f"{ex_name} set {set_num} saved")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


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
        st.session_state.profile_section = "Workout"
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

    sections = ["Course plan", "Workout", "Food", "Weight"]
    sec_idx = sections.index(st.session_state.profile_section) if st.session_state.profile_section in sections else 1
    tab = st.radio(
        "Section",
        sections,
        index=sec_idx,
        horizontal=True,
        key="profile_section_radio",
        label_visibility="collapsed",
    )
    st.session_state.profile_section = tab

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
        render_workout_log()

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
