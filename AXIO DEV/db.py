import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "axio.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # User Profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT 'Athlete',
        age INTEGER DEFAULT 28,
        gender TEXT DEFAULT 'Other',
        height_cm REAL DEFAULT 175.0,
        weight_kg REAL DEFAULT 75.0,
        fitness_goal TEXT DEFAULT 'Hypertrophy & Strength',
        experience_level TEXT DEFAULT 'Intermediate',
        workout_frequency INTEGER DEFAULT 4,
        equipment TEXT DEFAULT 'Full Gym',
        injuries TEXT DEFAULT 'None',
        diet_type TEXT DEFAULT 'Balanced High-Protein',
        bmr REAL DEFAULT 1720.0,
        tdee REAL DEFAULT 2450.0,
        target_calories REAL DEFAULT 2300.0,
        target_protein REAL DEFAULT 165.0,
        target_carbs REAL DEFAULT 250.0,
        target_fats REAL DEFAULT 70.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Workout Plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        goal TEXT,
        split_type TEXT,
        plan_json TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Workout Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan_id INTEGER,
        workout_title TEXT,
        duration_minutes INTEGER DEFAULT 45,
        total_volume_kg REAL DEFAULT 0.0,
        exercises_completed INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Workout Log Sets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_id INTEGER,
        exercise_name TEXT,
        set_number INTEGER,
        weight_kg REAL,
        reps INTEGER,
        rpe REAL,
        FOREIGN KEY(log_id) REFERENCES workout_logs(id)
    )
    """)

    # Form Analyses (Camera Movement Analysis results)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS form_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exercise_name TEXT,
        score INTEGER,
        reps_detected INTEGER DEFAULT 0,
        primary_feedback TEXT,
        detailed_analysis_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Coach Chat History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT,
        message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Nutrition Plans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        calories INTEGER,
        protein_g REAL,
        carbs_g REAL,
        fats_g REAL,
        plan_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Seed initial user if not exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO users (
            name, age, gender, height_cm, weight_kg, fitness_goal,
            experience_level, workout_frequency, equipment, injuries,
            diet_type, bmr, tdee, target_calories, target_protein, target_carbs, target_fats
        ) VALUES (
            'Alex Vance', 29, 'Male', 180.0, 78.5, 'Hypertrophy & Strength',
            'Intermediate', 4, 'Full Commercial Gym', 'Mild right shoulder impingement',
            'High Protein', 1780.0, 2580.0, 2450.0, 175.0, 260.0, 72.0
        )
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("AXIO Database initialized successfully.")
