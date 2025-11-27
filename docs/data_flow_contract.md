# Data Flow Contract for DevOps Tamagotchi

This document outlines the theoretical data flow contract between the frontend, business logic, and individual services in the DevOps Tamagotchi application. It includes the data formats exchanged at each layer.

---

## 1. Frontend to Business Logic

### Request Format
```json
{
    "action": "string",  // e.g., "get_status", "get_daily_summary", "query"
    "module": "string",  // e.g., "food_tracker", "water_tracker", "gym_tracker"
    "params": {
        "key": "value"   // Optional parameters, e.g., {"date": "2025-11-27"}
    }
}
```

### Response Format
```json
{
    "status": "string",  // "success" or "error"
    "data": {
        "key": "value"   // Module-specific data
    },
    "error": "string"    // Error message if status is "error"
}
```

---

## 2. Business Logic to Services

### Request Format
```python
{
    "date": "2025-11-27",  // Optional parameter for date-specific data
    "query": "string"      // Optional query for individual data retrieval
}
```

### Response Format
```json
{
    "key": "value"  // Module-specific data
}
```

---

## 3. Service Data Contracts

### Food Tracker Service
- **Purpose**: Stores meals, macros, and nutrition data.
- **Daily Summary**:
  ```json
  {
      "calories": 2000,
      "protein": 150,
      "carbs": 250,
      "fats": 70,
      "meals": [
          {"name": "Breakfast", "calories": 500},
          {"name": "Lunch", "calories": 700},
          {"name": "Dinner", "calories": 800}
      ]
  }
  ```
- **Weekly Summary**:
  ```json
  {
      "weekly_calories": 14000,
      "daily_averages": {
          "calories": 2000,
          "protein": 150,
          "carbs": 250,
          "fats": 70
      }
  }
  ```
- **Individual Query**:
  ```json
  {
      "meal": {
          "name": "Breakfast",
          "calories": 500,
          "protein": 30,
          "carbs": 50,
          "fats": 10
      }
  }
  ```
- **Mock Query**:
  ```json
  {
      "query": "Get all meals with calories > 600",
      "results": [
          {"name": "Lunch", "calories": 700},
          {"name": "Dinner", "calories": 800}
      ]
  }
  ```

### Water Tracker Service
- **Purpose**: Tracks daily water intake.
- **Daily Summary**:
  ```json
  {
      "water_intake_liters": 3.5
  }
  ```
- **Weekly Summary**:
  ```json
  {
      "weekly_water_intake": 24.5,
      "daily_averages": {
          "water_intake_liters": 3.5
      }
  }
  ```
- **Individual Query**:
  ```json
  {
      "date": "2025-11-27",
      "water_intake_liters": 3.5
  }
  ```
- **Mock Query**:
  ```json
  {
      "query": "Get water intake for the past 3 days",
      "results": [
          {"date": "2025-11-25", "water_intake_liters": 3.0},
          {"date": "2025-11-26", "water_intake_liters": 3.2},
          {"date": "2025-11-27", "water_intake_liters": 3.5}
      ]
  }
  ```

### Gym Tracker Service
- **Purpose**: Logs workouts and exercises.
- **Daily Summary**:
  ```json
  {
      "workouts": [
          {"type": "cardio", "duration_minutes": 30},
          {"type": "strength", "duration_minutes": 45}
      ]
  }
  ```
- **Weekly Summary**:
  ```json
  {
      "weekly_workouts": [
          {"type": "cardio", "total_duration_minutes": 210},
          {"type": "strength", "total_duration_minutes": 315}
      ]
  }
  ```
- **Individual Query**:
  ```json
  {
      "workout": {
          "type": "cardio",
          "duration_minutes": 30,
          "calories_burned": 300
      }
  }
  ```
- **Mock Query**:
  ```json
  {
      "query": "Get all strength workouts longer than 40 minutes",
      "results": [
          {"type": "strength", "duration_minutes": 45, "calories_burned": 400}
      ]
  }
  ```

---

## Summary
This contract ensures that the frontend, business logic, and services communicate using well-defined data formats. Each layer is responsible for validating and transforming data as needed to maintain consistency and reliability.