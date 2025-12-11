# API Endpoints Documentation

## Overview
This document describes all frontend-backend API connections for the Tamagotchi Tracker application.

---

## Water Tracker

### POST /api/water
Log a water intake entry.

**Request Body:**
```json
{
  "amount": 250,        // Required: Amount in ml (number)
  "notes": "Morning"    // Optional: Notes about the entry (string)
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Water logged successfully",
  "entry": { /* entry details */ }
}
```

**Frontend Files:** 
- `water.js` - Full form
- `home.js` - Quick log

---

### GET /api/water
Get today's water entries.

**Response (200):**
```json
{
  "entries": [
    {
      "id": 1,
      "amount": 250,
      "notes": "Morning",
      "timestamp": "2025-12-11T10:30:00"
    }
  ]
}
```

**Frontend Files:** 
- `water.js`

---

### DELETE /api/water/{entry_id}
Delete a water entry.

**Response (200):**
```json
{
  "success": true,
  "message": "Entry deleted successfully"
}
```

**Frontend Files:** 
- `water.js`

---

## Food Tracker

### POST /api/food
Log a meal entry.

**Request Body:**
```json
{
  "meal_name": "Breakfast",    // Optional: Name of the meal (string)
  "calories": 450,             // Required: Calories (number)
  "meal_type": "breakfast",    // Optional: Type of meal (string)
  "protein": 20,               // Optional: Protein in grams (number)
  "carbs": 50,                 // Optional: Carbs in grams (number)
  "fats": 15                   // Optional: Fats in grams (number)
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Meal logged successfully",
  "entry": { /* entry details */ }
}
```

**Frontend Files:** 
- `food.js` - Full form
- `home.js` - Quick log (meal_name and calories only)

---

### GET /api/food
Get today's meal entries.

**Response (200):**
```json
{
  "meals": [
    {
      "id": 1,
      "meal_name": "Breakfast",
      "calories": 450,
      "protein": 20,
      "carbs": 50,
      "fats": 15,
      "timestamp": "2025-12-11T08:00:00"
    }
  ]
}
```

**Frontend Files:** 
- `food.js`

---

### DELETE /api/food/{meal_id}
Delete a meal entry.

**Response (200):**
```json
{
  "success": true,
  "message": "Meal deleted successfully"
}
```

**Frontend Files:** 
- `food.js`

---

## Gym Tracker

### POST /api/gym
Log a workout entry.

**Request Body:**
```json
{
  "workout_type": "Cardio",    // Required: Type of workout (string)
  "duration": 30,              // Required: Duration in minutes (number)
  "intensity": "High",         // Optional: Intensity level (string: Low/Medium/High)
  "calories": 250,             // Optional: Calories burned (number)
  "notes": "Morning run"       // Optional: Notes about workout (string)
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Workout logged successfully",
  "entry": { /* entry details */ }
}
```

**Frontend Files:** 
- `gym.js` - Full form
- `home.js` - Quick log (workout_type and duration only)

---

### GET /api/gym
Get workout entries.

**Response (200):**
```json
{
  "workouts": [
    {
      "id": 1,
      "type": "Cardio",
      "duration": 30,
      "intensity": "High",
      "calories": 250,
      "notes": "Morning run",
      "timestamp": "2025-12-11T06:00:00"
    }
  ]
}
```

**Frontend Files:** 
- `gym.js`

---

### DELETE /api/gym/{workout_id}
Delete a workout entry.

**Response (200):**
```json
{
  "success": true,
  "message": "Workout deleted successfully"
}
```

**Frontend Files:** 
- `gym.js`

---

## Tamagotchi

### GET /api/tamagotchi/health
Get the Tamagotchi's current health status.

**Response (200):**
```json
{
  "health": 85,
  "status": "healthy",
  "message": "Your pet is doing great!",
  "water_score": 90,
  "food_score": 85,
  "exercise_score": 80
}
```

**Frontend Files:** 
- `home.js` (used for display, not currently called via JS)

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "error": "Field is required"
}
```

**401 Unauthorized:**
```json
{
  "error": "Unauthorized"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to process request"
}
```

---

## Frontend API Helper

All API calls use the `apiCall()` function in `main.js`:

```javascript
async function apiCall(endpoint, method = 'GET', data = null) {
    // Handles JSON requests/responses
    // Returns { error: "..." } on failure
    // Returns response JSON on success
}
```

---

## Field Name Mapping

**IMPORTANT:** Frontend form field names MUST match backend expectations:

| Frontend HTML `name` | Backend Expected Field |
|---------------------|------------------------|
| `amount` | `amount` |
| `notes` | `notes` |
| `meal_name` | `meal_name` ❌ was `meal` |
| `calories` | `calories` |
| `protein` | `protein` |
| `carbs` | `carbs` |
| `fats` | `fats` |
| `workout_type` | `workout_type` ❌ was `workout` |
| `duration` | `duration` |
| `intensity` | `intensity` |

✅ All mismatches have been fixed as of 2025-12-11
