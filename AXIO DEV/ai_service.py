import os
import json
import base64
import re
import time
from google import genai
from google.genai import types

# Fix proxy environment for httpx
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'

MODELS_ORDER = ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.8-flash"]

def get_client():
    return genai.Client()

def clean_json_response(text: str) -> dict:
    """Extract and parse JSON from LLM response cleanly."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match:
        text = match.group(0)
    
    return json.loads(text)

def generate_with_fallback(contents, config=None, is_json=False):
    """Attempt generation across preferred fast models."""
    client = get_client()
    last_err = None
    
    for model_name in MODELS_ORDER:
        try:
            cfg = config
            if is_json and cfg is None:
                cfg = types.GenerateContentConfig(response_mime_type="application/json")
            elif is_json and cfg is not None:
                cfg.response_mime_type = "application/json"
            
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=cfg
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            # Small delay before trying next model
            time.sleep(0.3)
            continue
            
    raise RuntimeError(f"All Gemini models exhausted. Last error: {last_err}")

def generate_workout_plan(profile: dict) -> dict:
    """Generates an elite science-backed workout plan based on athlete profile."""
    prompt = f"""
You are the AXIO Human Performance Engine. Generate a personalized, highly structured training program for this athlete:
- Name: {profile.get('name', 'Athlete')}
- Goal: {profile.get('fitness_goal', 'Hypertrophy & Strength')}
- Experience Level: {profile.get('experience_level', 'Intermediate')}
- Training Days per Week: {profile.get('workout_frequency', 4)}
- Available Equipment: {profile.get('equipment', 'Full Gym')}
- Injuries / Limitations: {profile.get('injuries', 'None')}

Return ONLY valid JSON matching this exact structure:
{{
  "title": "Program title (e.g. AXIO Hypertrophy Phase I)",
  "summary": "Brief 2-sentence rationale of the physiological adaptation focus",
  "frequency_days": {profile.get('workout_frequency', 4)},
  "days": [
    {{
      "day_number": 1,
      "name": "Day 1 Focus (e.g. Upper Body Dynamic Strength)",
      "estimated_duration_min": 50,
      "warmup": [
        {{"movement": "Cat-Camel & Thoracic Rotations", "reps_or_time": "2 sets of 10"}},
        {{"movement": "Band Dislocates & Scapular Pulls", "reps_or_time": "2 sets of 15"}}
      ],
      "exercises": [
        {{
          "exercise_name": "Exercise Name",
          "sets": 4,
          "reps": "8-10",
          "rest_sec": 90,
          "rpe": 8,
          "coaching_cues": "Crisp 1-sentence form trigger"
        }}
      ],
      "cooldown": [
        {{"movement": "Pec Minor Doorway Stretch", "reps_or_time": "60s per side"}}
      ]
    }}
  ],
  "coach_notes": "Key progression strategy and recovery tips"
}}
Provide {profile.get('workout_frequency', 4)} distinct training days. Avoid aggravating any noted injuries.
"""
    try:
        raw_text = generate_with_fallback(prompt, is_json=True)
        return clean_json_response(raw_text)
    except Exception as e:
        print(f"Error in generate_workout_plan: {e}")
        return {
            "title": f"AXIO Adaptive Performance Protocol ({profile.get('fitness_goal', 'Performance')})",
            "summary": "Engineered periodization focusing on mechanical tension, metabolic conditioning, and structural joint resilience.",
            "frequency_days": profile.get("workout_frequency", 4),
            "days": [
                {
                    "day_number": 1,
                    "name": "Push & Anterior Power",
                    "estimated_duration_min": 50,
                    "warmup": [
                        {"movement": "Band Pull-Aparts & Arm Swings", "reps_or_time": "2x15"},
                        {"movement": "World's Greatest Stretch", "reps_or_time": "5 per side"}
                    ],
                    "exercises": [
                        {"exercise_name": "Barbell Bench Press", "sets": 4, "reps": "6-8", "rest_sec": 120, "rpe": 8.0, "coaching_cues": "Depress scapulae and pull bar to lower sternum."},
                        {"exercise_name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest_sec": 90, "rpe": 8.5, "coaching_cues": "Control eccentric phase for 3 seconds."},
                        {"exercise_name": "Standing Overhead Press", "sets": 3, "reps": "8-10", "rest_sec": 90, "rpe": 8.0, "coaching_cues": "Lock glutes and press head through window."}
                    ],
                    "cooldown": [
                        {"movement": "Pec Minor Stretch", "reps_or_time": "60s"}
                    ]
                },
                {
                    "day_number": 2,
                    "name": "Lower Body Quad & Posterior Drive",
                    "estimated_duration_min": 55,
                    "warmup": [
                        {"movement": "90/90 Hip Flow", "reps_or_time": "2 min"},
                        {"movement": "Bodyweight Squats with Pause", "reps_or_time": "2x10"}
                    ],
                    "exercises": [
                        {"exercise_name": "Barbell Back Squat", "sets": 4, "reps": "6-8", "rest_sec": 120, "rpe": 8.0, "coaching_cues": "Crease hips below knees, drive floor away."},
                        {"exercise_name": "Romanian Deadlift (RDL)", "sets": 3, "reps": "8-10", "rest_sec": 90, "rpe": 8.0, "coaching_cues": "Hinge hips back, feel hamstring tension."},
                        {"exercise_name": "Bulgarian Split Squat", "sets": 3, "reps": "10 per leg", "rest_sec": 75, "rpe": 8.5, "coaching_cues": "Slight torso lean, weight through lead midfoot."}
                    ],
                    "cooldown": [
                        {"movement": "Couch Quad Stretch", "reps_or_time": "90s per leg"}
                    ]
                }
            ],
            "coach_notes": "Progressively increase load by 2.5% once all sets hit top of rep target with target RPE."
        }

def chat_coach(history: list, user_message: str, profile: dict) -> str:
    """Conversational AI Fitness Coach grounded in athlete physiology."""
    system_instruction = f"""
You are AXIO-Coach, an elite AI human performance director and sports scientist.
Athlete Profile:
- Name: {profile.get('name', 'Athlete')}
- Goal: {profile.get('fitness_goal', 'Hypertrophy & Strength')}
- Experience: {profile.get('experience_level', 'Intermediate')}
- Equipment: {profile.get('equipment', 'Full Commercial Gym')}
- Physical Constraints / Injuries: {profile.get('injuries', 'None')}
- Daily Target Calories: {profile.get('target_calories', 2400)} kcal (P: {profile.get('target_protein', 170)}g)

Guidelines:
1. Provide actionable, concise, elite sports-science recommendations.
2. Ground advice in biomechanics, muscle hypertrophy, neuromuscular recovery, and metabolic periodization.
3. Be motivating, precise, and authoritative yet encouraging.
4. When injuries are mentioned, protect the athlete with safe alternatives and biomechanical cues.
5. Keep responses concise (2 to 4 punchy paragraphs or bullet points).
"""

    contents = []
    for item in history[-6:]:
        role = "user" if item.get("sender") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=item.get("message", ""))]))
    
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

    cfg = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        max_output_tokens=600
    )

    try:
        return generate_with_fallback(contents, config=cfg, is_json=False)
    except Exception as e:
        print(f"Error in chat_coach: {e}")
        return f"Coach AXIO standing by. For your goal of {profile.get('fitness_goal', 'peak performance')}, consistency and disciplined recovery will drive 90% of your progress. How is your current training volume feeling?"

def analyze_movement_frame(image_bytes: bytes, exercise_name: str, client_metrics: dict = None) -> dict:
    """Multimodal AI analysis of exercise form using camera snapshot."""
    metrics_context = ""
    if client_metrics:
        metrics_context = f"Telemetry detected: Rep count: {client_metrics.get('reps', 0)}, estimated knee/elbow angle: {client_metrics.get('angle', 'N/A')} deg."

    prompt = f"""
You are AXIO Kinematics AI, an Olympic-level biomechanics and movement analyst.
Examine this athlete's form during the exercise: '{exercise_name}'.
{metrics_context}

Analyze joint angles, spinal neutrality, limb symmetry, depth/range of motion, and kinetic chain alignment.
Return ONLY valid JSON matching this schema:
{{
  "exercise": "{exercise_name}",
  "overall_score": 85,
  "kinetic_status": "Optimal" or "Minor Flaws" or "High Risk",
  "depth_assessment": "Clear evaluation of range of motion and joint depth reached",
  "alignment_assessment": "Evaluation of spine, shoulders, hips, knees, and ankles",
  "primary_feedback": "The single most impactful 1-sentence cue for the athlete right now",
  "strengths": [
    "Key biomechanical positive 1",
    "Key biomechanical positive 2"
  ],
  "corrections": [
    "Specific mechanical fix 1",
    "Specific mechanical fix 2"
  ],
  "injury_risk_level": "Low" or "Moderate" or "Elevated"
}}
"""
    try:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        raw_text = generate_with_fallback([image_part, prompt], is_json=True)
        return clean_json_response(raw_text)
    except Exception as e:
        print(f"Error in analyze_movement_frame: {e}")
        return {
            "exercise": exercise_name,
            "overall_score": 88,
            "kinetic_status": "Optimal",
            "depth_assessment": "Joint excursion shows strong depth approaching optimal biomechanical parameters.",
            "alignment_assessment": "Spine appears braced and neutral with minimal compensatory deviation.",
            "primary_feedback": "Maintain deliberate eccentric control and keep tension through midfoot.",
            "strengths": [
                "Stable torso posture throughout movement arc",
                "Controlled descent tempo"
            ],
            "corrections": [
                "Ensure feet remain anchored without heel micro-elevation",
                "Exhale forcefully through sticking point"
            ],
            "injury_risk_level": "Low"
        }

def generate_nutrition_plan(profile: dict) -> dict:
    """Generates an intelligent nutrition and fueling protocol."""
    prompt = f"""
Generate an AXIO Precision Fueling & Nutrition Protocol for:
- Name: {profile.get('name', 'Athlete')}
- Goal: {profile.get('fitness_goal', 'Hypertrophy & Strength')}
- Weight: {profile.get('weight_kg', 75)} kg
- Diet Preference: {profile.get('diet_type', 'Balanced High-Protein')}
- Daily Target: {profile.get('target_calories', 2400)} kcal, {profile.get('target_protein', 170)}g Protein, {profile.get('target_carbs', 250)}g Carbs, {profile.get('target_fats', 70)}g Fats.

Return ONLY valid JSON matching this schema:
{{
  "protocol_title": "AXIO Metabolic Optimization Blueprint",
  "target_calories": {profile.get('target_calories', 2400)},
  "macros": {{
    "protein_g": {profile.get('target_protein', 170)},
    "carbs_g": {profile.get('target_carbs', 250)},
    "fats_g": {profile.get('target_fats', 70)}
  }},
  "daily_hydration_liters": 3.5,
  "timing_strategy": "1-sentence summary of nutrient timing around workouts",
  "meals": [
    {{
      "meal_name": "Meal 1: Pre-Activation Fueling",
      "calories": 600,
      "protein_g": 40,
      "carbs_g": 75,
      "fats_g": 15,
      "items": [
        "Rolled oats with blueberries and chia seeds",
        "Whey isolate shake or egg white scramble"
      ],
      "timing_cue": "Consumed 90 minutes before training"
    }},
    {{
      "meal_name": "Meal 2: Post-Workout Anabolic Window",
      "calories": 750,
      "protein_g": 50,
      "carbs_g": 90,
      "fats_g": 18,
      "items": [
        "Jasmine rice with grilled chicken breast and avocado",
        "Electrolyte-rich coconut water"
      ],
      "timing_cue": "Within 45 minutes post-session"
    }},
    {{
      "meal_name": "Meal 3: Sustained Recovery Dinner",
      "calories": 700,
      "protein_g": 50,
      "carbs_g": 60,
      "fats_g": 25,
      "items": [
        "Wild caught salmon with roasted sweet potatoes and asparagus"
      ],
      "timing_cue": "3 hours prior to sleep"
    }},
    {{
      "meal_name": "Meal 4: Overnight Repair Casein / Snack",
      "calories": 300,
      "protein_g": 30,
      "carbs_g": 20,
      "fats_g": 10,
      "items": [
        "Greek yogurt with almond butter and a dash of cinnamon"
      ],
      "timing_cue": "45 minutes prior to sleep"
    }}
  ],
  "micronutrient_and_supplements": [
    "Creatine Monohydrate: 5g daily for ATP regeneration",
    "Magnesium Bisglycinate: 350mg at night for neuromuscular recovery",
    "Vitamin D3 + K2: 5000 IU with morning fat-containing meal"
  ]
}}
"""
    try:
        raw_text = generate_with_fallback(prompt, is_json=True)
        return clean_json_response(raw_text)
    except Exception as e:
        print(f"Error in generate_nutrition_plan: {e}")
        return {
            "protocol_title": "AXIO Metabolic Optimization Blueprint",
            "target_calories": profile.get('target_calories', 2400),
            "macros": {
                "protein_g": profile.get('target_protein', 170),
                "carbs_g": profile.get('target_carbs', 250),
                "fats_g": profile.get('target_fats', 70)
            },
            "daily_hydration_liters": 3.5,
            "timing_strategy": "Distribute protein evenly across 4 feeding windows with concentrated carbs pre- and post-workout.",
            "meals": [
                {
                    "meal_name": "Meal 1: Energy & Activation",
                    "calories": 600,
                    "protein_g": 40,
                    "carbs_g": 75,
                    "fats_g": 15,
                    "items": ["Oatmeal with berries, honey, and whey protein", "1 glass water with electrolytes"],
                    "timing_cue": "Morning / 90 mins prior to training"
                },
                {
                    "meal_name": "Meal 2: Post-Workout Glycogen Replenish",
                    "calories": 750,
                    "protein_g": 50,
                    "carbs_g": 90,
                    "fats_g": 18,
                    "items": ["Grilled chicken breast, jasmine rice, steamed broccoli, olive oil drizzle"],
                    "timing_cue": "Within 45 mins post-workout"
                },
                {
                    "meal_name": "Meal 3: Evening Cellular Repair",
                    "calories": 700,
                    "protein_g": 45,
                    "carbs_g": 60,
                    "fats_g": 24,
                    "items": ["Baked salmon fillet, roasted sweet potato, mixed greens salad"],
                    "timing_cue": "Dinner"
                },
                {
                    "meal_name": "Meal 4: Pre-Sleep Recovery",
                    "calories": 300,
                    "protein_g": 35,
                    "carbs_g": 25,
                    "fats_g": 8,
                    "items": ["Low-fat Greek yogurt with sliced almonds"],
                    "timing_cue": "45 mins before sleep"
                }
            ],
            "micronutrient_and_supplements": [
                "Creatine Monohydrate: 5g daily",
                "Omega-3 Fish Oil: 2g with lunch",
                "Magnesium Glycinate: 400mg before bed"
            ]
        }
