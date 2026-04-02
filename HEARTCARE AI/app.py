from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Load trained model
model = joblib.load("heart_model.pkl")


# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("heartcare.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()


def save_prediction(data):
    conn = sqlite3.connect("heartcare.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            age, gender, height, weight, ap_hi, ap_lo,
            cholesterol, gluc, smoke, alco, active,
            bmi, map_value, pulse_pressure,
            probability, risk_level, advice, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["age"], data["gender"], data["height"], data["weight"],
        data["ap_hi"], data["ap_lo"], data["cholesterol"], data["gluc"],
        data["smoke"], data["alco"], data["active"],
        data["bmi"], data["map_value"], data["pulse_pressure"],
        data["probability"], data["risk_level"], data["advice"],
        data["created_at"]
    ))

    conn.commit()
    conn.close()


def get_all_predictions():
    conn = sqlite3.connect("heartcare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM predictions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# HELPER FUNCTIONS
# =========================
def risk_level(prob):
    if prob < 0.30:
        return "Low Risk", "Maintain healthy lifestyle."
    elif prob < 0.60:
        return "Moderate Risk", "Regular monitoring recommended."
    elif prob < 0.80:
        return "High Risk", "Consult physician and improve lifestyle."
    else:
        return "Critical Risk", "Immediate cardiology consultation required."

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
    if bmi >= 25:
        factors.append("High BMI / Overweight")
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

    if len(factors) == 0:
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
        tips.append("Control sugar intake and get blood glucose checked regularly.")
    if smoke == 1:
        tips.append("Quit smoking to reduce cardiovascular risk.")
    if alco == 1:
        tips.append("Limit alcohol consumption.")
    if active == 0:
        tips.append("Do at least 30 minutes of physical activity daily.")

    if len(tips) == 0:
        tips.append("Continue your healthy lifestyle and regular health checkups.")

    return tips


def get_emergency_alert(ap_hi, ap_lo):
    if ap_hi >= 180 or ap_lo >= 120:
        return "Emergency Alert: Blood pressure is in a dangerously high range. Immediate medical consultation is recommended."
    return None


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

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


@app.route("/predict", methods=["POST"])
def predict():
    try:
        age = float(request.form["age"])
        gender = int(request.form["gender"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        ap_hi = float(request.form["ap_hi"])
        ap_lo = float(request.form["ap_lo"])
        cholesterol = int(request.form["cholesterol"])
        gluc = int(request.form["gluc"])
        smoke = int(request.form["smoke"])
        alco = int(request.form["alco"])
        active = int(request.form["active"])

        errors = validate_inputs(age, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)

        if errors:
            return render_template(
                "result.html",
                probability=0,
                level="Invalid Input",
                advice="Please correct the input values and try again.",
                bmi=0,
                map_value=0,
                pulse_pressure=0,
                risk_factors=errors,
                health_tips=["Use valid medical values."],
                emergency_alert=None,
                band="Not Available",
                bmi_status="Not Available",
                generated_at="Unavailable"

            )

        age_years = age
        height_m = height / 100
        BMI = weight / (height_m ** 2)
        bmi_status = bmi_category(BMI)
        MAP = (2 * ap_lo + ap_hi) / 3
        Pulse_Pressure = ap_hi - ap_lo

        age_group = 1 if age_years > 50 else 0
        log_BMI = np.log(BMI) if BMI > 0 else 0
        log_MAP = np.log(MAP) if MAP > 0 else 0

        Age_BMI = age_years * BMI
        Age_BP = age_years * ap_hi
        BMI_Chol = BMI * cholesterol
        BP_Chol = ap_hi * cholesterol

        Risk_Count = (
            (1 if cholesterol > 1 else 0) +
            (1 if gluc > 1 else 0) +
            smoke +
            alco +
            (1 if active == 0 else 0)
        )

        features = np.array([[
            age, gender, height, weight, ap_hi, ap_lo,
            cholesterol, gluc, smoke, alco, active,
            age_years, height_m, BMI, MAP, Pulse_Pressure,
            age_group, log_BMI, log_MAP,
            Age_BMI, Age_BP, BMI_Chol, BP_Chol, Risk_Count
        ]])

        prob = model.predict_proba(features)[0][1]
        level, advice = risk_level(prob)
        band = confidence_band(prob)

        risk_factors = get_risk_factors(age, BMI, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)
        health_tips = get_health_tips(BMI, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active)
        emergency_alert = get_emergency_alert(ap_hi, ap_lo)

        save_prediction({
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": cholesterol,
            "gluc": gluc,
            "smoke": smoke,
            "alco": alco,
            "active": active,
            "bmi": round(BMI, 2),
            "map_value": round(MAP, 2),
            "pulse_pressure": round(Pulse_Pressure, 2),
            "probability": round(prob * 100, 2),
            "risk_level": level,
            "advice": advice,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return render_template(
    "result.html",
    probability=round(prob * 100, 2),
    level=level,
    advice=advice,
    bmi=round(BMI, 2),
    bmi_status=bmi_status,
    map_value=round(MAP, 2),
    pulse_pressure=round(Pulse_Pressure, 2),
    risk_factors=risk_factors,
    health_tips=health_tips,
    emergency_alert=emergency_alert,
    band="Not Available"
)
    except Exception:
     return render_template(
        "result.html",
        probability=0,
        level="Processing Error",
        advice="Something went wrong while processing your request.",
        bmi=0,
        map_value=0,
        pulse_pressure=0,
        risk_factors=["Unable to process the request."],
        health_tips=["Please check inputs and try again."],
        emergency_alert=None,
        band="Unavailable",
        bmi_status="Unavailable"
    )
    
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

    if "blood pressure" in q or "bp" in q or "high bp" in q:
        return "High blood pressure increases strain on the heart and blood vessels. Reduce salt intake, exercise regularly, manage stress, and monitor BP frequently."

    elif "cholesterol" in q:
        return "High cholesterol can lead to plaque buildup in arteries, increasing heart disease risk. Prefer a low-fat diet, avoid fried foods, and consult a doctor for lipid management."

    elif "bmi" in q or "weight" in q or "obesity" in q:
        return "Higher BMI or obesity can increase cardiovascular risk. Try maintaining a healthy diet, portion control, and regular physical activity."

    elif "smoking" in q or "smoke" in q:
        return "Smoking damages blood vessels and greatly increases the risk of heart disease. Quitting smoking is one of the most effective ways to improve heart health."

    elif "alcohol" in q or "drink" in q:
        return "Excess alcohol can raise blood pressure and harm heart health. It is best to limit alcohol consumption."

    elif "exercise" in q or "workout" in q or "physical activity" in q:
        return "Regular physical activity helps control weight, blood pressure, cholesterol, and glucose levels. Aim for at least 30 minutes of exercise most days of the week."

    elif "diet" in q or "food" in q or "eat" in q:
        return "A heart-healthy diet includes fruits, vegetables, whole grains, lean protein, and low salt. Avoid ultra-processed food, excess sugar, and unhealthy fats."

    elif "glucose" in q or "diabetes" in q or "sugar" in q:
        return "High blood glucose or diabetes can damage blood vessels over time and increase heart disease risk. Regular monitoring, diet control, and exercise are important."

    elif "heart disease" in q or "heart problem" in q:
        return "Heart disease refers to conditions affecting the heart and blood vessels. Major risk factors include high blood pressure, high cholesterol, diabetes, smoking, obesity, and inactivity."

    elif "reduce risk" in q or "prevention" in q or "prevent" in q:
        return "To reduce heart disease risk, maintain healthy weight, exercise regularly, avoid smoking, limit alcohol, eat a balanced diet, and monitor BP, cholesterol, and glucose."

    elif "hello" in q or "hi" in q or "hey" in q:
        return "Hello! I am your HeartCare AI Assistant. You can ask me about blood pressure, cholesterol, BMI, exercise, smoking, diet, glucose, or heart disease prevention."
    
    elif "low risk" in q:
        return "Low risk means your current input profile shows fewer major cardiovascular warning patterns, but regular monitoring and a healthy lifestyle are still important."

    elif "high risk" in q or "critical risk" in q:
        return "High or critical risk means your health inputs show multiple warning indicators. You should improve lifestyle factors and seek medical advice."

    elif "bmi category" in q:
        return "BMI categories are: Underweight below 18.5, Normal 18.5 to 24.9, Overweight 25 to 29.9, and Obese above 30."

    else:
        return "I can help with topics like blood pressure, cholesterol, BMI, smoking, alcohol, diet, exercise, glucose, and heart disease prevention. Please ask a health-related question."
    

@app.route("/about_heart_disease")
def about_heart_disease():
    return render_template("about_heart_disease.html")

@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)

def get_dashboard_data():
    conn = sqlite3.connect("heartcare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM predictions")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE risk_level = 'Low Risk'")
    low = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE risk_level = 'Moderate Risk'")
    moderate = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE risk_level = 'High Risk'")
    high = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE risk_level = 'Critical Risk'")
    critical = cursor.fetchone()["count"]

    cursor.execute("SELECT ROUND(AVG(bmi), 2) as avg_bmi FROM predictions")
    avg_bmi = cursor.fetchone()["avg_bmi"] or 0

    cursor.execute("SELECT ROUND(AVG(ap_hi), 2) as avg_ap_hi FROM predictions")
    avg_ap_hi = cursor.fetchone()["avg_ap_hi"] or 0

    cursor.execute("SELECT ROUND(AVG(ap_lo), 2) as avg_ap_lo FROM predictions")
    avg_ap_lo = cursor.fetchone()["avg_ap_lo"] or 0

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 5")
    recent_records = cursor.fetchall()

    conn.close()

    return {
        "total": total,
        "low": low,
        "moderate": moderate,
        "high": high,
        "critical": critical,
        "avg_bmi": avg_bmi,
        "avg_ap_hi": avg_ap_hi,
        "avg_ap_lo": avg_ap_lo,
        "recent_records": recent_records
    }


@app.route("/history")
def history():
    records = get_all_predictions()
    return render_template("history.html", records=records)


@app.route("/download_report", methods=["POST"])
def download_report():
    probability = request.form["probability"]
    level = request.form["level"]
    advice = request.form["advice"]
    bmi = request.form.get("bmi", "N/A")
    map_value = request.form.get("map_value", "N/A")
    pulse_pressure = request.form.get("pulse_pressure", "N/A")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 760, "HeartCare AI - Heart Risk Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Predicted Probability: {probability}%")
    p.drawString(100, 710, f"Risk Level: {level}")
    p.drawString(100, 690, f"Recommendation: {advice}")
    p.drawString(100, 670, f"BMI: {bmi}")
    p.drawString(100, 650, f"MAP: {map_value}")
    p.drawString(100, 630, f"Pulse Pressure: {pulse_pressure}")

    p.drawString(100, 590, "Generated by HeartCare AI System")
    p.drawString(100, 570, "Developer: Purushottam Kumar")
    p.drawString(100, 550, "Disclaimer: This report is for educational use only.")
    p.drawString(100, 530, "It is not a substitute for professional medical diagnosis.")

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Heart_Risk_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)