import http.server
import socketserver
import json
import os
import sys
import urllib.parse
import sqlite3
import base64
from datetime import datetime

# Local imports
import db
import ai_service

PORT = int(os.environ.get("PORT", 9000))
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class AxioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    # Disable reverse DNS lookup to prevent hangs
    def address_string(self):
        return self.client_address[0]

    def log_message(self, format, *args):
        # Concise logging
        sys.stdout.write(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} - {format%args}\n")
        sys.stdout.flush()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/"):
            self.handle_api_get(path, urllib.parse.parse_qs(parsed_url.query))
        else:
            filepath = os.path.join(STATIC_DIR, path.lstrip("/"))
            if not os.path.exists(filepath) or os.path.isdir(filepath):
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/"):
            self.handle_api_post(path)
        else:
            self._send_json({"error": "Not Found"}, status=404)

    def handle_api_get(self, path, query_params):
        try:
            if path == "/api/profile":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                conn.close()
                if row:
                    self._send_json(dict(row))
                else:
                    self._send_json({"error": "Profile not found"}, status=404)

            elif path == "/api/exercises":
                ex_path = os.path.join(DATA_DIR, "exercises.json")
                if os.path.exists(ex_path):
                    with open(ex_path, "r") as f:
                        data = json.load(f)
                    category = query_params.get("category", [None])[0]
                    if category and category != "All":
                        data = [e for e in data if e.get("category", "").lower() == category.lower()]
                    self._send_json(data)
                else:
                    self._send_json([])

            elif path == "/api/workouts":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM workout_plans ORDER BY id DESC")
                rows = cur.fetchall()
                conn.close()
                plans = []
                for r in rows:
                    item = dict(r)
                    if item.get("plan_json"):
                        item["plan"] = json.loads(item["plan_json"])
                    plans.append(item)
                self._send_json(plans)

            elif path == "/api/workouts/history":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT wl.*, COUNT(ws.id) as set_count 
                    FROM workout_logs wl
                    LEFT JOIN workout_sets ws ON wl.id = ws.log_id
                    GROUP BY wl.id
                    ORDER BY wl.id DESC
                    LIMIT 20
                """)
                logs = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._send_json(logs)

            elif path == "/api/analytics":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as total_workouts, SUM(total_volume_kg) as total_volume, AVG(duration_minutes) as avg_duration FROM workout_logs")
                stats = dict(cur.fetchone())
                
                cur.execute("SELECT exercise_name, score, created_at FROM form_analyses ORDER BY id DESC LIMIT 10")
                form_history = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT workout_title, total_volume_kg, logged_at FROM workout_logs ORDER BY id DESC LIMIT 7")
                volume_history = [dict(r) for r in cur.fetchall()]

                conn.close()
                self._send_json({
                    "summary": {
                        "total_workouts": stats.get("total_workouts") or 0,
                        "total_volume_kg": round(stats.get("total_volume") or 0, 1),
                        "avg_duration_min": round(stats.get("avg_duration") or 0, 1),
                        "streak_days": 4
                    },
                    "form_history": form_history,
                    "volume_history": volume_history
                })

            elif path == "/api/coach/history":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sender, message, created_at FROM chat_messages ORDER BY id ASC LIMIT 50")
                history = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._send_json(history)

            elif path == "/api/nutrition":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM nutrition_plans ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                conn.close()
                if row:
                    res = dict(row)
                    if res.get("plan_json"):
                        res["plan"] = json.loads(res["plan_json"])
                    self._send_json(res)
                else:
                    self._send_json(None)

            else:
                self._send_json({"error": "Endpoint not found"}, status=404)

        except Exception as e:
            self._send_json({"error": str(e)}, status=500)

    def handle_api_post(self, path):
        try:
            body = self._read_json_body()

            if path == "/api/profile":
                conn = db.get_connection()
                cur = conn.cursor()
                
                weight = float(body.get("weight_kg", 75))
                height = float(body.get("height_cm", 175))
                age = int(body.get("age", 28))
                gender = body.get("gender", "Male")
                freq = int(body.get("workout_frequency", 4))
                goal = body.get("fitness_goal", "Hypertrophy & Strength")
                
                if gender.lower() == "female":
                    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
                else:
                    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
                
                activity_factors = {2: 1.375, 3: 1.45, 4: 1.55, 5: 1.65, 6: 1.75}
                tdee = bmr * activity_factors.get(freq, 1.5)
                
                if "fat loss" in goal.lower() or "cutting" in goal.lower():
                    target_cals = tdee - 450
                    protein = weight * 2.2
                    fats = (target_cals * 0.25) / 9
                    carbs = (target_cals - (protein * 4) - (fats * 9)) / 4
                elif "hypertrophy" in goal.lower() or "strength" in goal.lower() or "muscle" in goal.lower():
                    target_cals = tdee + 250
                    protein = weight * 2.0
                    fats = (target_cals * 0.28) / 9
                    carbs = (target_cals - (protein * 4) - (fats * 9)) / 4
                else:
                    target_cals = tdee
                    protein = weight * 1.8
                    fats = (target_cals * 0.27) / 9
                    carbs = (target_cals - (protein * 4) - (fats * 9)) / 4

                cur.execute("""
                    INSERT INTO users (
                        name, age, gender, height_cm, weight_kg, fitness_goal,
                        experience_level, workout_frequency, equipment, injuries,
                        diet_type, bmr, tdee, target_calories, target_protein, target_carbs, target_fats, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    body.get("name", "Athlete"),
                    age,
                    gender,
                    height,
                    weight,
                    goal,
                    body.get("experience_level", "Intermediate"),
                    freq,
                    body.get("equipment", "Full Gym"),
                    body.get("injuries", "None"),
                    body.get("diet_type", "Balanced High-Protein"),
                    round(bmr, 1),
                    round(tdee, 1),
                    round(target_cals, 0),
                    round(protein, 1),
                    round(carbs, 1),
                    round(fats, 1)
                ))
                user_id = cur.lastrowid
                conn.commit()
                
                cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user = dict(cur.fetchone())
                conn.close()
                self._send_json(user)

            elif path == "/api/workouts/generate":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                profile = dict(row) if row else {}
                profile.update(body)

                plan_data = ai_service.generate_workout_plan(profile)
                
                cur.execute("""
                    INSERT INTO workout_plans (user_id, title, goal, split_type, plan_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    profile.get("id", 1),
                    plan_data.get("title", "AXIO Custom Routine"),
                    profile.get("fitness_goal", "General Fitness"),
                    f"{profile.get('workout_frequency', 4)}-Day Split",
                    json.dumps(plan_data)
                ))
                plan_id = cur.lastrowid
                conn.commit()
                conn.close()

                plan_data["id"] = plan_id
                self._send_json(plan_data)

            elif path == "/api/coach/chat":
                user_message = body.get("message", "").strip()
                if not user_message:
                    self._send_json({"error": "Empty message"}, status=400)
                    return

                conn = db.get_connection()
                cur = conn.cursor()
                
                cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
                user_row = cur.fetchone()
                profile = dict(user_row) if user_row else {}

                cur.execute("SELECT sender, message FROM chat_messages ORDER BY id DESC LIMIT 8")
                history = [dict(r) for r in reversed(cur.fetchall())]

                cur.execute("INSERT INTO chat_messages (user_id, sender, message) VALUES (?, 'user', ?)",
                            (profile.get("id", 1), user_message))
                conn.commit()

                coach_reply = ai_service.chat_coach(history, user_message, profile)

                cur.execute("INSERT INTO chat_messages (user_id, sender, message) VALUES (?, 'model', ?)",
                            (profile.get("id", 1), coach_reply))
                conn.commit()
                conn.close()

                self._send_json({"reply": coach_reply})

            elif path == "/api/analyze-form":
                image_data = body.get("image_base64", "")
                exercise_name = body.get("exercise_name", "Bodyweight Air Squat")
                telemetry = body.get("telemetry", {})

                if not image_data:
                    self._send_json({"error": "No image payload provided"}, status=400)
                    return

                if "," in image_data:
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)

                analysis = ai_service.analyze_movement_frame(image_bytes, exercise_name, telemetry)

                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO form_analyses (user_id, exercise_name, score, reps_detected, primary_feedback, detailed_analysis_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    1,
                    exercise_name,
                    analysis.get("overall_score", 85),
                    telemetry.get("reps", 0),
                    analysis.get("primary_feedback", ""),
                    json.dumps(analysis)
                ))
                analysis_id = cur.lastrowid
                conn.commit()
                conn.close()

                analysis["id"] = analysis_id
                self._send_json(analysis)

            elif path == "/api/nutrition/generate":
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                profile = dict(row) if row else {}
                profile.update(body)

                nutrition_plan = ai_service.generate_nutrition_plan(profile)

                cur.execute("""
                    INSERT INTO nutrition_plans (user_id, title, calories, protein_g, carbs_g, fats_g, plan_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.get("id", 1),
                    nutrition_plan.get("protocol_title", "AXIO Nutrition Blueprint"),
                    nutrition_plan.get("target_calories", 2400),
                    nutrition_plan.get("macros", {}).get("protein_g", 170),
                    nutrition_plan.get("macros", {}).get("carbs_g", 250),
                    nutrition_plan.get("macros", {}).get("fats_g", 70),
                    json.dumps(nutrition_plan)
                ))
                conn.commit()
                conn.close()

                self._send_json(nutrition_plan)

            elif path == "/api/workouts/log":
                title = body.get("title", "AXIO Session")
                duration = int(body.get("duration_minutes", 45))
                sets = body.get("sets", [])
                notes = body.get("notes", "")

                total_volume = sum(float(s.get("weight_kg", 0)) * int(s.get("reps", 0)) for s in sets)

                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO workout_logs (user_id, workout_title, duration_minutes, total_volume_kg, exercises_completed, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (1, title, duration, total_volume, len(sets), notes))
                log_id = cur.lastrowid

                for s in sets:
                    cur.execute("""
                        INSERT INTO workout_sets (log_id, exercise_name, set_number, weight_kg, reps, rpe)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (log_id, s.get("exercise_name", ""), s.get("set_number", 1),
                          s.get("weight_kg", 0), s.get("reps", 0), s.get("rpe", 8.0)))

                conn.commit()
                conn.close()

                self._send_json({
                    "success": True,
                    "log_id": log_id,
                    "total_volume_kg": total_volume,
                    "exercises_completed": len(sets)
                })

            else:
                self._send_json({"error": "Unknown POST route"}, status=404)

        except Exception as e:
            self._send_json({"error": str(e)}, status=500)

def run_server():
    db.init_db()
    with ThreadedHTTPServer(("0.0.0.0", PORT), AxioRequestHandler) as httpd:
        print(f"AXIO Server running on port {PORT}...")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
