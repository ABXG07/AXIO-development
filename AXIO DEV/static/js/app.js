/**
 * AXIO – Universal Fitness & Human Performance Platform
 * Core Application Controller (app.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

const VIEW_METADATA = {
  dashboard: { title: 'Dashboard', breadcrumb: 'AXIO / Intelligence Hub' },
  coach: { title: 'AI Coach', breadcrumb: 'AXIO / Kinetic & Physiological Chat' },
  workouts: { title: 'Workout Planner', breadcrumb: 'AXIO / Adaptive Periodization' },
  movement: { title: 'Movement Studio', breadcrumb: 'AXIO / Real-Time Biomechanical Vision' },
  nutrition: { title: 'Nutrition Blueprint', breadcrumb: 'AXIO / Precision Metabolic Fueling' },
  analytics: { title: 'Performance Progress', breadcrumb: 'AXIO / Biometric Trendlines' },
  exercises: { title: 'Exercise Library', breadcrumb: 'AXIO / Biomechanical Movement Catalog' },
  profile: { title: 'Athlete Profile', breadcrumb: 'AXIO / Baseline Biometrics' }
};

let currentProfile = null;

async function initApp() {
  // 1. Setup Hash Router
  window.addEventListener('hashchange', handleHashRouting);
  
  // 2. Initial view setup based on hash or default to dashboard
  const initialHash = window.location.hash.replace('#', '') || 'dashboard';
  navigateTo(initialHash, false);

  // 3. Set Dynamic Time-based Greeting
  setDynamicGreeting();

  // 4. Load Data from Backend APIs
  await loadUserData();
  await loadDashboardWorkout();
  await loadAnalyticsSummary();

  // 5. Animate Performance Score Radial Gauge
  animateScoreGauge(94);
}

/**
 * Handle SPA view switching
 */
function navigateTo(viewName, updateHash = true) {
  if (!VIEW_METADATA[viewName]) {
    viewName = 'dashboard';
  }

  // Update hash if requested
  if (updateHash) {
    window.location.hash = viewName;
  }

  // Update topbar title and breadcrumb
  const meta = VIEW_METADATA[viewName];
  const titleEl = document.getElementById('page-title');
  const breadcrumbEl = document.getElementById('page-breadcrumb');
  if (titleEl) titleEl.textContent = meta.title;
  if (breadcrumbEl) breadcrumbEl.textContent = meta.breadcrumb;

  // Toggle active view panes
  document.querySelectorAll('.view-pane').forEach(pane => {
    pane.classList.remove('active');
  });
  const targetPane = document.getElementById(`view-${viewName}`);
  if (targetPane) {
    targetPane.classList.add('active');
  }

  // Update Desktop Sidebar Active States
  document.querySelectorAll('.app-sidebar .nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Update Mobile Bottom Nav Active States
  document.querySelectorAll('.mobile-bottom-nav .mobile-nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Close mobile sidebar if open
  toggleSidebar(false);

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function handleHashRouting() {
  const hash = window.location.hash.replace('#', '') || 'dashboard';
  navigateTo(hash, false);
}

/**
 * Mobile Sidebar Drawer Toggler
 */
function toggleSidebar(open) {
  const sidebar = document.getElementById('app-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (!sidebar || !overlay) return;

  if (open) {
    sidebar.classList.add('open');
    overlay.classList.add('open');
  } else {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  }
}

/**
 * Notification Modal Controls
 */
function openNotificationsModal() {
  const modal = document.getElementById('notif-modal');
  if (modal) modal.classList.add('open');
}

function closeNotificationsModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const modal = document.getElementById('notif-modal');
  if (modal) modal.classList.remove('open');
}

/**
 * Dynamic Greeting based on athlete's local time
 */
function setDynamicGreeting(athleteName = 'Athlete') {
  const greetingEl = document.getElementById('dash-greeting');
  if (!greetingEl) return;

  const hour = new Date().getHours();
  let timeStr = 'Good morning';
  if (hour >= 12 && hour < 17) {
    timeStr = 'Good afternoon';
  } else if (hour >= 17 || hour < 5) {
    timeStr = 'Good evening';
  }

  greetingEl.textContent = `${timeStr}, ${athleteName}.`;
}

/**
 * Load user profile from existing /api/profile
 */
async function loadUserData() {
  try {
    const profile = await window.API.getProfile();
    if (profile && !profile.error) {
      currentProfile = profile;
      
      // Update topbar display name
      const nameEl = document.getElementById('user-nav-name');
      if (nameEl && profile.name) {
        nameEl.textContent = profile.name;
      }

      // Update avatar initials
      const avatarEl = document.getElementById('user-avatar-text');
      if (avatarEl && profile.name) {
        const parts = profile.name.trim().split(' ');
        const initials = parts.length > 1 
          ? (parts[0][0] + parts[1][0]).toUpperCase() 
          : profile.name.substring(0, 2).toUpperCase();
        avatarEl.textContent = initials;
      }

      // Set personalized greeting
      if (profile.name) {
        setDynamicGreeting(profile.name.split(' ')[0]);
      }
    }
  } catch (err) {
    console.warn('Profile fetch note (using demo profile):', err);
  }
}

/**
 * Load Today's Workout from existing /api/workouts
 */
async function loadDashboardWorkout() {
  try {
    const workouts = await window.API.getSavedWorkouts();
    if (workouts && workouts.length > 0) {
      const latest = workouts[0];
      const plan = latest.plan || {};
      const days = plan.days || [];
      if (days.length > 0) {
        const day1 = days[0];
        
        // Update Workout Card in Dashboard
        const nameEl = document.getElementById('dash-workout-name');
        const tagEl = document.getElementById('workout-day-tag');
        const durEl = document.getElementById('dash-workout-duration');
        const miniList = document.getElementById('dash-exercise-mini-list');

        if (nameEl && day1.name) nameEl.textContent = day1.name;
        if (tagEl && latest.goal) tagEl.textContent = latest.goal.toUpperCase();
        if (durEl && day1.estimated_duration_min) durEl.textContent = `${day1.estimated_duration_min} mins`;

        if (miniList && day1.exercises && day1.exercises.length > 0) {
          miniList.innerHTML = day1.exercises.slice(0, 4).map(ex => `
            <div class="mini-exercise-item">
              <div class="exercise-name-left">
                <span class="exercise-bullet"></span>
                <span>${ex.exercise_name}</span>
              </div>
              <span class="exercise-sets-reps">${ex.sets} sets × ${ex.reps} reps</span>
            </div>
          `).join('');
        }
      }
    }
  } catch (err) {
    console.warn('Workouts fetch note (using demo routine):', err);
  }
}

/**
 * Load Analytics from existing /api/analytics
 */
async function loadAnalyticsSummary() {
  try {
    const data = await window.API.getAnalytics();
    if (data && data.summary) {
      const streakEl = document.getElementById('stat-streak');
      if (streakEl && data.summary.streak_days) {
        streakEl.textContent = `${data.summary.streak_days}d`;
      }
    }
  } catch (err) {
    console.warn('Analytics fetch note:', err);
  }
}

/**
 * Performance Gauge Radial Progress Animation
 */
function animateScoreGauge(score = 94) {
  const circle = document.getElementById('radial-score-circle');
  if (!circle) return;

  // Circumference for r=60 is 2 * PI * 60 ≈ 376.99
  const circumference = 377;
  const offset = circumference - (score / 100) * circumference;
  
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${circumference}`;

  setTimeout(() => {
    circle.style.strokeDashoffset = `${offset}`;
  }, 150);
}

/**
 * Global Search Filter Handler
 */
function handleGlobalSearch(event) {
  const query = event.target.value.toLowerCase().trim();
  if (event.key === 'Enter' && query) {
    // If searching for exercises, jump to exercises view
    if (query.includes('squat') || query.includes('press') || query.includes('deadlift') || query.includes('curl') || query.includes('row')) {
      navigateTo('exercises');
    } else if (query.includes('coach') || query.includes('pain') || query.includes('injur') || query.includes('tempo')) {
      navigateTo('coach');
    } else if (query.includes('diet') || query.includes('protein') || query.includes('calorie') || query.includes('macro')) {
      navigateTo('nutrition');
    }
  }
}

// Export functions to window for global access
window.navigateTo = navigateTo;
window.toggleSidebar = toggleSidebar;
window.openNotificationsModal = openNotificationsModal;
window.closeNotificationsModal = closeNotificationsModal;
window.handleGlobalSearch = handleGlobalSearch;
