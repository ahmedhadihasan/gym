-- Gym Tracker SQLite Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT 'User',
    gender TEXT,
    age INTEGER,
    height_cm REAL,
    current_weight_kg REAL,
    goal_weight_kg REAL,
    goal_date TEXT,
    main_goal TEXT,
    restrictions TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS weekly_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    muscle_group TEXT,
    exercise_name TEXT NOT NULL,
    sets_target INTEGER,
    reps_target TEXT,
    sort_order INTEGER DEFAULT 0,
    is_warmup INTEGER DEFAULT 0,
    is_optional INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS exercise_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT UNIQUE NOT NULL,
    muscle_group TEXT,
    default_sets INTEGER,
    default_reps TEXT
);

CREATE TABLE IF NOT EXISTS body_weight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    log_date TEXT NOT NULL,
    weight_kg REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, log_date)
);

CREATE TABLE IF NOT EXISTS workout_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    session_date TEXT NOT NULL,
    day_name TEXT,
    muscle_group TEXT,
    completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS workout_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    set_number INTEGER NOT NULL,
    weight_kg REAL,
    reps INTEGER,
    completed INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES workout_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cardio_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    log_date TEXT NOT NULL,
    cardio_type TEXT NOT NULL,
    duration_minutes REAL DEFAULT 0,
    intensity TEXT DEFAULT 'moderate',
    calories_burned_estimate REAL,
    source TEXT DEFAULT 'manual',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS swimming_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    log_date TEXT NOT NULL,
    swimming_minutes REAL DEFAULT 0,
    intensity TEXT DEFAULT 'moderate',
    calories_burned_estimate REAL,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    log_date TEXT NOT NULL,
    calories REAL,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    water_liters REAL,
    notes TEXT,
    UNIQUE(user_id, log_date)
);

CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    log_date TEXT NOT NULL,
    steps INTEGER,
    sleep_hours REAL,
    water_liters REAL,
    notes TEXT,
    UNIQUE(user_id, log_date)
);

CREATE INDEX IF NOT EXISTS idx_body_weight_date ON body_weight(log_date);
CREATE INDEX IF NOT EXISTS idx_workout_sessions_date ON workout_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_cardio_date ON cardio_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_swimming_date ON swimming_logs(log_date);
