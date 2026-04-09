from flask import Flask, render_template, request, send_file, redirect, url_for, Response
import joblib
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors as rl_colors
import io
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image
import scipy.stats as sci_stats
from scipy.signal import find_peaks
import csv

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load trained models
model = joblib.load("heart_model.pkl")
ecg_model = joblib.load("ecg_binary_model.pkl")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("heartcare.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT DEFAULT 'Anonymous',
            age REAL,
            gender INTEGER,
            height REAL,
            weight REAL,
            ap_hi REAL,
            ap_lo REAL,
            cholesterol INTEGER,
            gluc INTEGER,
            smoke INTEGER,
            alco INTEGER,
            active INTEGER,
            bmi REAL,
            map_value REAL,
            pulse_pressure REAL,
            probability REAL,
            risk_level TEXT,
            advice TEXT,
            created_at TEXT
        )
    """)

    # Add patient_name column if it doesn't exist (for existing DBs)
    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN patient_name TEXT DEFAULT 'Anonymous'")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ecg_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT DEFAULT 'Anonymous',
            filename TEXT,
            result TEXT,
            result_label TEXT,
            confidence REAL,
            num_peaks INTEGER,
            rr_mean REAL,
            rr_std REAL,
            mean_signal REAL,
            std_signal REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_prediction(data):
    conn = sqlite3.connect("heartcare.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            patient_name, age, gender, height, weight, ap_hi, ap_lo,
            cholesterol, gluc, smoke, alco, active,
            bmi, map_value, pulse_pressure,
            probability, risk_level, advice, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("patient_name", "Anonymous"),
        data["age"], data["gender"], data["height"], data["weight"],
        data["ap_hi"], data["ap_lo"], data["cholesterol"], data["gluc"],
        data["smoke"], data["alco"], data["active"],
        data["bmi"], data["map_value"], data["pulse_pressure"],
        data["probability"], data["risk_level"], data["advice"],
        data["created_at"]
    ))
    conn.commit()
    conn.close()


def save_ecg_prediction(data):
    conn = sqlite3.connect("heartcare.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ecg_predictions (
            patient_name, filename, result, result_label, confidence,
            num_peaks, rr_mean, rr_std, mean_signal, std_signal, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["patient_name"], data["filename"], data["result"],
        data["result_label"], data["confidence"],
        data["num_peaks"], data["rr_mean"], data["rr_std"],
        data["mean_signal"], data["std_signal"], data["created_at"]
    ))
    conn.commit()
    conn.close()


def get_all_predictions(search="", risk_filter=""):
    conn = sqlite3.connect("heartcare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if search:
        query += " AND (patient_name LIKE ? OR CAST(age AS TEXT) LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if risk_filter:
        query += " AND risk_level = ?"
        params.append(risk_filter)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_ecg_predictions():
    conn = sqlite3.connect("heartcare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ecg_predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# ECG IMAGE PROCESSING
# =========================
def extract_ecg_features_from_image(image_file):
    """Extract ECG signal statistical features from an uploaded ECG image."""
    img = Image.open(image_file).convert('L')  # Convert to grayscale

    # Resize to standard width for consistency
    width, height = img.size
    if width > 1400:
        ratio = 1400 / width
        img = img.resize((1400, int(height * ratio)), Image.LANCZOS)
    elif width < 200:
        img = img.resize((800, int(height * (800 / width))), Image.LANCZOS)

    arr = np.array(img, dtype=np.float64)

    # Invert if background is dark (ECG trace is usually dark on white background)
    if arr.mean() < 128:
        arr = 255.0 - arr

    # Extract signal: for each column, find the center of mass of dark pixels
    h, w = arr.shape
    signal = np.zeros(w)
    inverted = 255.0 - arr  # Dark pixels become bright

    for col in range(w):
        col_data = inverted[:, col]
        total = col_data.sum()
        if total > 0:
            signal[col] = np.average(np.arange(h), weights=col_data)
        else:
            signal[col] = h / 2.0

    # Normalize signal to zero mean, unit std
    sig_mean = signal.mean()
    sig_std = signal.std()
    if sig_std > 1e-6:
        signal_norm = (signal - sig_mean) / sig_std
    else:
        signal_norm = signal - sig_mean

    # --- Extract 13 features ---
    mean_val   = float(np.mean(signal_norm))
    std_val    = float(np.std(signal_norm))
    max_val    = float(np.max(signal_norm))
    min_val    = float(np.min(signal_norm))
    median_val = float(np.median(signal_norm))
    range_val  = float(max_val - min_val)
    rms_val    = float(np.sqrt(np.mean(signal_norm ** 2)))
    energy_val = float(np.sum(signal_norm ** 2))
    skew_val   = float(sci_stats.skew(signal_norm))
    kurt_val   = float(sci_stats.kurtosis(signal_norm))

    # Detect peaks
    peaks, _ = find_peaks(signal_norm, height=0.3, distance=max(5, w // 80))
    num_peaks = len(peaks)

    if len(peaks) > 1:
        rr_intervals = np.diff(peaks).astype(float)
        rr_mean = float(np.mean(rr_intervals))
        rr_std  = float(np.std(rr_intervals))
    else:
        rr_mean = 0.0
        rr_std  = 0.0

    features = np.array([[mean_val, std_val, max_val, min_val, median_val,
                          range_val, rms_val, energy_val, skew_val, kurt_val,
                          num_peaks, rr_mean, rr_std]])

    feature_info = {
        'mean':      round(mean_val, 4),
        'std':       round(std_val, 4),
        'max':       round(max_val, 4),
        'min':       round(min_val, 4),
        'median':    round(median_val, 4),
        'range':     round(range_val, 4),
        'rms':       round(rms_val, 4),
        'energy':    round(energy_val, 2),
        'skew':      round(skew_val, 4),
        'kurtosis':  round(kurt_val, 4),
        'num_peaks': num_peaks,
        'rr_mean':   round(rr_mean, 2),
        'rr_std':    round(rr_std, 2),
    }

    return features, feature_info


# =========================
# HELPER FUNCTIONS
# =========================
def risk_level(prob):
    if prob < 0.30:
        return "Low Risk", "Maintain healthy lifestyle with regular checkups."
    elif prob < 0.60:
        return "Moderate Risk", "Monitor health regularly and consult a physician."
    elif prob < 0.80:
        return "High Risk", "Consult a cardiologist and improve lifestyle urgently."
    else:
        return "Critical Risk", "Seek immediate cardiology consultation."


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    return "Obese"


def confidence_band(prob):
    if prob < 0.30:
        return "Stable Zone"
    elif prob < 0.60:
        return "Watch Zone"
    elif prob < 0.80:
        return "Attention Zone"
    return "Critical Zone"


def get_risk_factors(age, bmi, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active):
    factors = []
    if age > 50:
        factors.append("Age above 50")
    if bmi >= 30:
        factors.append("Obese BMI")
    elif bmi >= 25:
        factors.append("Overweight BMI")
    if ap_hi >= 140 or ap_lo >= 90:
        factors.append("High Blood Pressure")
    if cholesterol > 1:
        factors.append("High Cholesterol")
    if gluc > 1:
        factors.append("High Glucose")
    if smoke == 1:
        factors.append("Smoking Habit")
    if alco == 1:
        factors.append("Alcohol Consumption")
    if active == 0:
        factors.append("Low Physical Activity")
    if not factors:
        factors.append("No major visible risk factor")
    return factors


def get_health_tips(bmi, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active):
    tips = []
    if ap_hi >= 140 or ap_lo >= 90:
        tips.append("Reduce salt intake and monitor blood pressure regularly.")
    if bmi >= 25:
        tips.append("Maintain healthy weight through diet and regular exercise.")
    if cholesterol > 1:
        tips.append("Avoid oily and high-fat foods. Prefer a heart-healthy diet.")
    if gluc > 1:
        tips.append("Control sugar intake and check blood glucose regularly.")
    if smoke == 1:
        tips.append("Quit smoking — it's the single best cardiovascular improvement.")
    if alco == 1:
        tips.append("Limit alcohol to reduce BP and liver strain.")
    if active == 0:
        tips.append("Do at least 30 minutes of physical activity daily.")
    if not tips:
        tips.append("Continue your healthy lifestyle and get annual checkups.")
    return tips


def get_emergency_alert(ap_hi, ap_lo):
    if ap_hi >= 180 or ap_lo >= 120:
        return "EMERGENCY: BP is critically high. Seek immediate medical attention."
    if ap_hi >= 160:
        return "WARNING: Stage 2 hypertension detected. Please consult a doctor urgently."
    return None


def validate_inputs(age, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active):
    errors = []
    if age < 1 or age > 100:
        errors.append("Age must be between 1 and 100 years.")
    if height < 100 or height > 250:
        errors.append("Height must be between 100 and 250 cm.")
    if weight < 20 or weight > 250:
        errors.append("Weight must be between 20 and 250 kg.")
    if ap_hi < 70 or ap_hi > 250:
        errors.append("Systolic BP must be between 70 and 250.")
    if ap_lo < 40 or ap_lo > 150:
        errors.append("Diastolic BP must be between 40 and 150.")
    if ap_hi <= ap_lo:
        errors.append("Systolic BP must be greater than diastolic BP.")
    if cholesterol not in [1, 2, 3]:
        errors.append("Invalid cholesterol value.")
    if gluc not in [1, 2, 3]:
        errors.append("Invalid glucose value.")
    if smoke not in [0, 1]:
        errors.append("Invalid smoking value.")
    if alco not in [0, 1]:
        errors.append("Invalid alcohol value.")
    if active not in [0, 1]:
        errors.append("Invalid physical activity value.")
    return errors


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        patient_name = request.form.get("patient_name", "Anonymous").strip() or "Anonymous"
        age          = float(request.form["age"])
        gender       = int(request.form["gender"])
        height       = float(request.form["height"])
        weight       = float(request.form["weight"])
        ap_hi        = float(request.form["ap_hi"])
        ap_lo        = float(request.form["ap_lo"])
        cholesterol  = int(request.form["cholesterol"])
        gluc         = int(request.form["gluc"])
        smoke        = int(request.form["smoke"])
        alco         = int(request.form["alco"])
        active       = int(request.form["active"])

        errors = validate_inputs(age, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)
        if errors:
            return render_template(
                "result.html",
                patient_name=patient_name,
                probability=0, level="Invalid Input",
                advice="Please correct the input values and try again.",
                bmi=0, map_value=0, pulse_pressure=0,
                risk_factors=errors,
                health_tips=["Use valid medical values."],
                emergency_alert=None, band="Not Available",
                bmi_status="Not Available",
                generated_at="Unavailable"
            )

        age_years  = age
        height_m   = height / 100
        BMI        = weight / (height_m ** 2)
        bmi_status = bmi_category(BMI)
        MAP        = (2 * ap_lo + ap_hi) / 3
        PP         = ap_hi - ap_lo

        age_group = 1 if age_years > 50 else 0
        log_BMI   = np.log(BMI) if BMI > 0 else 0
        log_MAP   = np.log(MAP) if MAP > 0 else 0

        Age_BMI  = age_years * BMI
        Age_BP   = age_years * ap_hi
        BMI_Chol = BMI * cholesterol
        BP_Chol  = ap_hi * cholesterol

        Risk_Count = (
            (1 if cholesterol > 1 else 0) +
            (1 if gluc > 1 else 0) +
            smoke + alco +
            (1 if active == 0 else 0)
        )

        features = np.array([[
            age, gender, height, weight, ap_hi, ap_lo,
            cholesterol, gluc, smoke, alco, active,
            age_years, height_m, BMI, MAP, PP,
            age_group, log_BMI, log_MAP,
            Age_BMI, Age_BP, BMI_Chol, BP_Chol, Risk_Count
        ]])

        prob  = model.predict_proba(features)[0][1]
        level, advice = risk_level(prob)
        band  = confidence_band(prob)

        risk_factors  = get_risk_factors(age, BMI, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)
        health_tips   = get_health_tips(BMI, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)
        emergency_alert = get_emergency_alert(ap_hi, ap_lo)

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_prediction({
            "patient_name":   patient_name,
            "age":            age,
            "gender":         gender,
            "height":         height,
            "weight":         weight,
            "ap_hi":          ap_hi,
            "ap_lo":          ap_lo,
            "cholesterol":    cholesterol,
            "gluc":           gluc,
            "smoke":          smoke,
            "alco":           alco,
            "active":         active,
            "bmi":            round(BMI, 2),
            "map_value":      round(MAP, 2),
            "pulse_pressure": round(PP, 2),
            "probability":    round(prob * 100, 2),
            "risk_level":     level,
            "advice":         advice,
            "created_at":     generated_at
        })

        return render_template(
            "result.html",
            patient_name=patient_name,
            probability=round(prob * 100, 2),
            level=level, advice=advice,
            bmi=round(BMI, 2), bmi_status=bmi_status,
            map_value=round(MAP, 2),
            pulse_pressure=round(PP, 2),
            risk_factors=risk_factors,
            health_tips=health_tips,
            emergency_alert=emergency_alert,
            band=band,
            generated_at=generated_at
        )

    except Exception as e:
        return render_template(
            "result.html",
            patient_name="Unknown",
            probability=0, level="Processing Error",
            advice="Something went wrong. Please check your inputs.",
            bmi=0, map_value=0, pulse_pressure=0,
            risk_factors=["Unable to process the request."],
            health_tips=["Please check inputs and try again."],
            emergency_alert=None, band="Unavailable",
            bmi_status="Unavailable",
            generated_at="Unavailable"
        )


# =========================
# ECG ANALYSIS
# =========================
@app.route("/ecg_analysis", methods=["GET", "POST"])
def ecg_analysis():
    if request.method == "GET":
        return render_template("ecg_analysis.html", result=None)

    patient_name = request.form.get("patient_name", "Anonymous").strip() or "Anonymous"
    file = request.files.get("ecg_image")

    if not file or file.filename == "":
        return render_template("ecg_analysis.html", result=None,
                               error="Please upload an ECG image.")
    if not allowed_file(file.filename):
        return render_template("ecg_analysis.html", result=None,
                               error="Invalid file type. Upload PNG, JPG, BMP, or TIFF.")

    try:
        # Save uploaded filpe
        filename = secure_filename(file.filename)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = ts + filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.seek(0)
        file.save(save_path)

        # Extract features
        file.seek(0)
        features, feature_info = extract_ecg_features_from_image(file)

        # Predict
        prediction = ecg_model.predict(features)[0]
        proba = ecg_model.predict_proba(features)[0]
        confidence = round(float(proba[prediction]) * 100, 1)

        if prediction == 1:
            result_label = "Abnormal ECG"
            result_msg   = "Possible cardiac abnormality detected"
            result_class = "danger"
            result_icon  = "🚨"
            details = (
                "The ECG pattern analysis suggests potential cardiac abnormality. "
                "This may indicate arrhythmia, ischemia, or other heart conditions. "
                "Please consult a cardiologist for a proper clinical evaluation."
            )
        else:
            result_label = "Normal ECG"
            result_msg   = "No significant cardiac abnormality detected"
            result_class = "success"
            result_icon  = "✅"
            details = (
                "The ECG pattern analysis appears within normal range. "
                "However, this is a screening tool only. Regular cardiac checkups "
                "are still recommended, especially if you have risk factors."
            )

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_ecg_prediction({
            "patient_name": patient_name,
            "filename":     filename,
            "result":       str(prediction),
            "result_label": result_label,
            "confidence":   confidence,
            "num_peaks":    feature_info["num_peaks"],
            "rr_mean":      feature_info["rr_mean"],
            "rr_std":       feature_info["rr_std"],
            "mean_signal":  feature_info["mean"],
            "std_signal":   feature_info["std"],
            "created_at":   generated_at
        })

        result = {
            "patient_name": patient_name,
            "label":        result_label,
            "msg":          result_msg,
            "cls":          result_class,
            "icon":         result_icon,
            "details":      details,
            "confidence":   confidence,
            "features":     feature_info,
            "image_path":   f"uploads/{filename}",
            "generated_at": generated_at,
        }

        return render_template("ecg_analysis.html", result=result, error=None)

    except Exception as e:
        return render_template("ecg_analysis.html", result=None,
                               error=f"Could not process image: {str(e)}")


# =========================
# AI ASSISTANT
# =========================
@app.route("/ai_assistant", methods=["GET", "POST"])
def ai_assistant():
    answer = None
    user_query = ""
    if request.method == "POST":
        user_query = request.form.get("user_query", "")
        answer = get_ai_response(user_query)
    return render_template("ai_assistant.html", answer=answer, user_query=user_query)


def get_ai_response(user_query):
    q = user_query.lower().strip()

    responses = {
        ("blood pressure", "bp", "high bp", "hypertension"):
            "High blood pressure (hypertension) strains the heart and vessels. Reduce salt, exercise regularly, manage stress, avoid smoking, and monitor BP frequently. Normal BP is below 120/80 mmHg.",
        ("cholesterol", "ldl", "hdl"):
            "High LDL cholesterol causes plaque in arteries, risking heart attack. Eat more fiber, avoid fried/fatty foods, exercise, and consider statins if your doctor recommends.",
        ("bmi", "weight", "obesity", "overweight"):
            "High BMI increases cardiovascular risk. Aim for BMI 18.5–24.9 through balanced diet and at least 150 minutes of moderate exercise weekly.",
        ("smoking", "smoke", "cigarette", "tobacco"):
            "Smoking is the #1 preventable cause of heart disease. It damages vessel walls and increases clot risk. Quitting even after years of smoking significantly reduces risk.",
        ("alcohol", "drink", "drinking"):
            "Excess alcohol raises BP, causes arrhythmia, and weakens the heart muscle. Men: max 2 drinks/day; Women: max 1 drink/day.",
        ("exercise", "workout", "physical activity", "walk"):
            "150+ minutes/week of moderate aerobic exercise (brisk walking, cycling, swimming) reduces heart disease risk by up to 35%. Start slow and increase gradually.",
        ("diet", "food", "eat", "nutrition"):
            "Heart-healthy diet: fruits, vegetables, whole grains, lean protein, healthy fats (olive oil, nuts). Limit red meat, processed food, sugar, and salt.",
        ("glucose", "diabetes", "sugar", "blood sugar"):
            "Uncontrolled diabetes doubles heart disease risk. Monitor blood glucose, follow a low-glycemic diet, exercise regularly, and take prescribed medication.",
        ("heart attack", "heart disease", "coronary", "cardiac", "heart problem"):
            "Heart disease covers coronary artery disease, heart failure, arrhythmia, and more. Early signs: chest pain, shortness of breath, fatigue. Risk factors: BP, cholesterol, diabetes, smoking, obesity.",
        ("reduce risk", "prevention", "prevent", "protect heart"):
            "Top 5 to protect your heart: 1) Don't smoke, 2) Exercise daily, 3) Eat heart-healthy, 4) Manage BP/cholesterol/glucose, 5) Maintain healthy weight.",
        ("ecg", "electrocardiogram", "ecg test", "heart rhythm"):
            "An ECG records the heart's electrical activity. Abnormal patterns may indicate arrhythmia, ischemia, or prior heart attack. Our ECG Analysis tool can screen uploaded ECG images.",
        ("stress", "anxiety", "mental"):
            "Chronic stress raises cortisol, increasing BP and inflammation. Practice mindfulness, deep breathing, regular exercise, and adequate sleep (7–8 hrs).",
        ("age", "elderly", "old age"):
            "Cardiovascular risk increases with age, especially after 45 (men) and 55 (women). More frequent screenings for BP, cholesterol, and glucose are recommended.",
        ("sleep", "insomnia", "rest"):
            "Poor sleep (< 6 hrs/night) is linked to hypertension, obesity, and heart disease. Aim for 7–9 hours and maintain a consistent sleep schedule.",
        ("bmi category", "bmi range"):
            "BMI categories: Underweight < 18.5 | Normal 18.5–24.9 | Overweight 25–29.9 | Obese ≥ 30",
        ("low risk",):
            "Low risk means fewer cardiovascular warning signs currently. Maintain this through a healthy lifestyle, regular check-ups, and monitoring key metrics.",
        ("high risk", "critical risk", "danger"):
            "High/critical risk indicates multiple warning signs. Consult a cardiologist, adopt lifestyle changes immediately, and follow medical advice closely.",
        ("hello", "hi", "hey", "help"):
            "Hello! I'm HeartCare AI Assistant. Ask me about: blood pressure, cholesterol, BMI, ECG, diet, exercise, smoking, diabetes, heart disease, or risk prevention.",
    }

    for keywords, reply in responses.items():
        if any(k in q for k in keywords):
            return reply

    return ("I can help with: blood pressure, cholesterol, BMI, ECG, smoking, alcohol, diet, "
            "exercise, glucose/diabetes, sleep, stress, heart disease prevention, and risk levels. "
            "Please ask a specific health question.")


# =========================
# ABOUT
# =========================
@app.route("/about_heart_disease")
def about_heart_disease():
    return render_template("about_heart_disease.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)


def get_dashboard_data():
    conn = sqlite3.connect("heartcare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    def qone(sql, params=()):
        cursor.execute(sql, params)
        return cursor.fetchone()

    total    = qone("SELECT COUNT(*) as c FROM predictions")["c"]
    low      = qone("SELECT COUNT(*) as c FROM predictions WHERE risk_level='Low Risk'")["c"]
    moderate = qone("SELECT COUNT(*) as c FROM predictions WHERE risk_level='Moderate Risk'")["c"]
    high     = qone("SELECT COUNT(*) as c FROM predictions WHERE risk_level='High Risk'")["c"]
    critical = qone("SELECT COUNT(*) as c FROM predictions WHERE risk_level='Critical Risk'")["c"]

    avg_bmi   = qone("SELECT ROUND(AVG(bmi),2) as v FROM predictions")["v"] or 0
    avg_ap_hi = qone("SELECT ROUND(AVG(ap_hi),2) as v FROM predictions")["v"] or 0
    avg_ap_lo = qone("SELECT ROUND(AVG(ap_lo),2) as v FROM predictions")["v"] or 0
    avg_prob  = qone("SELECT ROUND(AVG(probability),2) as v FROM predictions")["v"] or 0

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 8")
    recent_records = cursor.fetchall()

    # BMI distribution buckets
    bmi_under  = qone("SELECT COUNT(*) as c FROM predictions WHERE bmi < 18.5")["c"]
    bmi_normal = qone("SELECT COUNT(*) as c FROM predictions WHERE bmi >= 18.5 AND bmi < 25")["c"]
    bmi_over   = qone("SELECT COUNT(*) as c FROM predictions WHERE bmi >= 25 AND bmi < 30")["c"]
    bmi_obese  = qone("SELECT COUNT(*) as c FROM predictions WHERE bmi >= 30")["c"]

    # Last 7 predictions trend
    cursor.execute("SELECT probability, created_at FROM predictions ORDER BY id DESC LIMIT 7")
    trend_rows = cursor.fetchall()
    trend_probs  = [r["probability"] for r in reversed(trend_rows)]
    trend_labels = [r["created_at"][:10] for r in reversed(trend_rows)]

    # ECG stats
    ecg_total    = qone("SELECT COUNT(*) as c FROM ecg_predictions")["c"]
    ecg_abnormal = qone("SELECT COUNT(*) as c FROM ecg_predictions WHERE result='1'")["c"]
    ecg_normal   = qone("SELECT COUNT(*) as c FROM ecg_predictions WHERE result='0'")["c"]

    conn.close()

    return {
        "total": total, "low": low, "moderate": moderate,
        "high": high, "critical": critical,
        "avg_bmi": avg_bmi, "avg_ap_hi": avg_ap_hi,
        "avg_ap_lo": avg_ap_lo, "avg_prob": avg_prob,
        "recent_records": recent_records,
        "bmi_under": bmi_under, "bmi_normal": bmi_normal,
        "bmi_over": bmi_over, "bmi_obese": bmi_obese,
        "trend_probs": trend_probs, "trend_labels": trend_labels,
        "ecg_total": ecg_total, "ecg_abnormal": ecg_abnormal,
        "ecg_normal": ecg_normal,
    }


# =========================
# HISTORY
# =========================
@app.route("/history")
def history():
    search      = request.args.get("search", "").strip()
    risk_filter = request.args.get("risk", "").strip()
    records     = get_all_predictions(search, risk_filter)
    return render_template("history.html", records=records,
                           search=search, risk_filter=risk_filter)


@app.route("/ecg_history")
def ecg_history():
    records = get_all_ecg_predictions()
    return render_template("ecg_history.html", records=records)


@app.route("/export_csv")
def export_csv():
    records = get_all_predictions()

    def generate():
        header = ["ID", "Patient Name", "Date", "Age", "Gender", "Height", "Weight",
                  "Systolic BP", "Diastolic BP", "Cholesterol", "Glucose",
                  "Smoking", "Alcohol", "Active", "BMI", "MAP",
                  "Pulse Pressure", "Probability %", "Risk Level", "Advice"]
        yield ",".join(header) + "\n"
        for r in records:
            row = [
                str(r["id"]), r["patient_name"] or "Anonymous",
                r["created_at"], str(r["age"]),
                "Female" if r["gender"] == 1 else "Male",
                str(r["height"]), str(r["weight"]),
                str(r["ap_hi"]), str(r["ap_lo"]),
                str(r["cholesterol"]), str(r["gluc"]),
                str(r["smoke"]), str(r["alco"]), str(r["active"]),
                str(r["bmi"]), str(r["map_value"]), str(r["pulse_pressure"]),
                str(r["probability"]), r["risk_level"], r["advice"]
            ]
            yield ",".join(f'"{v}"' for v in row) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=heartcare_history.csv"}
    )


# =========================
# PDF REPORT
# =========================
@app.route("/download_report", methods=["POST"])
def download_report():
    patient_name   = request.form.get("patient_name", "Anonymous")
    probability    = request.form.get("probability", "N/A")
    level          = request.form.get("level", "N/A")
    advice         = request.form.get("advice", "N/A")
    bmi            = request.form.get("bmi", "N/A")
    bmi_status_val = request.form.get("bmi_status", "N/A")
    map_value      = request.form.get("map_value", "N/A")
    pulse_pressure = request.form.get("pulse_pressure", "N/A")
    risk_factors   = request.form.get("risk_factors_str", "")
    health_tips    = request.form.get("health_tips_str", "")
    generated_at   = request.form.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    W, H = letter

    # ---- Header bar ----
    p.setFillColorRGB(0.07, 0.04, 0.18)
    p.rect(0, H - 72, W, 72, fill=1, stroke=0)

    p.setFillColorRGB(0.49, 0.23, 0.93)
    p.circle(40, H - 36, 8, fill=1, stroke=0)

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.92, 0.94, 1)
    p.drawString(60, H - 42, "HeartCare AI — Heart Risk Report")

    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.7, 0.75, 0.9)
    p.drawString(60, H - 58, f"Generated: {generated_at}   |   Patient: {patient_name}")

    # ---- Risk box ----
    try:
        prob_float = float(probability)
    except Exception:
        prob_float = 0

    if prob_float < 30:
        r, g, b = 0.13, 0.77, 0.37
    elif prob_float < 60:
        r, g, b = 0.96, 0.62, 0.04
    elif prob_float < 80:
        r, g, b = 0.94, 0.27, 0.27
    else:
        r, g, b = 0.55, 0.05, 0.05

    p.setFillColorRGB(r, g, b)
    p.roundRect(40, H - 175, 240, 80, 10, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(160, H - 140, f"{probability}%")
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(160, H - 162, f"Risk Score — {level}")

    # ---- Metrics ----
    p.setFillColorRGB(0.92, 0.94, 1)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(310, H - 105, "Clinical Metrics")
    p.setFont("Helvetica", 11)
    metrics = [
        ("BMI", f"{bmi}  ({bmi_status_val})"),
        ("Mean Arterial Pressure", f"{map_value} mmHg"),
        ("Pulse Pressure", f"{pulse_pressure} mmHg"),
        ("Recommendation", advice),
    ]
    y = H - 122
    for label, val in metrics:
        p.setFont("Helvetica-Bold", 10)
        p.setFillColorRGB(0.55, 0.6, 0.85)
        p.drawString(310, y, label + ":")
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0.92, 0.94, 1)
        # Wrap long text
        if len(val) > 45:
            val = val[:45] + "…"
        p.drawString(310, y - 13, val)
        y -= 34

    # ---- Divider ----
    p.setStrokeColorRGB(0.49, 0.23, 0.93)
    p.setLineWidth(1.5)
    p.line(40, H - 190, W - 40, H - 190)

    # ---- Risk Factors ----
    y = H - 210
    p.setFillColorRGB(0.92, 0.94, 1)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "Identified Risk Factors")
    y -= 18
    p.setFont("Helvetica", 10)
    if risk_factors:
        for factor in risk_factors.split("|"):
            factor = factor.strip()
            if factor:
                p.setFillColorRGB(0.94, 0.27, 0.27)
                p.circle(50, y + 3, 3, fill=1, stroke=0)
                p.setFillColorRGB(0.92, 0.94, 1)
                p.drawString(60, y, factor)
                y -= 16

    # ---- Health Tips ----
    y -= 8
    p.setFont("Helvetica-Bold", 13)
    p.setFillColorRGB(0.92, 0.94, 1)
    p.drawString(40, y, "Health Recommendations")
    y -= 18
    p.setFont("Helvetica", 10)
    if health_tips:
        for tip in health_tips.split("|"):
            tip = tip.strip()
            if tip:
                p.setFillColorRGB(0.13, 0.77, 0.37)
                p.circle(50, y + 3, 3, fill=1, stroke=0)
                p.setFillColorRGB(0.92, 0.94, 1)
                # Wrap tip at ~90 chars
                words = tip.split()
                line = ""
                for word in words:
                    if len(line) + len(word) + 1 > 90:
                        p.drawString(60, y, line)
                        y -= 14
                        line = word
                    else:
                        line = (line + " " + word).strip()
                if line:
                    p.drawString(60, y, line)
                    y -= 16

    # ---- Footer ----
    p.setStrokeColorRGB(0.3, 0.3, 0.5)
    p.setLineWidth(0.8)
    p.line(40, 55, W - 40, 55)
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0.55, 0.6, 0.85)
    p.drawString(40, 40, "HeartCare AI — Developed by Purushottam Kumar")
    p.drawRightString(W - 40, 40, "Disclaimer: Educational use only. Not a medical diagnosis.")

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"HeartCare_Report_{patient_name.replace(' ', '_')}.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
