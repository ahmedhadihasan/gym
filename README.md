# Gym Tracker PWA

Personal fat-loss gym tracking app: body weight, workouts, cardio, swimming, nutrition, and CSV export for ChatGPT analysis.

## Tech stack

- Python Flask backend
- SQLite database
- HTML / CSS / JavaScript frontend
- PWA (install on phone home screen)
- Mobile-first dark UI

## Project structure

```
GymSystem/
├── app.py                 # Flask app & API
├── requirements.txt
├── gym_tracker.db         # Created on first run
├── database/
│   ├── schema.sql         # Table definitions
│   └── seed.sql           # User profile + weekly plan
├── utils/
│   ├── db.py              # Database connection
│   ├── met.py             # MET calorie formulas
│   └── csv_export.py      # CSV export/import/report
├── templates/             # HTML pages
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── manifest.json
│   ├── sw.js
│   └── icons/
├── exports/               # Auto-generated CSV files
└── scripts/
    └── generate_icons.py
```

## Installation

```bash
cd GymSystem
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_icons.py
```

## Run

```bash
python app.py
```

Open **http://localhost:5000** on your phone (same Wi‑Fi) or computer.

### Install as PWA

- **iPhone:** Safari → Share → Add to Home Screen  
- **Android:** Chrome → menu → Install app  

## Daily workflow

After each training day, log:

1. Morning body weight (`Weight` tab)
2. Food: calories, protein, carbs, fat (`Food` tab)
3. Water, steps, sleep, notes (`Food` tab)
4. Workout sets with weight & reps (`Workout` tab)
5. Bicycle / cardio minutes (`Cardio` tab)
6. Swimming minutes & intensity (`Swimming` tab)

The **Dashboard** auto-detects weekday and shows today’s gym course.

## CSV files (auto-updated on save)

| File | Purpose |
|------|---------|
| `exports/daily_summary.csv` | Weight, food, water, steps, sleep |
| `exports/workout_log.csv` | Every set logged |
| `exports/cardio_log.csv` | Cardio sessions |
| `exports/swimming_log.csv` | Swimming sessions |
| `exports/weekly_report.csv` | Weekly aggregates |

Use **Report → Export CSV** to refresh all files.

**Import CSV** merges a chosen file back into the database.

**Generate ChatGPT Report** builds a text summary you can paste into ChatGPT.

## Calorie estimates (MET)

`calories = MET × body_weight_kg × hours`

Default MET values are in `utils/met.py`. You can override calories on cardio/swim forms if your machine shows a different number.

## Pre-seeded profile

- Male, 22, 174 cm, 86 kg → goal 82 kg by 2026-07-01  
- Fat loss focus; avoid heavy deadlifts, squats, bent-over rows  
- Full 6-day split + Friday rest (see `database/seed.sql`)

## API endpoints (local)

- `GET /api/dashboard` — today’s summary  
- `GET/POST /api/weight`  
- `GET /api/workout/today`, `POST /api/workout/set`  
- `GET/POST /api/cardio`, `/api/swimming`, `/api/food`  
- `GET /api/report/weekly`  
- `POST /api/export-csv`, `/api/import-csv`  
- `GET /api/chatgpt-report`  

## Reset database

Delete `gym_tracker.db` and restart `python app.py` to recreate schema and seed data.

## Streamlit Cloud

Streamlit Cloud **cannot** run `app.py` (Flask). Use the Streamlit entry point instead:

1. Deploy repo: https://github.com/ahmedhadihasan/gym
2. In app settings → **Main file path**: `streamlit_app.py`
3. Reboot the app

Local Flask/PWA: `python app.py`  
Streamlit UI: `streamlit run streamlit_app.py`
