import json
import os

EXERCISES = [
    {
        "id": "barbell-back-squat",
        "name": "Barbell Back Squat",
        "category": "Legs",
        "movement_pattern": "Squat",
        "difficulty": "Intermediate",
        "equipment": "Barbell / Rack",
        "primary_muscles": ["Quadriceps", "Gluteus Maximus"],
        "secondary_muscles": ["Hamstrings", "Adductors", "Erector Spinae", "Core"],
        "cues": [
            "Brace core with a deep diaphragmatic breath into the belt.",
            "Break simultaneously at the hips and knees.",
            "Descend until hip crease is parallel with or below the top of the knee.",
            "Drive through mid-foot while keeping chest upright and knees tracking over toes."
        ],
        "common_flaws": ["Knee valgus (caving inward)", "Chest collapse (good-morning squat)", "Heel lifting", "Inadequate depth"],
        "camera_analyzable": True,
        "key_angles": {"knee_min": 75, "knee_max": 170, "hip_min": 70, "torso_max_lean": 45}
    },
    {
        "id": "bodyweight-air-squat",
        "name": "Bodyweight Air Squat",
        "category": "Legs",
        "movement_pattern": "Squat",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
        "primary_muscles": ["Quadriceps", "Glutes"],
        "secondary_muscles": ["Hamstrings", "Core"],
        "cues": [
            "Feet shoulder-width apart, toes flared slightly 15-30 degrees.",
            "Reach hips back and sink down with arms forward for counterbalance.",
            "Keep weight evenly balanced across tripod of each foot.",
            "Stand tall and squeeze glutes at the apex."
        ],
        "common_flaws": ["Knees caving", "Excessive forward lean", "Rounds lower back at bottom"],
        "camera_analyzable": True,
        "key_angles": {"knee_min": 80, "knee_max": 175, "hip_min": 75}
    },
    {
        "id": "push-up",
        "name": "Standard Push-Up",
        "category": "Chest",
        "movement_pattern": "Horizontal Push",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
        "primary_muscles": ["Pectoralis Major", "Triceps Brachii"],
        "secondary_muscles": ["Anterior Deltoids", "Core / Rectus Abdominis", "Serratus Anterior"],
        "cues": [
            "Hands slightly wider than shoulder-width, fingers splayed.",
            "Maintain straight rigid plank from heels to crown of head.",
            "Elbows tracked at approximately 45 degrees to the torso (arrowhead shape).",
            "Lower chest until 2 inches above the floor, then press away forcefully."
        ],
        "common_flaws": ["Flaring elbows to 90 degrees", "Sagging hips / lumbar hyperextension", "Incomplete range of motion", "Head nodding down early"],
        "camera_analyzable": True,
        "key_angles": {"elbow_min": 75, "elbow_max": 170, "hip_spine_line": 180}
    },
    {
        "id": "barbell-bench-press",
        "name": "Barbell Bench Press",
        "category": "Chest",
        "movement_pattern": "Horizontal Push",
        "difficulty": "Intermediate",
        "equipment": "Barbell & Bench",
        "primary_muscles": ["Pectoralis Major", "Triceps Brachii"],
        "secondary_muscles": ["Anterior Deltoid", "Latissimus Dorsi (stabilizer)"],
        "cues": [
            "Retract and depress scapulae firmly into the bench.",
            "Establish active leg drive through flat feet.",
            "Unrack and lower bar smoothly to lower sternum in a controlled arc.",
            "Drive bar upwards and slightly back toward shoulder joints."
        ],
        "common_flaws": ["Bouncing bar off sternum", "Flaring elbows excessively wide", "Lifting hips off bench", "Uneven lockout"],
        "camera_analyzable": True,
        "key_angles": {"elbow_bottom": 80, "elbow_top": 175}
    },
    {
        "id": "romanian-deadlift",
        "name": "Romanian Deadlift (RDL)",
        "category": "Hamstrings & Glutes",
        "movement_pattern": "Hip Hinge",
        "difficulty": "Intermediate",
        "equipment": "Barbell or Dumbbells",
        "primary_muscles": ["Hamstrings", "Gluteus Maximus"],
        "secondary_muscles": ["Erector Spinae", "Latissimus Dorsi", "Forearm Flexors"],
        "cues": [
            "Soft bend in knees, fixed knee angle throughout the descent.",
            "Push hips back toward the wall behind you as if closing a car door.",
            "Keep barbell or dumbbells shaving down the front of your shins.",
            "Halt descent when hamstrings reach full stretch before lumbar spine bends."
        ],
        "common_flaws": ["Turning the hinge into a squat", "Rounding thoracic/lumbar spine", "Letting bar drift away from legs"],
        "camera_analyzable": True,
        "key_angles": {"knee_fixed": 160, "hip_hinge_min": 70}
    },
    {
        "id": "conventional-deadlift",
        "name": "Barbell Conventional Deadlift",
        "category": "Full Body / Back",
        "movement_pattern": "Hip Hinge / Pull",
        "difficulty": "Advanced",
        "equipment": "Barbell",
        "primary_muscles": ["Glutes", "Hamstrings", "Erector Spinae", "Trapezius"],
        "secondary_muscles": ["Quadriceps", "Forearms", "Lats", "Core"],
        "cues": [
            "Stance hip-width, barbell directly over midfoot.",
            "Hinge down and grip the bar without rolling it.",
            "Pull slack out of the bar, pull chest up, wedging hips into position.",
            "Drive floor away with legs, lock out hips and knees simultaneously."
        ],
        "common_flaws": ["Rounding lower back", "Bar drifting forward during pull", "Hyperextending spine at lockout"],
        "camera_analyzable": True,
        "key_angles": {"hip_start": 80, "knee_start": 110}
    },
    {
        "id": "standing-overhead-press",
        "name": "Overhead Barbell Press (OHP)",
        "category": "Shoulders",
        "movement_pattern": "Vertical Push",
        "difficulty": "Intermediate",
        "equipment": "Barbell",
        "primary_muscles": ["Anterior Deltoids", "Triceps Brachii"],
        "secondary_muscles": ["Lateral Deltoid", "Upper Trapezius", "Core", "Glutes"],
        "cues": [
            "Squeeze glutes and brace abdominal wall tight.",
            "Elbows slightly in front of bar in the front rack position.",
            "Tilt head back slightly to clear the chin as bar travels straight up.",
            "Push head through the window at top lockout directly over midfoot."
        ],
        "common_flaws": ["Excessive lumbar arching (leaning back)", "Bar looping forward around face", "Incomplete shoulder elevation lockout"],
        "camera_analyzable": True,
        "key_angles": {"elbow_top": 175, "torso_lean_max": 15}
    },
    {
        "id": "pull-up",
        "name": "Strict Pull-Up",
        "category": "Back",
        "movement_pattern": "Vertical Pull",
        "difficulty": "Intermediate",
        "equipment": "Pull-Up Bar",
        "primary_muscles": ["Latissimus Dorsi", "Biceps Brachii"],
        "secondary_muscles": ["Brachialis", "Rhomboids", "Lower Trapezius", "Core"],
        "cues": [
            "Overhand grip just outside shoulder width.",
            "Start from a dead hang with active shoulders engaged.",
            "Drive elbows straight down toward your hip pockets.",
            "Clear chin over the bar with minimal kipping or body swing."
        ],
        "common_flaws": ["Kicking legs or kipping", "Half reps (not reaching full extension)", "Rolling shoulders forward at apex"],
        "camera_analyzable": True,
        "key_angles": {"elbow_flexion_top": 60, "elbow_extension_bottom": 175}
    },
    {
        "id": "barbell-bent-over-row",
        "name": "Barbell Bent-Over Row",
        "category": "Back",
        "movement_pattern": "Horizontal Pull",
        "difficulty": "Intermediate",
        "equipment": "Barbell",
        "primary_muscles": ["Latissimus Dorsi", "Rhomboids", "Mid/Lower Trapezius"],
        "secondary_muscles": ["Posterior Deltoids", "Biceps", "Spinal Erectors"],
        "cues": [
            "Hinge torso forward to roughly 45 to 60 degrees relative to floor.",
            "Keep neutral neck and flat spine braced tight.",
            "Row bar towards lower ribcage/belly button by pulling through elbows.",
            "Squeeze shoulder blades together at apex, avoid momentum bouncing."
        ],
        "common_flaws": ["Standing up too tall using body momentum", "Rounding thoracic spine", "Jerking weight with lower back"],
        "camera_analyzable": True,
        "key_angles": {"torso_angle": 50, "elbow_retraction": 85}
    },
    {
        "id": "dumbbell-walking-lunge",
        "name": "Walking Dumbbell Lunges",
        "category": "Legs",
        "movement_pattern": "Unilateral / Lunge",
        "difficulty": "Intermediate",
        "equipment": "Dumbbells",
        "primary_muscles": ["Quadriceps", "Gluteus Maximus"],
        "secondary_muscles": ["Hamstrings", "Calves", "Core Stabilizers"],
        "cues": [
            "Take an exaggerated stride forward.",
            "Lower back knee smoothly until hovering 1 inch from floor.",
            "Front shin remains relatively vertical or tracks slightly over middle toes.",
            "Drive through front heel to step smoothly into next stride."
        ],
        "common_flaws": ["Taking too short a step crashing front knee", "Torso collapsing forward", "Inward knee collapse"],
        "camera_analyzable": True,
        "key_angles": {"front_knee_depth": 90, "back_knee_depth": 90}
    },
    {
        "id": "standing-dumbbell-bicep-curl",
        "name": "Standing Dumbbell Bicep Curl",
        "category": "Arms",
        "movement_pattern": "Arm Flexion",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
        "primary_muscles": ["Biceps Brachii"],
        "secondary_muscles": ["Brachialis", "Brachioradialis"],
        "cues": [
            "Stand tall, pin elbows against ribcage.",
            "Supinate palms upward as you curl dumbbells smoothly.",
            "Contract biceps tightly at apex without swinging torso.",
            "Lower under strict eccentric control for 2-3 seconds."
        ],
        "common_flaws": ["Swinging hips for momentum", "Elbows drifting far forward", "Dropping weights quickly"],
        "camera_analyzable": True,
        "key_angles": {"elbow_curl_min": 45, "elbow_curl_max": 170}
    },
    {
        "id": "plank",
        "name": "Forearm Core Plank",
        "category": "Core",
        "movement_pattern": "Anti-Extension",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
        "primary_muscles": ["Rectus Abdominis", "Transverse Abdominis"],
        "secondary_muscles": ["Glutes", "Quadriceps", "Shoulders"],
        "cues": [
            "Forearms parallel on floor, elbows directly beneath shoulders.",
            "Tuck pelvis slightly into a hollow-body posterior pelvic tilt.",
            "Squeeze glutes and quads intensely, creating total body tension.",
            "Maintain unbroken line from heels to ears; breathe rhythmically."
        ],
        "common_flaws": ["Sagging hips / arched lumbar spine", "Piking hips up toward ceiling", "Holding breath"],
        "camera_analyzable": True,
        "key_angles": {"torso_straight_line": 180}
    },
    {
        "id": "bulgarian-split-squat",
        "name": "Bulgarian Split Squat",
        "category": "Legs",
        "movement_pattern": "Unilateral Squat",
        "difficulty": "Intermediate",
        "equipment": "Dumbbells & Bench",
        "primary_muscles": ["Quadriceps", "Gluteus Maximus"],
        "secondary_muscles": ["Hamstrings", "Adductor Magnus"],
        "cues": [
            "Rear foot laces rested flat on bench.",
            "Sink down and slightly back into front hip until front thigh is parallel.",
            "Maintain slight forward torso lean to load target glute and quad.",
            "Drive through midfoot of the lead leg to return to starting position."
        ],
        "common_flaws": ["Pushing through rear leg", "Front knee caving inward", "Excessive arching of lower back"],
        "camera_analyzable": False,
        "key_angles": {"lead_knee_depth": 90}
    },
    {
        "id": "dumbbell-lateral-raise",
        "name": "Dumbbell Lateral Raise",
        "category": "Shoulders",
        "movement_pattern": "Shoulder Abduction",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
        "primary_muscles": ["Lateral Deltoid"],
        "secondary_muscles": ["Supraspinatus", "Upper Trapezius"],
        "cues": [
            "Slight forward torso hinge, soft bend in elbows.",
            "Raise arms in the scapular plane (approx 30 degrees forward from side).",
            "Lead with elbows, raising until upper arms are parallel to floor.",
            "Avoid shrugging shoulders up toward ears."
        ],
        "common_flaws": ["Using body sway to jerk weights", "Raising thumbs higher than pinkies", "Shrugging traps"],
        "camera_analyzable": True,
        "key_angles": {"arm_abduction_peak": 90}
    },
    {
        "id": "cable-tricep-pushdown",
        "name": "Cable Triceps Pushdown",
        "category": "Arms",
        "movement_pattern": "Elbow Extension",
        "difficulty": "Beginner",
        "equipment": "Cable Machine",
        "primary_muscles": ["Triceps Brachii (All 3 heads)"],
        "secondary_muscles": ["Forearm Extensors"],
        "cues": [
            "Pin elbows tightly by your sides.",
            "Extend arms straight down, spreading rope or pressing bar at bottom.",
            "Squeeze triceps for a full second at full extension.",
            "Allow forearms to rise to 90 degrees before next rep without elbows drifting."
        ],
        "common_flaws": ["Flaring elbows out", "Leaning over the weight using bodyweight", "Partial extension"],
        "camera_analyzable": False,
        "key_angles": {"elbow_extension": 175}
    },
    {
        "id": "lat-pulldown",
        "name": "Wide-Grip Lat Pulldown",
        "category": "Back",
        "movement_pattern": "Vertical Pull",
        "difficulty": "Beginner",
        "equipment": "Cable Lat Pulldown Machine",
        "primary_muscles": ["Latissimus Dorsi"],
        "secondary_muscles": ["Biceps Brachii", "Teres Major", "Rhomboids"],
        "cues": [
            "Grip slightly wider than shoulder width.",
            "Depress shoulders before initiating pull.",
            "Drive elbows down and back toward ribs, touching bar to upper clavicle.",
            "Control weight up to full overhead stretch."
        ],
        "common_flaws": ["Leaning excessively far back", "Pulling bar down with wrist curl", "Jerking the stack"],
        "camera_analyzable": False,
        "key_angles": {"elbow_flexion": 70}
    },
    {
        "id": "dumbbell-incline-press",
        "name": "Incline Dumbbell Press",
        "category": "Chest",
        "movement_pattern": "Incline Push",
        "difficulty": "Intermediate",
        "equipment": "Incline Bench & Dumbbells",
        "primary_muscles": ["Pectoralis Major (Clavicular Head / Upper Chest)"],
        "secondary_muscles": ["Anterior Deltoid", "Triceps Brachii"],
        "cues": [
            "Set bench to 30 degrees incline.",
            "Retract shoulder blades and plant feet firmly.",
            "Lower dumbbells with control, feeling deep stretch across upper chest.",
            "Press dumbbells upward and inward without clanking at top."
        ],
        "common_flaws": ["Bench angle too steep (turns into shoulder press)", "Flaring elbows 90 degrees", "Bouncing at bottom"],
        "camera_analyzable": False,
        "key_angles": {"elbow_depth": 85}
    },
    {
        "id": "hanging-leg-raise",
        "name": "Hanging Leg / Knee Raise",
        "category": "Core",
        "movement_pattern": "Spinal Flexion / Hip Flexion",
        "difficulty": "Advanced",
        "equipment": "Pull-Up Bar",
        "primary_muscles": ["Rectus Abdominis", "Iliopsoas"],
        "secondary_muscles": ["Obliques", "Grip Strength"],
        "cues": [
            "Hang with active shoulders, eliminate swinging.",
            "Curl pelvis forward and up as you lift knees/toes toward chest.",
            "Focus on rounding lower spine to engage lower rectus abdominis.",
            "Lower slowly without using pendulum momentum."
        ],
        "common_flaws": ["Swinging body back and forth", "Using only hip flexors without posterior pelvic tilt"],
        "camera_analyzable": False,
        "key_angles": {"hip_flexion": 90}
    },
    {
        "id": "barbell-hip-thrust",
        "name": "Barbell Hip Thrust",
        "category": "Glutes & Hamstrings",
        "movement_pattern": "Hip Extension",
        "difficulty": "Intermediate",
        "equipment": "Barbell & Bench / Pad",
        "primary_muscles": ["Gluteus Maximus"],
        "secondary_muscles": ["Hamstrings", "Quadriceps", "Adductors"],
        "cues": [
            "Upper back resting on edge of bench, barbell cushioned over hip crease.",
            "Feet shoulder-width apart, shins vertical at top lockout.",
            "Drive through heels and squeeze glutes hard at top.",
            "Keep chin tucked and ribs down to avoid lumbar hyperextension."
        ],
        "common_flaws": ["Hyperextending lower back at top", "Placing feet too far forward or back", "Incomplete hip lockout"],
        "camera_analyzable": False,
        "key_angles": {"hip_lockout": 180}
    },
    {
        "id": "dumbbell-hammer-curl",
        "name": "Dumbbell Neutral-Grip Hammer Curl",
        "category": "Arms",
        "movement_pattern": "Elbow Flexion",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
        "primary_muscles": ["Brachialis", "Brachioradialis"],
        "secondary_muscles": ["Biceps Brachii"],
        "cues": [
            "Maintain palms facing inward (neutral grip) throughout entire motion.",
            "Lock elbows at sides, curl dumbbells up toward shoulder level.",
            "Squeeze brachialis firmly at top, descend with 2-second eccentric control."
        ],
        "common_flaws": ["Swinging torso", "Flaring elbows forward"],
        "camera_analyzable": True,
        "key_angles": {"elbow_curl_min": 45, "elbow_curl_max": 170}
    }
]

def save_exercises():
    path = os.path.join(os.path.dirname(__file__), "data", "exercises.json")
    with open(path, "w") as f:
        json.dump(EXERCISES, f, indent=2)
    print(f"Saved {len(EXERCISES)} exercises to {path}")

if __name__ == "__main__":
    save_exercises()
