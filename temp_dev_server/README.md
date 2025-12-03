# Temporary Development Server

⚠️ **THIS FOLDER IS TEMPORARY** - Delete before production deployment

## Purpose
This is a standalone development server for frontend testing only. It provides:
- Simple Flask server with in-memory data storage
- Basic authentication (no real security)
- Mock API endpoints for water, food, and gym tracking
- Frontend preview functionality

## Usage

### 1. Install dependencies (if not already installed):
```bash
pip install Flask Flask-CORS
```

### 2. Run the server:
```bash
python server.py
```

### 3. Open your browser:
```
http://localhost:5000
```

### Default Test Account:
- Username: `test`
- Password: `test123`

Or register a new account (data stored in memory only)

## Features
- User registration and login (session-based)
- Water intake tracking
- Food/meal tracking
- Gym/workout tracking
- Tamagotchi health calculation
- All data stored in memory (resets on server restart)

## Notes
- Data is NOT persisted (in-memory only)
- No real password security (for testing only)
- No database required
- DELETE this folder when integrating with production backend
