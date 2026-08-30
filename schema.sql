CREATE DATABASE IF NOT EXISTS focusease_db;

USE focusease_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_type ENUM('Student', 'Professional') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    sleep_hours FLOAT,
    screen_time FLOAT,
    workload INT,
    energy_level INT,
    stress_level INT,
    breaks_taken INT,

    eye_strain BOOLEAN DEFAULT FALSE,
    head_discomfort BOOLEAN DEFAULT FALSE,
    fatigue BOOLEAN DEFAULT FALSE,

    weather VARCHAR(100),
    temperature FLOAT,

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