-- Default user profile
INSERT OR IGNORE INTO users (id, name, gender, age, height_cm, current_weight_kg, goal_weight_kg, goal_date, main_goal, restrictions)
VALUES (1, 'Ahmed', 'Male', 22, 174, 86, 82, '2026-07-01', 'Fat loss', 'Avoid heavy deadlifts, heavy squats, heavy bent-over rows');

-- Saturday: Chest + Triceps (0=Monday in Python weekday? Python: Mon=0, Sat=5, Sun=6)
-- Using Python weekday: Monday=0 ... Sunday=6
-- Saturday = 5, Sunday = 6, Monday = 0, Tuesday = 1, Wednesday = 2, Thursday = 3, Friday = 4

DELETE FROM weekly_plan;

-- Saturday (5) - Chest + Triceps
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(5, 'Saturday', 'Chest + Triceps', 'Bicycle', 1, '20 min', 1, 1),
(5, 'Saturday', 'Chest + Triceps', 'Chest Press', 4, '12', 2, 0),
(5, 'Saturday', 'Chest + Triceps', 'Incline Chest Press', 4, '12', 3, 0),
(5, 'Saturday', 'Chest + Triceps', 'Pec Deck Fly', 3, '15', 4, 0),
(5, 'Saturday', 'Chest + Triceps', 'Triceps Pushdown', 3, '12', 5, 0),
(5, 'Saturday', 'Chest + Triceps', 'Overhead Triceps Extension', 3, '12', 6, 0),
(5, 'Saturday', 'Chest + Triceps', 'Incline Walk', 1, '15 min', 7, 0),
(5, 'Saturday', 'Chest + Triceps', 'Swimming', 1, '20-30 min', 8, 0);

-- Sunday (6) - Back + Biceps
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(6, 'Sunday', 'Back + Biceps', 'Bicycle', 1, '20 min', 1, 1),
(6, 'Sunday', 'Back + Biceps', 'Lat Pulldown', 4, '12', 2, 0),
(6, 'Sunday', 'Back + Biceps', 'Seated Row', 4, '12', 3, 0),
(6, 'Sunday', 'Back + Biceps', 'Low Row', 3, '12', 4, 0),
(6, 'Sunday', 'Back + Biceps', 'Biceps Curl', 3, '12', 5, 0),
(6, 'Sunday', 'Back + Biceps', 'Hammer Curl', 3, '12', 6, 0),
(6, 'Sunday', 'Back + Biceps', 'Elliptical', 1, '15 min', 7, 0),
(6, 'Sunday', 'Back + Biceps', 'Swimming', 1, '20-30 min', 8, 0);

-- Monday (0) - Legs + Core
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(0, 'Monday', 'Legs + Core', 'Bicycle', 1, '20 min', 1, 1),
(0, 'Monday', 'Legs + Core', 'Leg Press', 4, '12', 2, 0),
(0, 'Monday', 'Legs + Core', 'Leg Curl', 4, '12', 3, 0),
(0, 'Monday', 'Legs + Core', 'Leg Extension', 4, '12', 4, 0),
(0, 'Monday', 'Legs + Core', 'Calf Raise', 4, '15', 5, 0),
(0, 'Monday', 'Legs + Core', 'Plank', 3, 'hold', 6, 0),
(0, 'Monday', 'Legs + Core', 'Bird Dog', 3, '10', 7, 0),
(0, 'Monday', 'Legs + Core', 'Dead Bug', 3, '10', 8, 0),
(0, 'Monday', 'Legs + Core', 'Swimming', 1, '20 min', 9, 0);

-- Tuesday (1) - Shoulders + Traps
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(1, 'Tuesday', 'Shoulders + Traps', 'Bicycle', 1, '20 min', 1, 1),
(1, 'Tuesday', 'Shoulders + Traps', 'Shoulder Press', 4, '12', 2, 0),
(1, 'Tuesday', 'Shoulders + Traps', 'Lateral Raise', 4, '15', 3, 0),
(1, 'Tuesday', 'Shoulders + Traps', 'Rear Delt', 4, '15', 4, 0),
(1, 'Tuesday', 'Shoulders + Traps', 'Shrugs', 3, '15', 5, 0),
(1, 'Tuesday', 'Shoulders + Traps', 'Stair Climber', 1, '10-15 min', 6, 0),
(1, 'Tuesday', 'Shoulders + Traps', 'Swimming', 1, '20-30 min', 7, 0);

-- Wednesday (2) - Chest + Back
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(2, 'Wednesday', 'Chest + Back', 'Bicycle', 1, '20 min', 1, 1),
(2, 'Wednesday', 'Chest + Back', 'Chest Press', 4, '12', 2, 0),
(2, 'Wednesday', 'Chest + Back', 'Incline Chest Press', 3, '12', 3, 0),
(2, 'Wednesday', 'Chest + Back', 'Lat Pulldown', 4, '12', 4, 0),
(2, 'Wednesday', 'Chest + Back', 'Seated Row', 4, '12', 5, 0),
(2, 'Wednesday', 'Chest + Back', 'Elliptical', 1, '15 min', 6, 0),
(2, 'Wednesday', 'Chest + Back', 'Swimming', 1, '20-30 min', 7, 0);

-- Thursday (3) - Arms + Core
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_warmup) VALUES
(3, 'Thursday', 'Arms + Core', 'Bicycle', 1, '20 min', 1, 1),
(3, 'Thursday', 'Arms + Core', 'Biceps Curl', 4, '12', 2, 0),
(3, 'Thursday', 'Arms + Core', 'Hammer Curl', 3, '12', 3, 0),
(3, 'Thursday', 'Arms + Core', 'Triceps Pushdown', 4, '12', 4, 0),
(3, 'Thursday', 'Arms + Core', 'Overhead Extension', 3, '12', 5, 0),
(3, 'Thursday', 'Arms + Core', 'Plank', 3, 'hold', 6, 0),
(3, 'Thursday', 'Arms + Core', 'Bird Dog', 3, '10', 7, 0),
(3, 'Thursday', 'Arms + Core', 'Dead Bug', 3, '10', 8, 0),
(3, 'Thursday', 'Arms + Core', 'Incline Walk', 1, '15-20 min', 9, 0),
(3, 'Thursday', 'Arms + Core', 'Swimming', 1, '20-30 min', 10, 0);

-- Friday (4) - Rest
INSERT INTO weekly_plan (day_of_week, day_name, muscle_group, exercise_name, sets_target, reps_target, sort_order, is_optional) VALUES
(4, 'Friday', 'Rest', 'Walking', 1, '6000-10000 steps', 1, 1),
(4, 'Friday', 'Rest', 'Easy Swimming', 1, 'optional', 2, 1);

-- Exercise templates
INSERT OR IGNORE INTO exercise_templates (exercise_name, muscle_group, default_sets, default_reps) VALUES
('Chest Press', 'Chest', 4, '12'),
('Incline Chest Press', 'Chest', 4, '12'),
('Pec Deck Fly', 'Chest', 3, '15'),
('Lat Pulldown', 'Back', 4, '12'),
('Seated Row', 'Back', 4, '12'),
('Low Row', 'Back', 3, '12'),
('Leg Press', 'Legs', 4, '12'),
('Leg Curl', 'Legs', 4, '12'),
('Leg Extension', 'Legs', 4, '12'),
('Calf Raise', 'Legs', 4, '15'),
('Shoulder Press', 'Shoulders', 4, '12'),
('Lateral Raise', 'Shoulders', 4, '15'),
('Rear Delt', 'Shoulders', 4, '15'),
('Shrugs', 'Traps', 3, '15'),
('Biceps Curl', 'Biceps', 3, '12'),
('Hammer Curl', 'Biceps', 3, '12'),
('Triceps Pushdown', 'Triceps', 3, '12'),
('Overhead Triceps Extension', 'Triceps', 3, '12'),
('Overhead Extension', 'Triceps', 3, '12');
