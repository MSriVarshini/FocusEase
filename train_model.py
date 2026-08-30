import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    LabelEncoder,
    PolynomialFeatures
)

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.linear_model import LinearRegression

from sklearn.cluster import KMeans

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==================================================
# 1. GENERATE PROFILE-BASED SYNTHETIC DATA
# ==================================================

np.random.seed(42)

n = 5000

profiles = np.random.choice(
    [
        "Balanced",
        "Overloaded",
        "High_Performer",
        "Low_Energy"
    ],
    n,
    p=[0.35, 0.25, 0.20, 0.20]
)

data = []

for profile in profiles:

    # ----------------------------------------------
    # BALANCED PROFILE
    # ----------------------------------------------

    if profile == "Balanced":

        sleep_hours = np.random.uniform(6.5, 8.5)
        sleep_quality = np.random.randint(3, 6)

        screen_time = np.random.uniform(3, 7)

        workload = np.random.randint(2, 4)

        energy_level = np.random.randint(3, 6)

        stress_level = np.random.randint(2, 4)

        previous_focus = np.random.uniform(3, 6)


    # ----------------------------------------------
    # OVERLOADED PROFILE
    # ----------------------------------------------

    elif profile == "Overloaded":

        sleep_hours = np.random.uniform(4, 6.5)
        sleep_quality = np.random.randint(1, 4)

        screen_time = np.random.uniform(7, 12)

        workload = np.random.randint(4, 6)

        energy_level = np.random.randint(1, 4)

        stress_level = np.random.randint(4, 6)

        previous_focus = np.random.uniform(1, 4)


    # ----------------------------------------------
    # HIGH PERFORMER
    # ----------------------------------------------

    elif profile == "High_Performer":

        sleep_hours = np.random.uniform(7, 9)

        sleep_quality = np.random.randint(4, 6)

        screen_time = np.random.uniform(2, 6)

        workload = np.random.randint(3, 6)

        energy_level = np.random.randint(4, 6)

        stress_level = np.random.randint(1, 4)

        previous_focus = np.random.uniform(5, 8)


    # ----------------------------------------------
    # LOW ENERGY
    # ----------------------------------------------

    else:

        sleep_hours = np.random.uniform(4.5, 7)

        sleep_quality = np.random.randint(1, 4)

        screen_time = np.random.uniform(5, 10)

        workload = np.random.randint(2, 5)

        energy_level = np.random.randint(1, 3)

        stress_level = np.random.randint(3, 6)

        previous_focus = np.random.uniform(1, 4)


    # ==================================================
    # USER TYPE
    # ==================================================

    user_type = np.random.choice(
        ["Student", "Professional"]
    )


    # ==================================================
    # WELLNESS FEATURES
    # ==================================================

    eye_strain = min(
        5,
        max(
            0,
            int(
                (screen_time - 2) / 2
                + np.random.normal(0, 1)
            )
        )
    )


    eye_discomfort = min(
        5,
        max(
            0,
            eye_strain + np.random.randint(-1, 2)
        )
    )


    head_discomfort = min(
        5,
        max(
            0,
            int(
                stress_level * 0.6
                + np.random.normal(0, 1)
            )
        )
    )


    mental_fatigue = min(
        5,
        max(
            0,
            int(
                (stress_level + workload) / 2
                + np.random.normal(0, 1)
            )
        )
    )


    neck_back_discomfort = min(
        5,
        max(
            0,
            int(
                screen_time / 2
                + np.random.normal(0, 1)
            )
        )
    )


    difficulty_concentrating = min(
        5,
        max(
            0,
            int(
                stress_level
                + mental_fatigue
                - energy_level
                + np.random.normal(0, 1)
            )
        )
    )


    # ==================================================
    # FEATURE ENGINEERING FOR DATA GENERATION
    # ==================================================

    sleep_score = (
        sleep_hours * sleep_quality
    )


    screen_fatigue = (
        screen_time
        * (eye_strain + eye_discomfort + 1)
        / 10
    )


    health_burden = (
        eye_strain
        + eye_discomfort
        + head_discomfort
        + neck_back_discomfort
    )


    cognitive_burden = (
        stress_level
        + mental_fatigue
        + difficulty_concentrating
    )


    # ==================================================
    # TARGET: FOCUS HOURS
    # ==================================================

    focus_hours = (

        # Sleep

        0.50 * sleep_hours

        + 0.35 * sleep_quality


        # Productivity

        - 0.16 * screen_time

        - 0.30 * workload

        + 0.55 * energy_level

        - 0.45 * stress_level

        + 0.32 * previous_focus


        # Wellness

        - 0.18 * eye_strain

        - 0.12 * eye_discomfort

        - 0.22 * head_discomfort

        - 0.30 * mental_fatigue

        - 0.14 * neck_back_discomfort

        - 0.28 * difficulty_concentrating


        # Engineered effects

        - 0.08 * screen_fatigue

        - 0.05 * health_burden

        - 0.06 * cognitive_burden


        # Noise

        + np.random.normal(0, 0.8)
    )


    focus_hours = np.clip(
        focus_hours,
        0,
        12
    )


    data.append([

        user_type,

        sleep_hours,
        sleep_quality,

        screen_time,

        workload,
        energy_level,
        stress_level,

        previous_focus,

        eye_strain,
        eye_discomfort,
        head_discomfort,
        mental_fatigue,
        neck_back_discomfort,
        difficulty_concentrating,

        focus_hours
    ])


# ==================================================
# 2. CREATE DATAFRAME
# ==================================================

columns = [

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
    "difficulty_concentrating",

    "focus_hours"
]


df = pd.DataFrame(
    data,
    columns=columns
)


# ==================================================
# SAVE DATASET
# ==================================================

df.to_csv(
    "productivity_data.csv",
    index=False
)


print("\n Dataset created successfully!")

print(
    "Dataset shape:",
    df.shape
)


# ==================================================
# 3. ENCODE USER TYPE
# ==================================================

encoder = LabelEncoder()

df["user_type"] = encoder.fit_transform(
    df["user_type"]
)


# ==================================================
# 4. FEATURES AND TARGET
# ==================================================

X = df.drop(
    "focus_hours",
    axis=1
)

y = df["focus_hours"]


# ==================================================
# 5. TRAIN / TEST SPLIT
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42
)


# ==================================================
# 6. MODEL COMPARISON
# ==================================================

models = {

    "Linear Regression":

        LinearRegression(),


    "Random Forest":

        RandomForestRegressor(

            n_estimators=300,

            max_depth=18,

            min_samples_split=5,

            min_samples_leaf=2,

            random_state=42,

            n_jobs=-1
        ),


    "Gradient Boosting":

        GradientBoostingRegressor(

            n_estimators=300,

            learning_rate=0.05,

            max_depth=3,

            random_state=42
        )
}


results = {}

best_model = None

best_model_name = None

best_mae = float("inf")


print("\n")

print("=" * 55)

print(" FOCUSEASE AI MODEL COMPARISON")

print("=" * 55)


# ==================================================
# 7. TRAIN MODELS
# ==================================================

for name, model in models.items():

    print(f"\n Training: {name}")

    model.fit(
        X_train,
        y_train
    )


    predictions = model.predict(
        X_test
    )


    mae = mean_absolute_error(
        y_test,
        predictions
    )


    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )


    r2 = r2_score(
        y_test,
        predictions
    )


    results[name] = {

        "MAE": mae,

        "RMSE": rmse,

        "R2": r2
    }


    print(
        "MAE:",
        round(mae, 3)
    )


    print(
        "RMSE:",
        round(rmse, 3)
    )


    print(
        "R² Score:",
        round(r2, 3)
    )


    # Select best model based on MAE

    if mae < best_mae:

        best_mae = mae

        best_model = model

        best_model_name = name


# ==================================================
# 8. MODEL COMPARISON TABLE
# ==================================================

results_df = pd.DataFrame(
    results
).T


print("\n")

print("=" * 55)

print("FINAL MODEL RESULTS")

print("=" * 55)


print(
    results_df.round(3)
)


print("\n BEST MODEL:", best_model_name)


# ==================================================
# 9. FEATURE IMPORTANCE
# ==================================================

if hasattr(
    best_model,
    "feature_importances_"
):

    importance_df = pd.DataFrame({

        "Feature":

            X.columns,

        "Importance":

            best_model.feature_importances_

    })


    importance_df = importance_df.sort_values(

        by="Importance",

        ascending=False
    )


    print("\n")

    print("=" * 55)

    print(" FEATURE IMPORTANCE")

    print("=" * 55)


    print(
        importance_df.to_string(
            index=False
        )
    )


# ==================================================
# 10. SAVE BEST MODEL
# ==================================================

joblib.dump(
    best_model,
    "model.pkl"
)


joblib.dump(
    encoder,
    "encoder.pkl"
)


joblib.dump(
    best_model_name,
    "best_model_name.pkl"
)


print(
    "\n💾 Best model saved as model.pkl"
)


# ==================================================
# 11. K-MEANS PRODUCTIVITY PERSONAS
# ==================================================

cluster_features = [

    "sleep_hours",

    "screen_time",

    "energy_level",

    "stress_level",

    "previous_focus_hours",

    "mental_fatigue",

    "focus_hours"
]


cluster_data = df[
    cluster_features
]


scaler = StandardScaler()


scaled_data = scaler.fit_transform(
    cluster_data
)


kmeans = KMeans(

    n_clusters=4,

    random_state=42,

    n_init=20
)


df["cluster"] = kmeans.fit_predict(
    scaled_data
)


joblib.dump(
    kmeans,
    "kmeans.pkl"
)


joblib.dump(
    scaler,
    "scaler.pkl"
)


print("\n")

print("=" * 55)

print("🔵 K-MEANS PRODUCTIVITY PERSONAS")

print("=" * 55)


print(

    df.groupby(
        "cluster"
    )[cluster_features]

    .mean()

    .round(2)

)


# ==================================================
# 12. FINAL MESSAGE
# ==================================================

print("\n")

print("=" * 55)

print(" FOCUSEASE AI ML ENGINE TRAINED SUCCESSFULLY!")

print("=" * 55)

print(
    f"""
 Best Regression Model: {best_model_name}

 Models Compared:
   • Linear Regression
   • Random Forest
   • Gradient Boosting

 Clustering:
   • K-Means Productivity Personas

 Features:
   • Lifestyle Signals
   • Productivity Signals
   • Health & Wellness Signals
"""
)
