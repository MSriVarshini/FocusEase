from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import pandas as pd

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "focusease_secret")

# --------------------------------------------------
# MYSQL CONFIGURATION
# --------------------------------------------------

db_config = {
   "host": os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE"),
    "port": int(os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or 3306)
}

# --------------------------------------------------
# LOAD ML MODELS
# --------------------------------------------------

model = joblib.load("model.pkl")
encoder = joblib.load("encoder.pkl")
kmeans = joblib.load("kmeans.pkl")
scaler = joblib.load("scaler.pkl")

# --------------------------------------------------
# PRODUCTIVITY PERSONAS
# --------------------------------------------------

persona_names = {
    0: "Balanced Performer",
    1: "Digitally Overloaded",
    2: "Low Energy / High Stress",
    3: "High Performance"
}


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        **db_config,
        connection_timeout=10
    )


# --------------------------------------------------
# WELLNESS IMPACT CALCULATION
# --------------------------------------------------

def calculate_wellness(data):

    score = 100

    # Wellness factors reduce the score
    score -= data["eye_strain"] * 4
    score -= data["eye_discomfort"] * 3
    score -= data["head_discomfort"] * 5
    score -= data["mental_fatigue"] * 6
    score -= data["neck_back_discomfort"] * 3
    score -= data["difficulty_concentrating"] * 5

    score = max(0, min(100, score))

    if score >= 75:
        impact = "Low Impact"
    elif score >= 50:
        impact = "Moderate Impact"
    else:
        impact = "High Impact"

    return score, impact


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.route("/signup", methods=["POST"])
def signup():

    connection = None
    cursor = None

    try:
        data = request.get_json()

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]
        user_type = data["user_type"]
        daily_goal = data.get("daily_goal", "").strip()

        if not name or not email or not password:
            return jsonify({
                "success": False,
                "error": "Name, email and password are required."
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "error": "An account with this email already exists. Please log in."
            }), 409

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password_hash, user_type, daily_goal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, password_hash, user_type, daily_goal)
        )

        connection.commit()
        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "user_id": user_id,
            "name": name,
            "user_type": user_type,
            "daily_goal": daily_goal,
            "message": "Account created successfully!"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    connection = None
    cursor = None

    try:
        data = request.get_json()

        email = data["email"].strip().lower()
        password = data["password"]

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Email and password are required."
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, password_hash, user_type, daily_goal
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "error": "No account found with this email."
            }), 404

        user_id, name, password_hash, user_type, daily_goal = user

        if not check_password_hash(password_hash, password):
            return jsonify({
                "success": False,
                "error": "Incorrect password."
            }), 401

        return jsonify({
            "success": True,
            "user_id": user_id,
            "name": name,
            "user_type": user_type,
            "daily_goal": daily_goal,
            "message": f"Welcome back, {name}! 👋"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# COGNITIVE READINESS SCORE
# --------------------------------------------------

def calculate_readiness(data):

    score = 50

    score += data["sleep_hours"] * 4
    score += data["sleep_quality"] * 5
    score += data["energy_level"] * 6
    score += data["previous_focus_hours"] * 2

    score -= data["stress_level"] * 5
    score -= data["mental_fatigue"] * 6
    score -= data["difficulty_concentrating"] * 5

    score = max(0, min(100, score))

    if score >= 75:
        level = "High Readiness"
    elif score >= 50:
        level = "Moderate Readiness"
    else:
        level = "Low Readiness"

    return score, level


# --------------------------------------------------
# PERSONALIZED RECOMMENDATION
# --------------------------------------------------

def generate_recommendation(data, focus_hours, wellness_impact, readiness):

    recommendations = []

    if data["eye_strain"] >= 3:
        recommendations.append(
            "Enable Comfort Mode and take regular screen breaks."
        )

    if data["head_discomfort"] >= 3:
        recommendations.append(
            "Reduce visual clutter and choose shorter focus sessions."
        )

    if data["mental_fatigue"] >= 3:
        recommendations.append(
            "Start with lighter tasks and take structured breaks."
        )

    if data["stress_level"] >= 4:
        recommendations.append(
            "Prioritize important tasks and avoid multitasking."
        )

    if data["sleep_hours"] < 6:
        recommendations.append(
            "Your sleep level is low. Avoid planning extremely demanding work."
        )

    if readiness == "High Readiness":
        recommendations.append(
            "Great time for deep work or challenging tasks!"
        )

    elif readiness == "Low Readiness":
        recommendations.append(
            "Focus on lighter tasks and avoid cognitive overload."
        )

    if focus_hours >= 6:
        recommendations.append(
            "Your predicted focus capacity is strong today."
        )
    elif focus_hours < 3:
        recommendations.append(
            "Plan shorter sessions and realistic goals today."
        )

    if not recommendations:
        recommendations.append(
            "Maintain your current routine and take regular breaks."
        )

    return recommendations


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# PREDICTION API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    connection = None
    cursor = None

    try:
        data = request.get_json()

        # Get logged-in user
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required. Please log in again."
            }), 400

        # Get user input
        user_type = data["user_type"]

        input_data = {
            "sleep_hours": float(data["sleep_hours"]),
            "sleep_quality": int(data["sleep_quality"]),
            "screen_time": float(data["screen_time"]),
            "workload": int(data["workload"]),
            "energy_level": int(data["energy_level"]),
            "stress_level": int(data["stress_level"]),
            "previous_focus_hours": float(data["previous_focus_hours"]),
            "eye_strain": int(data["eye_strain"]),
            "eye_discomfort": int(data["eye_discomfort"]),
            "head_discomfort": int(data["head_discomfort"]),
            "mental_fatigue": int(data["mental_fatigue"]),
            "neck_back_discomfort": int(data["neck_back_discomfort"]),
            "difficulty_concentrating": int(data["difficulty_concentrating"])
        }

        # Encode Student / Professional
        user_type_encoded = encoder.transform([user_type])[0]

        # ML prediction with feature names
        feature_columns = [
            "user_type",
            "sleep_hours",
            "sleep_quality",
            "screen_time",
            "workload",
            "energy_level",
            "stress_level",
            "previous_focus_hours",
            "eye_strain",
            "eye_discomfort",
            "head_discomfort",
            "mental_fatigue",
            "neck_back_discomfort",
            "difficulty_concentrating"
        ]

        features_df = pd.DataFrame(
            [[
                user_type_encoded,
                input_data["sleep_hours"],
                input_data["sleep_quality"],
                input_data["screen_time"],
                input_data["workload"],
                input_data["energy_level"],
                input_data["stress_level"],
                input_data["previous_focus_hours"],
                input_data["eye_strain"],
                input_data["eye_discomfort"],
                input_data["head_discomfort"],
                input_data["mental_fatigue"],
                input_data["neck_back_discomfort"],
                input_data["difficulty_concentrating"]
            ]],
            columns=feature_columns
        )

        focus_hours = float(model.predict(features_df)[0])
        focus_hours = max(0, min(12, focus_hours))

        # Wellness and readiness
        wellness_score, wellness_impact = calculate_wellness(input_data)
        readiness_score, readiness = calculate_readiness(input_data)

        # K-Means persona
        cluster_columns = [
            "sleep_hours",
            "screen_time",
            "energy_level",
            "stress_level",
            "previous_focus_hours",
            "mental_fatigue",
            "focus_hours"
        ]

        cluster_df = pd.DataFrame(
            [[
                input_data["sleep_hours"],
                input_data["screen_time"],
                input_data["energy_level"],
                input_data["stress_level"],
                input_data["previous_focus_hours"],
                input_data["mental_fatigue"],
                focus_hours
            ]],
            columns=cluster_columns
        )

        scaled_features = scaler.transform(cluster_df)
        cluster = int(kmeans.predict(scaled_features)[0])
        persona = persona_names.get(cluster, "Unknown Persona")

        # Recommendations
        recommendations = generate_recommendation(
            input_data,
            focus_hours,
            wellness_impact,
            readiness
        )

        recommendation_text = " | ".join(recommendations)

        # Database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Save daily check-in
        cursor.execute(
            """
            INSERT INTO daily_checkins (
                user_id,
                sleep_hours,
                sleep_quality,
                screen_time,
                workload,
                energy_level,
                stress_level,
                previous_focus_hours,
                eye_strain,
                eye_discomfort,
                head_discomfort,
                mental_fatigue,
                neck_back_discomfort,
                difficulty_concentrating
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                user_id,
                input_data["sleep_hours"],
                input_data["sleep_quality"],
                input_data["screen_time"],
                input_data["workload"],
                input_data["energy_level"],
                input_data["stress_level"],
                input_data["previous_focus_hours"],
                input_data["eye_strain"],
                input_data["eye_discomfort"],
                input_data["head_discomfort"],
                input_data["mental_fatigue"],
                input_data["neck_back_discomfort"],
                input_data["difficulty_concentrating"]
            )
        )

        checkin_id = cursor.lastrowid

        # Save AI prediction
        cursor.execute(
            """
            INSERT INTO predictions (
                user_id,
                checkin_id,
                predicted_focus_hours,
                productivity_persona,
                cognitive_readiness_score,
                wellness_score,
                wellness_impact,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                checkin_id,
                round(focus_hours, 2),
                persona,
                readiness_score,
                wellness_score,
                wellness_impact,
                recommendation_text
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "predicted_focus_hours": round(focus_hours, 2),
            "productivity_persona": persona,
            "wellness_score": wellness_score,
            "wellness_impact": wellness_impact,
            "cognitive_readiness_score": readiness_score,
            "cognitive_readiness": readiness,
            "recommendations": recommendations
        })

    except Exception as e:

        if connection:
            connection.rollback()

        print("❌ PREDICTION ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
