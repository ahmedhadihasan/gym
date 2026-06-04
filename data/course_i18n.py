"""Full weekly course plan — English, Arabic, Kurdish Sorani."""

LANGS = {
    "en": {"label": "English", "dir": "ltr", "locale": "en"},
    "ar": {"label": "العربية", "dir": "rtl", "locale": "ar"},
    "ku": {"label": "کوردی (سۆرانی)", "dir": "rtl", "locale": "ckb"},
}

# Display order: Saturday → Friday (training week)
DAY_ORDER = [5, 6, 0, 1, 2, 3, 4]

UI = {
    "en": {
        "page_title": "Course Plan",
        "language": "Language",
        "subtitle": "Fat-loss program · avoid heavy deadlifts, squats & bent-over rows",
        "nutrition_title": "Daily nutrition targets",
        "nutrition_cal": "Calories: 1700–1900 kcal",
        "nutrition_protein": "Protein: 150–180 g",
        "nutrition_water": "Water: 3–4 liters",
        "nutrition_steps": "Steps: 7000–10000",
        "rest_note": "No cheat day",
        "optional": "Optional",
        "warmup": "Warm-up",
        "sets_reps": "Sets × Reps",
        "duration": "Duration",
        "friday_rest": "Rest day — light activity only",
    },
    "ar": {
        "page_title": "خطة البرنامج",
        "language": "اللغة",
        "subtitle": "برنامج حرق دهون · تجنب الرفعة الميتة الثقيلة، السكوات الثقيلة، والتجديف المنحني الثقيل",
        "nutrition_title": "أهداف التغذية اليومية",
        "nutrition_cal": "السعرات: 1700–1900",
        "nutrition_protein": "البروتين: 150–180 غ",
        "nutrition_water": "الماء: 3–4 لتر",
        "nutrition_steps": "الخطوات: 7000–10000",
        "rest_note": "بدون يوم غش",
        "optional": "اختياري",
        "warmup": "إحماء",
        "sets_reps": "مجموعات × تكرارات",
        "duration": "المدة",
        "friday_rest": "يوم راحة — نشاط خفيف فقط",
    },
    "ku": {
        "page_title": "پلانی ڕاهێنان",
        "language": "زمان",
        "subtitle": "بەرنامەی کەمکردنەوەی چڕی · دووربکەوە لە deadlift قورس، squat قورس، و bent-over row قورس",
        "nutrition_title": "ئامانجی خۆراکی ڕۆژانە",
        "nutrition_cal": "کالۆری: 1700–1900",
        "nutrition_protein": "پرۆتین: 150–180 گرام",
        "nutrition_water": "ئاو: 3–4 لیتر",
        "nutrition_steps": "هەنگاو: 7000–10000",
        "rest_note": "بێ ڕۆژی چیت",
        "optional": "ئارەزوومەندانە",
        "warmup": "گەرمکردنەوە",
        "sets_reps": "سیت × دووبارە",
        "duration": "ماوە",
        "friday_rest": "ڕۆژی پشوو — چالاکی سووک",
    },
}

# day_of_week → lang → day content
PLAN = {
    5: {
        "en": {
            "day_name": "Saturday",
            "muscle_group": "Chest + Triceps",
            "summary": "Chest and triceps focus with cardio and swimming.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Chest Press", "detail": "4 × 12"},
                {"name": "Incline Chest Press", "detail": "4 × 12"},
                {"name": "Pec Deck Fly", "detail": "3 × 15"},
                {"name": "Triceps Pushdown", "detail": "3 × 12"},
                {"name": "Overhead Triceps Extension", "detail": "3 × 12"},
                {"name": "Incline Walk", "detail": "15 min", "tag": "optional"},
                {"name": "Swimming", "detail": "20–30 min"},
            ],
        },
        "ar": {
            "day_name": "السبت",
            "muscle_group": "صدر + ترايسبس",
            "summary": "تركيز على الصدر والترايسبس مع كارديو وسباحة.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "ضغط صدر", "detail": "4 × 12"},
                {"name": "ضغط صدر مائل", "detail": "4 × 12"},
                {"name": "فراشة الصدر (بيك ديك)", "detail": "3 × 15"},
                {"name": "ترايسبس بول داون", "detail": "3 × 12"},
                {"name": "تمديد ترايسبس فوق الرأس", "detail": "3 × 12"},
                {"name": "مشي على منحدر", "detail": "15 دقيقة", "tag": "optional"},
                {"name": "سباحة", "detail": "20–30 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "شەممە",
            "muscle_group": "سینگ + ترایسپس",
            "summary": "تەرکیز لەسەر سینگ و ترایسپس لەگەڵ کاردیۆ و مەلەکردن.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "پرسی سینگ", "detail": "4 × 12"},
                {"name": "پرسی سینگی لار", "detail": "4 × 12"},
                {"name": "پەروازەی سینگ (پێک دەک)", "detail": "3 × 15"},
                {"name": "ترایسپس پوش داون", "detail": "3 × 12"},
                {"name": "درێژکردنەوەی ترایسپس سەرەوە", "detail": "3 × 12"},
                {"name": "پیاسەی لار", "detail": "15 خولەک", "tag": "optional"},
                {"name": "مەلەکردن", "detail": "20–30 خولەک"},
            ],
        },
    },
    6: {
        "en": {
            "day_name": "Sunday",
            "muscle_group": "Back + Biceps",
            "summary": "Back and biceps — no heavy bent-over rows.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Lat Pulldown", "detail": "4 × 12"},
                {"name": "Seated Row", "detail": "4 × 12"},
                {"name": "Low Row", "detail": "3 × 12"},
                {"name": "Biceps Curl", "detail": "3 × 12"},
                {"name": "Hammer Curl", "detail": "3 × 12"},
                {"name": "Elliptical", "detail": "15 min", "tag": "optional"},
                {"name": "Swimming", "detail": "20–30 min"},
            ],
        },
        "ar": {
            "day_name": "الأحد",
            "muscle_group": "ظهر + بايسبس",
            "summary": "ظهر وبايسبس — بدون تجديف منحني ثقيل.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "سحب علوي (لات)", "detail": "4 × 12"},
                {"name": "تجديف جالس", "detail": "4 × 12"},
                {"name": "تجديف منخفض", "detail": "3 × 12"},
                {"name": "بايسبس", "detail": "3 × 12"},
                {"name": "هامر كيرل", "detail": "3 × 12"},
                {"name": "جهاز بيضاوي", "detail": "15 دقيقة", "tag": "optional"},
                {"name": "سباحة", "detail": "20–30 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "یەکشەممە",
            "muscle_group": "پشت + بایسپس",
            "summary": "پشت و بایسپس — بە bent-over row قورس.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "لاٹ پولداون", "detail": "4 × 12"},
                {"name": "ڕۆی دانیشتوو", "detail": "4 × 12"},
                {"name": "ڕۆی نزم", "detail": "3 × 12"},
                {"name": "بایسپس کەرڵ", "detail": "3 × 12"},
                {"name": "هامەر کەرڵ", "detail": "3 × 12"},
                {"name": "ئەلپتیکال", "detail": "15 خولەک", "tag": "optional"},
                {"name": "مەلەکردن", "detail": "20–30 خولەک"},
            ],
        },
    },
    0: {
        "en": {
            "day_name": "Monday",
            "muscle_group": "Legs + Core",
            "summary": "Leg machines and core — no heavy squats.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Leg Press", "detail": "4 × 12"},
                {"name": "Leg Curl", "detail": "4 × 12"},
                {"name": "Leg Extension", "detail": "4 × 12"},
                {"name": "Calf Raise", "detail": "4 × 15"},
                {"name": "Plank", "detail": "3 sets hold"},
                {"name": "Bird Dog", "detail": "3 × 10"},
                {"name": "Dead Bug", "detail": "3 × 10"},
                {"name": "Swimming", "detail": "20 min"},
            ],
        },
        "ar": {
            "day_name": "الاثنين",
            "muscle_group": "أرجل + بطن",
            "summary": "أجهزة الأرجل والبطن — بدون سكوات ثقيل.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "ضغط أرجل", "detail": "4 × 12"},
                {"name": "لف أرجل خلفي", "detail": "4 × 12"},
                {"name": "تمديد أرجل", "detail": "4 × 12"},
                {"name": "رفع ربلة", "detail": "4 × 15"},
                {"name": "بلانك", "detail": "3 مجموعات ثبات"},
                {"name": "بيرد دوغ", "detail": "3 × 10"},
                {"name": "ديد باغ", "detail": "3 × 10"},
                {"name": "سباحة", "detail": "20 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "دووشەممە",
            "muscle_group": "قاچ + ناوەکە",
            "summary": "ئامێری قاچ و ناوەکە — بە squat قورس.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "پرسی قاچ", "detail": "4 × 12"},
                {"name": "لەقەی قاچ", "detail": "4 × 12"},
                {"name": "درێژکردنەوەی قاچ", "detail": "4 × 12"},
                {"name": "بەرزکردنەوەی پێ", "detail": "4 × 15"},
                {"name": "پلانک", "detail": "3 سیت هێڵگرتن"},
                {"name": "بێرد داگ", "detail": "3 × 10"},
                {"name": "دێد باگ", "detail": "3 × 10"},
                {"name": "مەلەکردن", "detail": "20 خولەک"},
            ],
        },
    },
    1: {
        "en": {
            "day_name": "Tuesday",
            "muscle_group": "Shoulders + Traps",
            "summary": "Shoulders and traps with optional stair climber.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Shoulder Press", "detail": "4 × 12"},
                {"name": "Lateral Raise", "detail": "4 × 15"},
                {"name": "Rear Delt", "detail": "4 × 15"},
                {"name": "Shrugs", "detail": "3 × 15"},
                {"name": "Stair Climber", "detail": "10–15 min", "tag": "optional"},
                {"name": "Swimming", "detail": "20–30 min"},
            ],
        },
        "ar": {
            "day_name": "الثلاثاء",
            "muscle_group": "أكتاف + ترابيس",
            "summary": "أكتاف وترابيس مع درج اختياري.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "ضغط كتف", "detail": "4 × 12"},
                {"name": "رفع جانبي", "detail": "4 × 15"},
                {"name": "ديلت خلفي", "detail": "4 × 15"},
                {"name": "هز الأكتاف", "detail": "3 × 15"},
                {"name": "صعود درج", "detail": "10–15 دقيقة", "tag": "optional"},
                {"name": "سباحة", "detail": "20–30 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "سێشەممە",
            "muscle_group": "شان + تراپیس",
            "summary": "شان و تراپیس لەگەڵ سەرەدانی ئارەزوومەندانە.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "پرسی شان", "detail": "4 × 12"},
                {"name": "بەرزکردنەوەی لا", "detail": "4 × 15"},
                {"name": "دەلتی پشتەوە", "detail": "4 × 15"},
                {"name": "شڕەقینەی شان", "detail": "3 × 15"},
                {"name": "سەرەدانی پەلەکان", "detail": "10–15 خولەک", "tag": "optional"},
                {"name": "مەلەکردن", "detail": "20–30 خولەک"},
            ],
        },
    },
    2: {
        "en": {
            "day_name": "Wednesday",
            "muscle_group": "Chest + Back",
            "summary": "Combined chest and back session.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Chest Press", "detail": "4 × 12"},
                {"name": "Incline Chest Press", "detail": "3 × 12"},
                {"name": "Lat Pulldown", "detail": "4 × 12"},
                {"name": "Seated Row", "detail": "4 × 12"},
                {"name": "Elliptical", "detail": "15 min", "tag": "optional"},
                {"name": "Swimming", "detail": "20–30 min"},
            ],
        },
        "ar": {
            "day_name": "الأربعاء",
            "muscle_group": "صدر + ظهر",
            "summary": "جلسة تجمع الصدر والظهر.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "ضغط صدر", "detail": "4 × 12"},
                {"name": "ضغط صدر مائل", "detail": "3 × 12"},
                {"name": "سحب علوي (لات)", "detail": "4 × 12"},
                {"name": "تجديف جالس", "detail": "4 × 12"},
                {"name": "جهاز بيضاوي", "detail": "15 دقيقة", "tag": "optional"},
                {"name": "سباحة", "detail": "20–30 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "چوارشەممە",
            "muscle_group": "سینگ + پشت",
            "summary": "ڕاهێنانی تێکەڵی سینگ و پشت.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "پرسی سینگ", "detail": "4 × 12"},
                {"name": "پرسی سینگی لار", "detail": "3 × 12"},
                {"name": "لاٹ پولداون", "detail": "4 × 12"},
                {"name": "ڕۆی دانیشتوو", "detail": "4 × 12"},
                {"name": "ئەلپتیکال", "detail": "15 خولەک", "tag": "optional"},
                {"name": "مەلەکردن", "detail": "20–30 خولەک"},
            ],
        },
    },
    3: {
        "en": {
            "day_name": "Thursday",
            "muscle_group": "Arms + Core",
            "summary": "Arms and core with optional incline walk.",
            "exercises": [
                {"name": "Bicycle", "detail": "20 min", "tag": "warmup"},
                {"name": "Biceps Curl", "detail": "4 × 12"},
                {"name": "Hammer Curl", "detail": "3 × 12"},
                {"name": "Triceps Pushdown", "detail": "4 × 12"},
                {"name": "Overhead Extension", "detail": "3 × 12"},
                {"name": "Plank", "detail": "3 sets hold"},
                {"name": "Bird Dog", "detail": "3 × 10"},
                {"name": "Dead Bug", "detail": "3 × 10"},
                {"name": "Incline Walk", "detail": "15–20 min", "tag": "optional"},
                {"name": "Swimming", "detail": "20–30 min"},
            ],
        },
        "ar": {
            "day_name": "الخميس",
            "muscle_group": "ذراعين + بطن",
            "summary": "ذراعين وبطن مع مشي منحدر اختياري.",
            "exercises": [
                {"name": "دراجة ثابتة", "detail": "20 دقيقة", "tag": "warmup"},
                {"name": "بايسبس", "detail": "4 × 12"},
                {"name": "هامر كيرل", "detail": "3 × 12"},
                {"name": "ترايسبس بول داون", "detail": "4 × 12"},
                {"name": "تمديد فوق الرأس", "detail": "3 × 12"},
                {"name": "بلانك", "detail": "3 مجموعات ثبات"},
                {"name": "بيرد دوغ", "detail": "3 × 10"},
                {"name": "ديد باغ", "detail": "3 × 10"},
                {"name": "مشي على منحدر", "detail": "15–20 دقيقة", "tag": "optional"},
                {"name": "سباحة", "detail": "20–30 دقيقة"},
            ],
        },
        "ku": {
            "day_name": "پێنجشەممە",
            "muscle_group": "دەست + ناوەکە",
            "summary": "دەست و ناوەکە لەگەڵ پیاسەی لاری ئارەزوومەندانە.",
            "exercises": [
                {"name": "پاسکیل", "detail": "20 خولەک", "tag": "warmup"},
                {"name": "بایسپس کەرڵ", "detail": "4 × 12"},
                {"name": "هامەر کەرڵ", "detail": "3 × 12"},
                {"name": "ترایسپس پوش داون", "detail": "4 × 12"},
                {"name": "درێژکردنەوە سەرەوە", "detail": "3 × 12"},
                {"name": "پلانک", "detail": "3 سیت هێڵگرتن"},
                {"name": "بێرد داگ", "detail": "3 × 10"},
                {"name": "دێد باگ", "detail": "3 × 10"},
                {"name": "پیاسەی لار", "detail": "15–20 خولەک", "tag": "optional"},
                {"name": "مەلەکردن", "detail": "20–30 خولەک"},
            ],
        },
    },
    4: {
        "en": {
            "day_name": "Friday",
            "muscle_group": "Rest",
            "summary": "Active recovery — walking and optional easy swim.",
            "exercises": [
                {"name": "Walking", "detail": "6000–10000 steps"},
                {"name": "Easy Swimming", "detail": "optional", "tag": "optional"},
            ],
        },
        "ar": {
            "day_name": "الجمعة",
            "muscle_group": "راحة",
            "summary": "استشفاء نشط — مشي وسباحة خفيفة اختيارية.",
            "exercises": [
                {"name": "مشي", "detail": "6000–10000 خطوة"},
                {"name": "سباحة خفيفة", "detail": "اختياري", "tag": "optional"},
            ],
        },
        "ku": {
            "day_name": "هەینی",
            "muscle_group": "پشوو",
            "summary": "چاکبوونەوەی چالاک — پیاسە و مەلەی سووکی ئارەزوومەندانە.",
            "exercises": [
                {"name": "پیاسە", "detail": "6000–10000 هەنگاو"},
                {"name": "مەلەی سووک", "detail": "ئارەزوومەندانە", "tag": "optional"},
            ],
        },
    },
}


def get_course_plan(lang="en"):
    if lang not in LANGS:
        lang = "en"
    ui = UI[lang]
    days = []
    for dow in DAY_ORDER:
        day = PLAN[dow][lang]
        exercises = []
        for ex in day["exercises"]:
            tag = ex.get("tag")
            tag_label = ui.get(tag, "") if tag else ""
            exercises.append({
                "name": ex["name"],
                "detail": ex["detail"],
                "tag": tag,
                "tag_label": tag_label,
            })
        days.append({
            "day_of_week": dow,
            "day_name": day["day_name"],
            "muscle_group": day["muscle_group"],
            "summary": day["summary"],
            "exercises": exercises,
            "is_rest": dow == 4,
        })
    return {
        "lang": lang,
        "lang_label": LANGS[lang]["label"],
        "dir": LANGS[lang]["dir"],
        "ui": ui,
        "days": days,
        "languages": [{"code": c, "label": LANGS[c]["label"]} for c in LANGS],
    }
