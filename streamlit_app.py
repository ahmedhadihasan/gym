"""
Streamlit Cloud entry point — mirrors the Flask PWA layout.
Settings → Main file path: streamlit_app.py
"""
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
    ("Home", "🏠"),
    ("Dashboard", "📊"),
    ("Report", "📈"),
    ("Profile", "👤"),
]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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
        padding-bottom: calc(78px + env(safe-area-inset-bottom, 0px)) !important;
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

    .stButton > button:not([data-testid*="nav_"]) {
        border-radius: 10px; font-weight: 600; border: none;
        background: linear-gradient(135deg, #16a34a, #22c55e); color: #052e16;
        width: 100%;
    }
    .stButton > button[kind="secondary"]:not([data-testid*="nav_"]) {
        background: #121820; color: #f0f4f8;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* Bottom tab bar — works locally + on Streamlit Cloud (see #gym-nav-fixed-root) */
    #gym-nav-fixed-root {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        margin: 0 !important;
        padding: 0.35rem 0.5rem calc(0.45rem + env(safe-area-inset-bottom, 0px)) !important;
        background: rgba(14, 18, 26, 0.96) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.45);
    }
    #gym-nav-fixed-root [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        max-width: 540px !important;
        margin: 0 auto !important;
        gap: 0 !important;
    }
    #gym-nav-fixed-root [data-testid="column"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 2px !important;
    }
    #gym-nav-fixed-root [data-testid="stRadio"] {
        max-width: 540px;
        margin: 0 auto;
    }
    #gym-nav-fixed-root [data-testid="stRadio"] > div,
    #gym-nav-fixed-root [data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-around !important;
        width: 100% !important;
        gap: 0 !important;
    }
    #gym-nav-fixed-root [data-testid="stRadio"] label {
        flex: 1 1 0 !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0.35rem 0.15rem !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.62rem !important;
        font-weight: 600 !important;
        color: #8b9cb3 !important;
        white-space: pre-line !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }
    #gym-nav-fixed-root [data-testid="stRadio"] label:has(input:checked) {
        color: #22c55e !important;
    }
    #gym-nav-fixed-root .stButton > button {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        min-height: 52px !important;
        background: transparent !important;
        color: #8b9cb3 !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.62rem !important;
        white-space: pre-line !important;
    }
    @media (max-width: 480px) {
        .block-container { padding-left: 0.85rem !important; padding-right: 0.85rem !important; }
    }
</style>
""", unsafe_allow_html=True)

svc.ensure_database()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "lang" not in st.session_state:
    st.session_state.lang = "en"

today_s = date.today().isoformat()


PAGE_NAMES = [name for name, _ in NAV_ITEMS]
PAGE_ICONS = dict(NAV_ITEMS)


def _nav_label(name: str) -> str:
    return f"{PAGE_ICONS[name]}\n{name}"


def nav_bar():
    """Horizontal radio tab bar — stays in one row on mobile (unlike 4 st.buttons in columns)."""
    st.markdown('<div id="gym-bottom-nav-anchor" hidden></div>', unsafe_allow_html=True)
    idx = PAGE_NAMES.index(st.session_state.page) if st.session_state.page in PAGE_NAMES else 0
    selected = st.radio(
        "App navigation",
        PAGE_NAMES,
        index=idx,
        horizontal=True,
        label_visibility="collapsed",
        format_func=_nav_label,
    )
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()


def pin_bottom_nav():
    """Streamlit Cloud often splits anchor & radio into sibling blocks; CSS :has() then fails."""
    components.html(
        """
<script>
(function () {
  const doc = window.parent.document;

  function findNavRoot(anchor) {
    let block = anchor.closest("[data-testid='stVerticalBlock']");
    if (!block) return null;
    if (block.querySelector("[data-testid='stRadio']")) return block;
    let sib = block;
    for (let i = 0; i < 8; i++) {
      sib = sib.nextElementSibling;
      if (!sib) break;
      if (sib.querySelector("[data-testid='stRadio']")) return sib;
    }
    return block;
  }

  function apply() {
    const anchor = doc.getElementById("gym-bottom-nav-anchor");
    if (!anchor) return;
    const anchorBlock = anchor.closest("[data-testid='stVerticalBlock']");
    const root = findNavRoot(anchor);
    if (!root) return;

    if (anchorBlock && anchorBlock !== root) {
      anchorBlock.style.cssText = "height:0!important;margin:0!important;padding:0!important;border:none!important;overflow:hidden!important;";
    }

    root.id = "gym-nav-fixed-root";

    const row = root.querySelector("[data-testid='stHorizontalBlock']");
    if (row) {
      row.style.display = "flex";
      row.style.flexDirection = "row";
      row.style.flexWrap = "nowrap";
      root.querySelectorAll("[data-testid='column']").forEach((c) => {
        c.style.flex = "1 1 0";
        c.style.minWidth = "0";
      });
    }
    const radio = root.querySelector("[data-testid='stRadio']");
    if (radio) {
      const group = radio.querySelector("[role='radiogroup']") || radio.firstElementChild;
      if (group) {
        group.style.display = "flex";
        group.style.flexDirection = "row";
        group.style.flexWrap = "nowrap";
        group.style.justifyContent = "space-around";
        group.style.width = "100%";
      }
    }
  }

  apply();
  setTimeout(apply, 80);
  setTimeout(apply, 400);
  new MutationObserver(apply).observe(doc.body, { childList: true, subtree: true });
})();
</script>
        """,
        height=0,
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
pin_bottom_nav()
