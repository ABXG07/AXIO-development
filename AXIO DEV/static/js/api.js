// AXIO Client API Layer
const API = {
  async getProfile() {
    const res = await fetch('/api/profile');
    return res.json();
  },

  async updateProfile(profileData) {
    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });
    return res.json();
  },

  async getExercises(category = 'All') {
    const url = category && category !== 'All' ? `/api/exercises?category=${encodeURIComponent(category)}` : '/api/exercises';
    const res = await fetch(url);
    return res.json();
  },

  async generateWorkoutPlan(customParams = {}) {
    const res = await fetch('/api/workouts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customParams)
    });
    return res.json();
  },

  async getSavedWorkouts() {
    const res = await fetch('/api/workouts');
    return res.json();
  },

  async logWorkout(workoutData) {
    const res = await fetch('/api/workouts/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workoutData)
    });
    return res.json();
  },

  async sendCoachMessage(message) {
    const res = await fetch('/api/coach/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  },

  async getCoachHistory() {
    const res = await fetch('/api/coach/history');
    return res.json();
  },

  async analyzeMovementFrame(imageBase64, exerciseName, telemetry = {}) {
    const res = await fetch('/api/analyze-form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: imageBase64,
        exercise_name: exerciseName,
        telemetry: telemetry
      })
    });
    return res.json();
  },

  async generateNutritionPlan(customParams = {}) {
    const res = await fetch('/api/nutrition/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customParams)
    });
    return res.json();
  },

  async getNutritionPlan() {
    const res = await fetch('/api/nutrition');
    return res.json();
  },

  async getAnalytics() {
    const res = await fetch('/api/analytics');
    return res.json();
  }
};

window.API = API;
