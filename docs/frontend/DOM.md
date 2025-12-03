# Document Object Model (DOM) - Frontend Architecture

## Overview
This document outlines the Document Object Model structure and JavaScript interactions for the Tamagotchi Tracker frontend application.

---

## Table of Contents
1. [Application Structure](#application-structure)
2. [Page-Specific DOM](#page-specific-dom)
3. [Shared Components](#shared-components)
4. [JavaScript Interactions](#javascript-interactions)
5. [API Integration](#api-integration)
6. [State Management](#state-management)

---

## Application Structure

### Base Template (`base.html`)
The base template provides the foundational DOM structure inherited by all pages.

```
html
└── head
    ├── meta (charset, viewport)
    ├── title (dynamic per page)
    ├── link (CSS: style.css)
    └── link (favicon)
└── body
    ├── nav.navbar
    │   └── div.nav-container
    │       ├── a.nav-logo (Tamagotchi Tracker)
    │       └── ul.nav-menu
    │           ├── li > a.nav-link (Home)
    │           ├── li > a.nav-link (Water)
    │           ├── li > a.nav-link (Food)
    │           ├── li > a.nav-link (Gym)
    │           └── li > a.nav-link (Logout)
    │
    ├── div.container
    │   └── [Page-specific content block]
    │
    └── script (main.js)
    └── [Page-specific scripts block]
```

**Key Elements:**
- **Navigation Bar**: Fixed navigation with links to all major sections
- **Container**: Main content area for page-specific content
- **Flash Messages**: Alert notifications rendered server-side

---

## Page-Specific DOM

### 1. Login Page (`login.html`)

```
div.auth-container
└── div.auth-box
    ├── h1 (🐾 Welcome Back!)
    ├── p.subtitle (Login to check on your Tamagotchi)
    ├── form.auth-form [method=POST]
    │   ├── div.form-group
    │   │   ├── label[for=email] (Email)
    │   │   └── input#email[type=email, name=email, required]
    │   ├── div.form-group
    │   │   ├── label[for=password] (Password)
    │   │   └── input#password[type=password, name=password, required]
    │   └── button.btn.btn-primary[type=submit] (Login)
    └── p.auth-footer
        └── a[href=/register] (Register here)
```

**Form Fields:**
- `email`: User's email address (login identifier)
- `password`: User's password

**Actions:**
- Form submission sends POST to `/login`
- Redirects to home on success

---

### 2. Registration Page (`register.html`)

```
div.auth-container
└── div.auth-box
    ├── h1 (🎉 Create Account)
    ├── p.subtitle (Start your Tamagotchi journey)
    ├── form.auth-form [method=POST]
    │   ├── div.form-group
    │   │   ├── label[for=email] (Email)
    │   │   └── input#email[type=email, name=email, required]
    │   ├── div.form-group
    │   │   ├── label[for=username] (Username - Display Name)
    │   │   └── input#username[type=text, name=username, required]
    │   ├── div.form-group
    │   │   ├── label[for=pet_name] (Pet Name)
    │   │   └── input#pet_name[type=text, name=pet_name, required, placeholder="Name your Tamagotchi"]
    │   ├── div.form-group
    │   │   ├── label[for=password] (Password)
    │   │   └── input#password[type=password, name=password, required, minlength=6]
    │   ├── div.form-group
    │   │   ├── label[for=confirm_password] (Confirm Password)
    │   │   └── input#confirm_password[type=password, name=confirm_password, required, minlength=6]
    │   └── button.btn.btn-primary[type=submit] (Create Account)
    └── p.auth-footer
        └── a[href=/login] (Login here)
```

**Form Fields:**
- `email`: User's email (unique identifier)
- `username`: Display name shown in app
- `pet_name`: Name of user's Tamagotchi pet
- `password`: Account password
- `confirm_password`: Password confirmation

**Actions:**
- Form submission sends POST to `/register`
- Validates password match client-side
- Creates account and logs in on success

---

### 3. Home Page (`home.html`)

```
div.home-container
├── h1 (Welcome, {username}! 👋)
│
├── div.tamagotchi-section
│   ├── div.tamagotchi-display
│   │   ├── div#tamagotchi-sprite.tamagotchi-sprite [data-health={health}]
│   │   │   └── div.sprite-container
│   │   │       ├── img#tamagotchi-image.tamagotchi-image [src="", alt="Tamagotchi"]
│   │   │       └── div#image-loading.image-loading (Loading...)
│   │   ├── h2.tamagotchi-name ({pet_name})
│   │   └── div.health-bar-container
│   │       ├── div.health-bar
│   │       │   └── div.health-fill [style="width: {health}%"]
│   │       └── span.health-text ({health}% Health)
│   │
│   └── div.stats-grid
│       ├── div.stat-card.water-stat
│       │   ├── div.stat-icon (💧)
│       │   ├── div.stat-info
│       │   │   ├── h3 (Water)
│       │   │   ├── p.stat-value ({water_today} ml)
│       │   │   └── p.stat-label (Today)
│       │   └── a.stat-link[href=/water] (View Details →)
│       ├── div.stat-card.food-stat
│       │   └── [Similar structure for Food]
│       └── div.stat-card.gym-stat
│           └── [Similar structure for Gym]
│
├── div.quick-actions
│   ├── h2 (Quick Actions)
│   └── div.action-buttons
│       ├── button.btn.btn-water[onclick="quickLog('water')"] (💧 Log Water)
│       ├── button.btn.btn-food[onclick="quickLog('food')"] (🍎 Log Food)
│       ├── button.btn.btn-gym[onclick="quickLog('gym')"] (💪 Log Workout)
│       └── button.btn.btn-danger[onclick="quickLog('health')"] (❤️ Set Health - Temp Dev)
│
└── div#quickLogModal.modal
    └── div.modal-content
        ├── span.close (×)
        ├── h2#modalTitle (Quick Log)
        └── form#quickLogForm
            ├── div#modalBody [Dynamic content]
            └── button.btn.btn-primary[type=submit] (Save)
```

**Key Dynamic Elements:**
- `#tamagotchi-sprite[data-health]`: Stores current health value
- `#tamagotchi-image`: Mascot image that changes based on health
- `.health-fill`: Visual health bar (width = health percentage)
- `#modalBody`: Dynamic content based on quick action type

**JavaScript Functions:**
- `updateTamagotchiSprite()`: Updates mascot image based on health
- `quickLog(type)`: Opens modal for logging actions
- `getHealthLevel(health)`: Maps health to image level

---

### 4. Water Tracker Page (`water.html`)

```
div.tracker-page
├── div.page-header
│   ├── div
│   │   ├── h1 (💧 Water Tracker)
│   │   └── p (Stay hydrated and keep your Tamagotchi happy!)
│   └── button.btn.btn-primary[onclick="showModal('addWaterModal')"] (+ Add Water)
│
├── div.analytics-grid
│   ├── div.analytics-card
│   │   ├── h3 (Today's Water)
│   │   ├── p.big-stat ({today_total} ml)
│   │   ├── div.progress-bar
│   │   │   └── div.progress-fill [style="width: {today_percentage}%"]
│   │   └── p ({today_percentage}% of {daily_goal}ml goal)
│   ├── div.analytics-card (Weekly Average)
│   ├── div.analytics-card (Weekly Total)
│   └── div.analytics-card (Streak)
│
├── div.chart-container
│   ├── h2 (Weekly Trend)
│   └── canvas#waterChart
│
└── div.history-section
    ├── h2 (Today's History)
    └── table.data-table
        ├── thead
        │   └── tr
        │       ├── th (Time)
        │       ├── th (Amount)
        │       ├── th (Notes)
        │       └── th (Actions)
        └── tbody
            └── tr [for each entry]
                ├── td ({time})
                ├── td ({amount} ml)
                ├── td ({notes})
                └── td
                    └── button.btn-icon[onclick="deleteEntry({id})"] (🗑️)
```

**Modal Structure:**
```
div#addWaterModal.modal
└── div.modal-content
    ├── span.close (×)
    ├── h2 (Add Water Entry)
    └── form#waterForm
        ├── div.form-group
        │   ├── label[for=amount] (Amount (ml))
        │   └── input#amount[type=number, name=amount, required, min=0, step=50]
        ├── div.form-group
        │   ├── label[for=notes] (Notes - optional)
        │   └── textarea#notes[name=notes, rows=3]
        └── button.btn.btn-primary[type=submit] (Save Entry)
```

---

### 5. Food Tracker Page (`food.html`)

```
div.tracker-page
├── div.page-header
│   ├── div
│   │   ├── h1 (🍎 Food Tracker)
│   │   └── p (Track your meals and nutrition)
│   └── button.btn.btn-primary[onclick="showModal('addMealModal')"] (+ Add Meal)
│
├── div.analytics-grid
│   ├── div.analytics-card (Calories)
│   │   ├── h3 (Calories Today)
│   │   ├── p.big-stat ({today_calories} cal)
│   │   ├── div.progress-bar
│   │   │   └── div.progress-fill [style="width: {calorie_percentage}%"]
│   │   └── p ({calorie_percentage}% of {calorie_goal} cal goal)
│   ├── div.analytics-card (Protein with macro-bar.protein-bar)
│   ├── div.analytics-card (Carbs with macro-bar.carbs-bar)
│   └── div.analytics-card (Fats with macro-bar.fats-bar)
│
├── div.charts-row
│   ├── div.chart-container
│   │   ├── h3 (Daily Calories)
│   │   └── canvas#calorieChart
│   └── div.chart-container
│       ├── h3 (Macro Distribution)
│       └── canvas#macroChart
│
└── div.history-section
    ├── h2 (Today's Meals)
    └── div.meal-list
        └── div.meal-card [for each meal]
            ├── div.meal-header
            │   ├── h3 ({meal_name})
            │   └── span ({time})
            ├── div.meal-macros
            │   ├── span (🔥 {calories} cal)
            │   ├── span (🥩 {protein}g protein)
            │   ├── span (🍞 {carbs}g carbs)
            │   └── span (🥑 {fats}g fats)
            └── div.meal-actions
                └── button.btn-icon[onclick="deleteMeal({id})"] (🗑️)
```

**Modal Structure:**
```
div#addMealModal.modal
└── div.modal-content
    ├── span.close (×)
    ├── h2 (Add Meal)
    └── form#mealForm
        ├── div.form-group
        │   ├── label[for=meal_name] (Meal Name)
        │   └── input#meal_name[type=text, name=meal_name, required]
        ├── div.form-row
        │   ├── div.form-group
        │   │   ├── label[for=calories] (Calories)
        │   │   └── input#calories[type=number, name=calories, required, min=0]
        │   ├── div.form-group (Protein)
        │   ├── div.form-group (Carbs)
        │   └── div.form-group (Fats)
        └── button.btn.btn-primary[type=submit] (Save Meal)
```

---

### 6. Gym Tracker Page (`gym.html`)

```
div.tracker-page
├── div.page-header
│   ├── div
│   │   ├── h1 (💪 Gym Tracker)
│   │   └── p (Track your workouts and stay active)
│   └── button.btn.btn-primary[onclick="showModal('addWorkoutModal')"] (+ Add Workout)
│
├── div.analytics-grid
│   ├── div.analytics-card (Today's Minutes)
│   ├── div.analytics-card (Weekly Minutes)
│   ├── div.analytics-card (Weekly Workouts)
│   ├── div.analytics-card (Calories Burned)
│   └── div.analytics-card (Streak)
│
├── div.chart-container
│   ├── h2 (Weekly Activity)
│   └── canvas#workoutChart
│
└── div.history-section
    ├── h2 (Recent Workouts)
    └── div.workout-list
        └── div.workout-card [for each workout]
            ├── div.workout-header
            │   ├── h3 ({workout_type})
            │   └── span ({date} at {time})
            ├── div.workout-stats
            │   ├── div.workout-stat
            │   │   ├── span.stat-label (Duration)
            │   │   └── span.stat-value ({duration} min)
            │   ├── div.workout-stat (Intensity)
            │   └── div.workout-stat (Calories)
            ├── p ({notes})
            └── div.workout-actions
                └── button.btn-icon[onclick="deleteWorkout({id})"] (🗑️)
```

**Modal Structure:**
```
div#addWorkoutModal.modal
└── div.modal-content
    ├── span.close (×)
    ├── h2 (Add Workout)
    └── form#workoutForm
        ├── div.form-group
        │   ├── label[for=workout_type] (Workout Type)
        │   └── select#workout_type[name=workout_type, required]
        │       ├── option (Cardio)
        │       ├── option (Strength Training)
        │       ├── option (HIIT)
        │       └── option (Yoga)
        ├── div.form-row
        │   ├── div.form-group (Duration)
        │   └── div.form-group (Intensity)
        ├── div.form-group
        │   ├── label[for=calories] (Calories Burned - optional)
        │   └── input#calories[type=number, name=calories, min=0]
        ├── div.form-group (Notes - textarea)
        └── button.btn.btn-primary[type=submit] (Save Workout)
```

---

## Shared Components

### Alert/Flash Messages
```
div.alert.alert-{type}
└── text (message)
```

**Types:**
- `alert-success`: Green background for success messages
- `alert-error`: Red background for errors
- `alert-warning`: Yellow background for warnings
- `alert-info`: Blue background for info

**Behavior:**
- Auto-dismiss after 5 seconds
- Fade out animation (opacity transition)

---

### Modal Component
```
div.modal [style="display: none"]
└── div.modal-content
    ├── span.close (×)
    ├── h2 (Modal Title)
    └── [Modal Content]
```

**Interaction:**
- Click `.close` to hide modal
- Click outside `.modal-content` to hide modal
- Escape key to close (can be implemented)

---

## JavaScript Interactions

### Main.js - Global Functions

#### Flash Message Handling
```javascript
// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
```

#### Modal Management
```javascript
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Close button functionality
document.querySelectorAll('.close').forEach(btn => {
    btn.onclick = function() {
        this.closest('.modal').style.display = 'none';
    }
});
```

#### API Helper
```javascript
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            return { error: `Server error: ${response.status}` };
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return { error: 'Invalid response from server' };
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { error: error.message };
    }
}
```

#### Toast Notifications
```javascript
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
```

---

### Home.js - Mascot & Health Management

#### Health Level Mapping
```javascript
function getHealthLevel(health) {
    if (health === 0) return 0;
    if (health === 100) return 100;
    
    const levels = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95];
    
    let closest = levels[0];
    let minDiff = Math.abs(health - closest);
    
    for (let level of levels) {
        const diff = Math.abs(health - level);
        if (diff < minDiff) {
            minDiff = diff;
            closest = level;
        }
    }
    
    return closest;
}
```

#### Image Loading
```javascript
async function tryLoadImage(basePath, healthLevel) {
    const extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'];
    const baseUrl = `${basePath}/health_${healthLevel}`;
    
    for (let ext of extensions) {
        try {
            const imageUrl = `${baseUrl}.${ext}`;
            const response = await fetch(imageUrl, { method: 'HEAD' });
            if (response.ok) {
                return imageUrl;
            }
        } catch (e) {
            // Continue to next extension
        }
    }
    
    return null;
}
```

#### Sprite Update
```javascript
async function updateTamagotchiSprite() {
    const sprite = document.getElementById('tamagotchi-sprite');
    const health = parseInt(sprite.dataset.health);
    const image = document.getElementById('tamagotchi-image');
    const loading = document.getElementById('image-loading');
    
    const healthLevel = getHealthLevel(health);
    
    loading.style.display = 'block';
    image.style.display = 'none';
    
    const basePath = '/static/images/mascot';
    const imageUrl = await tryLoadImage(basePath, healthLevel);
    
    if (imageUrl) {
        image.src = imageUrl;
        image.onload = function() {
            loading.style.display = 'none';
            image.style.display = 'block';
        };
    } else {
        loading.textContent = `No image found for health level ${healthLevel}`;
        loading.style.color = '#64748b';
    }
}
```

#### Quick Log Modal
```javascript
function quickLog(type) {
    const modal = document.getElementById('quickLogModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    // Set content based on type (water, food, gym, health)
    // Each type has specific form fields
    
    modalBody.innerHTML = content;
    modal.style.display = 'block';
    
    // Handle form submission
    const form = document.getElementById('quickLogForm');
    form.onsubmit = async function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        const endpoint = type === 'health' ? '/api/tamagotchi/health' : `/api/${type}`;
        const result = await apiCall(endpoint, 'POST', data);
        
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            if (type === 'health') {
                // Update UI immediately for health changes
                sprite.dataset.health = data.health;
                document.querySelector('.health-fill').style.width = `${data.health}%`;
                document.querySelector('.health-text').textContent = `${data.health}% Health`;
                updateTamagotchiSprite();
            } else {
                // Reload page for other actions
                setTimeout(() => location.reload(), 1000);
            }
            showToast('Success!', 'success');
            modal.style.display = 'none';
        }
    };
}
```

---

### Water.js, Food.js, Gym.js - Tracker Pages

Each tracker page has similar patterns:

#### Form Submission
```javascript
document.getElementById('formId').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    const result = await apiCall('/api/endpoint', 'POST', data);
    
    if (result.error) {
        showToast(result.error, 'error');
    } else {
        showToast('Entry added successfully!', 'success');
        hideModal('modalId');
        setTimeout(() => location.reload(), 1000);
    }
});
```

#### Delete Entry
```javascript
async function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this entry?')) {
        return;
    }
    
    const result = await apiCall(`/api/endpoint/${id}`, 'DELETE');
    
    if (result.error) {
        showToast(result.error, 'error');
    } else {
        showToast('Entry deleted successfully!', 'success');
        setTimeout(() => location.reload(), 1000);
    }
}
```

#### Chart Rendering (using Chart.js)
```javascript
// Example for water chart
const ctx = document.getElementById('waterChart').getContext('2d');
const waterChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Water Intake (ml)',
            data: weeklyData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
```

---

## API Integration

### Endpoints

#### Authentication
- **POST** `/login` - User login with email and password
- **POST** `/register` - User registration with email, username, pet_name, password
- **GET** `/logout` - User logout (clears session)

#### Water Tracker
- **GET** `/api/water` - Get today's water entries
- **POST** `/api/water` - Add water entry
  ```json
  {
    "amount": 500,
    "notes": "Optional notes"
  }
  ```
- **DELETE** `/api/water/{id}` - Delete water entry

#### Food Tracker
- **GET** `/api/food` - Get today's meals
- **POST** `/api/food` - Add meal entry
  ```json
  {
    "meal_name": "Breakfast",
    "calories": 450,
    "protein": 25,
    "carbs": 50,
    "fats": 15
  }
  ```
- **DELETE** `/api/food/{id}` - Delete meal entry

#### Gym Tracker
- **GET** `/api/gym` - Get workouts
- **POST** `/api/gym` - Add workout entry
  ```json
  {
    "workout_type": "Cardio",
    "duration": 30,
    "intensity": "High",
    "calories": 250,
    "notes": "Morning run"
  }
  ```
- **DELETE** `/api/gym/{id}` - Delete workout entry

#### Tamagotchi Health
- **GET** `/api/tamagotchi/health` - Get current health
- **POST** `/api/tamagotchi/health` - Set health (dev only)
  ```json
  {
    "health": 75
  }
  ```

---

## State Management

### Session Storage
The application uses Flask sessions (server-side) to maintain:
- `user_id`: Unique user identifier
- `username`: User's display name
- `pet_name`: User's Tamagotchi pet name
- `email`: User's email address
- `override_health`: Manually set health value (dev mode)

### Local State (Client-side)
- **Tamagotchi Health**: Stored in `data-health` attribute on `#tamagotchi-sprite`
- **Modal State**: Managed via `display` style property
- **Form Data**: Captured via FormData API before submission

### Data Flow
```
User Action (DOM Event)
    ↓
JavaScript Handler
    ↓
API Call (fetch)
    ↓
Server Processing
    ↓
JSON Response
    ↓
Update DOM / Show Toast
    ↓
Page Reload (if needed)
```

---

## Event Listeners

### Page Load Events
```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    // Set up event listeners
    // Load initial data
    // Start periodic updates
});
```

### Form Events
- `submit`: Prevent default, validate, send API request
- `input`: Real-time validation (future enhancement)
- `change`: Update dependent fields

### Click Events
- Modal open/close buttons
- Delete action buttons
- Quick action buttons
- Navigation links

### Window Events
- `click`: Close modals when clicking outside
- `resize`: Responsive chart adjustments (future)

---

## CSS Classes Reference

### Layout
- `.container`: Main content wrapper (max-width: 1200px)
- `.auth-container`: Centered authentication layout
- `.home-container`: Home page layout
- `.tracker-page`: Tracker page layout

### Components
- `.navbar`, `.nav-container`, `.nav-menu`, `.nav-link`: Navigation
- `.auth-box`: Authentication form container
- `.modal`, `.modal-content`: Modal dialog
- `.alert`, `.alert-success`, `.alert-error`: Notifications

### Cards
- `.stat-card`: Home page statistics cards
- `.analytics-card`: Analytics display cards
- `.meal-card`, `.workout-card`: Entry cards

### Forms
- `.form-group`: Form field container
- `.form-row`: Horizontal form layout
- `.btn`, `.btn-primary`, `.btn-water`, `.btn-food`, `.btn-gym`, `.btn-danger`: Buttons

### Tamagotchi
- `.tamagotchi-display`: Main mascot display area
- `.sprite-container`: Mascot image container
- `.tamagotchi-image`: Mascot image element
- `.health-bar`, `.health-fill`: Health visualization
- `.image-loading`: Loading state indicator

---

## Accessibility Considerations

### Semantic HTML
- Use appropriate heading hierarchy (h1 → h2 → h3)
- Form labels associated with inputs via `for` attribute
- Semantic elements (`nav`, `section`, `article`)

### Keyboard Navigation
- Tab order follows logical flow
- Focus styles on interactive elements
- Enter key submits forms
- Escape key closes modals (to be implemented)

### ARIA Attributes (Future Enhancement)
- `aria-label` for icon-only buttons
- `aria-describedby` for form field hints
- `role="dialog"` for modals
- `aria-live` for dynamic updates

---

## Performance Optimizations

### Image Loading
- Lazy loading for mascot images
- Multiple format support (WebP, PNG, GIF, etc.)
- HEAD request to check existence before loading

### API Calls
- Error handling and retry logic
- Loading states during requests
- Debouncing for rapid actions (future)

### DOM Updates
- Minimal reflows (batch updates)
- CSS transitions for smooth animations
- Request Animation Frame for animations (future)

---

## Future Enhancements

### Progressive Web App (PWA)
- Service worker for offline support
- Installable app experience
- Push notifications for reminders

### Real-time Updates
- WebSocket connection for live health updates
- Real-time chart updates
- Multi-device synchronization

### Advanced Interactions
- Drag-and-drop for organizing entries
- Inline editing for entries
- Bulk actions (delete multiple entries)

### Enhanced Mascot
- More expressive animations
- Interactive pet (click to play)
- Evolution/growth stages

---

## Development Guidelines

### Adding New Pages
1. Create template extending `base.html`
2. Define DOM structure in this document
3. Create corresponding JavaScript file
4. Add route in Flask application
5. Update navigation menu

### Adding New Features
1. Plan DOM structure
2. Implement HTML/CSS
3. Add JavaScript interactions
4. Create API endpoints
5. Test across browsers
6. Update this documentation

### Code Organization
- Keep JavaScript modular (one file per page)
- Reuse shared functions from `main.js`
- Follow consistent naming conventions
- Comment complex logic

---

## Browser Compatibility

### Supported Browsers
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

### Required Features
- ES6+ JavaScript (async/await, arrow functions)
- Fetch API
- CSS Grid and Flexbox
- CSS Custom Properties (variables)

---

## Testing Checklist

### Functional Testing
- [ ] All forms submit successfully
- [ ] Validation errors display correctly
- [ ] Modals open and close properly
- [ ] Navigation works on all pages
- [ ] API calls handle errors gracefully
- [ ] Mascot image changes with health
- [ ] Charts render correctly

### Cross-browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Responsive Testing
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

---

## Conclusion

This DOM structure provides a complete, interactive frontend for the Tamagotchi Tracker application. The modular design allows for easy maintenance and future enhancements while maintaining a consistent user experience across all pages.

For implementation details, refer to the actual template and JavaScript files in the codebase.
