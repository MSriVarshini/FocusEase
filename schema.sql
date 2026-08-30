CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    user_type ENUM('Student', 'Professional') NOT NULL,

    daily_goal VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS daily_checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    sleep_hours FLOAT,

    sleep_quality INT,

    screen_time FLOAT,

    workload INT,

    energy_level INT,

    stress_level INT,

    previous_focus_hours FLOAT,

    eye_strain INT,

    eye_discomfort INT,

    head_discomfort INT,

    mental_fatigue INT,

    neck_back_discomfort INT,

    difficulty_concentrating INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    checkin_id INT NOT NULL,

    predicted_focus_hours FLOAT,

    productivity_persona VARCHAR(100),

    cognitive_readiness_score INT,

    wellness_score INT,

    wellness_impact VARCHAR(50),

    recommendation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (checkin_id)
        REFERENCES daily_checkins(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS focus_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    duration_minutes INT,

    breaks_taken INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
