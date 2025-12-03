"""
Temporary Development Server - FOR TESTING FRONTEND ONLY
⚠️ DELETE THIS FILE BEFORE PRODUCTION DEPLOYMENT
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import os
import sys

# Add parent directory to path to import templates
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

app = Flask(
    __name__,
    template_folder='../src/frontend/templates',
    static_folder='../src/frontend/static'
)
app.secret_key = 'temp-dev-secret-key-not-for-production'
CORS(app)

# In-memory data storage (resets on server restart)
users = {
    'test@example.com': {
        'password': 'test123',
        'email': 'test@example.com',
        'username': 'test',
        'pet_name': 'TamagotchMe',
        'id': 1
    }
}
water_entries = []
food_entries = []
gym_entries = []
next_user_id = 2


# Helper Functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_tamagotchi_health():
    """Calculate Tamagotchi health based on recent activities."""
    if 'user_id' not in session:
        return 50
    
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Get today's data
    water_today = sum(e['amount'] for e in water_entries 
                     if e['user_id'] == user_id and e['date'] == today)
    calories_today = sum(e['calories'] for e in food_entries 
                        if e['user_id'] == user_id and e['date'] == today)
    workout_today = sum(e['duration'] for e in gym_entries 
                       if e['user_id'] == user_id and e['date'] == today)
    
    # Simple health calculation (0-100)
    health = 50  # Base health
    
    # Water contribution (max +20)
    if water_today >= 2000:
        health += 20
    elif water_today >= 1500:
        health += 15
    elif water_today >= 1000:
        health += 10
    
    # Food contribution (max +20)
    if 1800 <= calories_today <= 2200:
        health += 20
    elif 1500 <= calories_today <= 2500:
        health += 15
    elif calories_today > 0:
        health += 5
    
    # Exercise contribution (max +10)
    if workout_today >= 60:
        health += 10
    elif workout_today >= 30:
        health += 7
    elif workout_today >= 15:
        health += 4
    
    return min(100, max(0, health))


# Authentication Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # TEMP: Accept any input - always succeed
        if email and password:
            # Auto-create user if doesn't exist
            if email not in users:
                global next_user_id
                users[email] = {
                    'password': password,
                    'email': email,
                    'username': email.split('@')[0],
                    'pet_name': 'TamagotchMe',
                    'id': next_user_id
                }
                next_user_id += 1
            
            session['user_id'] = users[email]['id']
            session['username'] = users[email]['username']
            session['pet_name'] = users[email]['pet_name']
            session['email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please enter email and password', 'warning')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global next_user_id
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        pet_name = request.form.get('pet_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # TEMP: Accept any input - always succeed
        if email and username and pet_name and password:
            # Check if email already exists
            if email in users:
                session['user_id'] = users[email]['id']
                session['username'] = users[email]['username']
                session['pet_name'] = users[email]['pet_name']
                session['email'] = email
                flash('Welcome back! Logged in successfully.', 'success')
                return redirect(url_for('home'))
            
            # Create new user
            users[email] = {
                'password': password,
                'email': email,
                'username': username,
                'pet_name': pet_name,
                'id': next_user_id
            }
            next_user_id += 1
            
            session['user_id'] = users[email]['id']
            session['username'] = username
            session['pet_name'] = pet_name
            session['email'] = email
            flash('Account created and logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please fill in all fields', 'warning')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Page Routes
@app.route('/home')
@login_required
def home():
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Calculate today's stats
    water_today = sum(e['amount'] for e in water_entries 
                     if e['user_id'] == user_id and e['date'] == today)
    calories_today = sum(e['calories'] for e in food_entries 
                        if e['user_id'] == user_id and e['date'] == today)
    workout_today = sum(e['duration'] for e in gym_entries 
                       if e['user_id'] == user_id and e['date'] == today)
    
    tamagotchi = {
        'name': session.get('pet_name', 'TamagotchMe'),
        'health': calculate_tamagotchi_health()
    }
    
    stats = {
        'water_today': water_today,
        'calories_today': calories_today,
        'workout_minutes': workout_today
    }
    
    return render_template('home.html', 
                         username=session.get('username'),
                         pet_name=session.get('pet_name'),
                         tamagotchi=tamagotchi,
                         stats=stats)


@app.route('/water')
@login_required
def water_page():
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Get today's water entries
    today_entries = [e for e in water_entries 
                    if e['user_id'] == user_id and e['date'] == today]
    water_today = sum(e['amount'] for e in today_entries)
    
    # Calculate weekly stats
    week_ago = today - timedelta(days=7)
    weekly_entries = [e for e in water_entries 
                     if e['user_id'] == user_id and e['date'] >= week_ago]
    weekly_total = sum(e['amount'] for e in weekly_entries)
    weekly_avg = weekly_total // 7 if weekly_entries else 0
    
    # Calculate streak
    streak = 0
    check_date = today
    while True:
        day_total = sum(e['amount'] for e in water_entries 
                       if e['user_id'] == user_id and e['date'] == check_date)
        if day_total >= 2000:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    analytics = {
        'today_total': water_today,
        'today_percentage': min(100, (water_today / 2000) * 100),
        'daily_goal': 2000,
        'weekly_avg': weekly_avg,
        'weekly_total': weekly_total,
        'streak': streak
    }
    
    # Format history
    history = sorted(today_entries, key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('water.html', analytics=analytics, history=history)


@app.route('/food')
@login_required
def food_page():
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Get today's meals
    today_meals = [e for e in food_entries 
                  if e['user_id'] == user_id and e['date'] == today]
    
    calories_today = sum(e['calories'] for e in today_meals)
    protein_today = sum(e.get('protein', 0) for e in today_meals)
    carbs_today = sum(e.get('carbs', 0) for e in today_meals)
    fats_today = sum(e.get('fats', 0) for e in today_meals)
    
    analytics = {
        'today_calories': calories_today,
        'calorie_percentage': min(100, (calories_today / 2000) * 100),
        'calorie_goal': 2000,
        'today_protein': protein_today,
        'protein_percentage': min(100, (protein_today / 150) * 100),
        'today_carbs': carbs_today,
        'carbs_percentage': min(100, (carbs_today / 250) * 100),
        'today_fats': fats_today,
        'fats_percentage': min(100, (fats_today / 70) * 100)
    }
    
    meals = sorted(today_meals, key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('food.html', analytics=analytics, meals=meals)


@app.route('/gym')
@login_required
def gym_page():
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Get today's workouts
    today_workouts = [e for e in gym_entries 
                     if e['user_id'] == user_id and e['date'] == today]
    
    today_minutes = sum(e['duration'] for e in today_workouts)
    
    # Weekly stats
    week_ago = today - timedelta(days=7)
    weekly_workouts = [e for e in gym_entries 
                      if e['user_id'] == user_id and e['date'] >= week_ago]
    weekly_minutes = sum(e['duration'] for e in weekly_workouts)
    
    # Calculate calories burned (rough estimate)
    calories_burned = today_minutes * 8  # ~8 cal/min average
    
    # Calculate streak
    streak = 0
    check_date = today
    while True:
        day_total = sum(e['duration'] for e in gym_entries 
                       if e['user_id'] == user_id and e['date'] == check_date)
        if day_total >= 20:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    analytics = {
        'today_minutes': today_minutes,
        'goal_percentage': min(100, (today_minutes / 60) * 100),
        'daily_goal': 60,
        'weekly_minutes': weekly_minutes,
        'weekly_workouts': len(weekly_workouts),
        'calories_burned': calories_burned,
        'streak': streak
    }
    
    workouts = sorted(weekly_workouts, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    return render_template('gym.html', analytics=analytics, workouts=workouts)


# API Routes
@app.route('/api/water', methods=['GET', 'POST'])
@login_required
def api_water():
    if request.method == 'POST':
        data = request.get_json()
        
        entry = {
            'id': len(water_entries) + 1,
            'user_id': session['user_id'],
            'amount': int(data.get('amount', 0)),
            'notes': data.get('notes', ''),
            'timestamp': datetime.now(),
            'date': datetime.now().date()
        }
        
        water_entries.append(entry)
        
        return jsonify({
            'success': True,
            'message': 'Water logged successfully',
            'entry': {
                'id': entry['id'],
                'amount': entry['amount']
            }
        }), 201
    
    # GET
    user_id = session['user_id']
    today = datetime.now().date()
    entries = [e for e in water_entries if e['user_id'] == user_id and e['date'] == today]
    
    return jsonify({'entries': entries}), 200


@app.route('/api/water/<int:entry_id>', methods=['DELETE'])
@login_required
def api_delete_water(entry_id):
    global water_entries
    water_entries = [e for e in water_entries if e['id'] != entry_id]
    
    return jsonify({
        'success': True,
        'message': 'Entry deleted successfully'
    }), 200


@app.route('/api/food', methods=['GET', 'POST'])
@login_required
def api_food():
    if request.method == 'POST':
        data = request.get_json()
        
        entry = {
            'id': len(food_entries) + 1,
            'user_id': session['user_id'],
            'name': data.get('meal_name', ''),
            'calories': int(data.get('calories', 0)),
            'protein': float(data.get('protein', 0)),
            'carbs': float(data.get('carbs', 0)),
            'fats': float(data.get('fats', 0)),
            'timestamp': datetime.now(),
            'date': datetime.now().date()
        }
        
        food_entries.append(entry)
        
        return jsonify({
            'success': True,
            'message': 'Meal logged successfully',
            'entry': {'id': entry['id']}
        }), 201
    
    # GET
    user_id = session['user_id']
    today = datetime.now().date()
    entries = [e for e in food_entries if e['user_id'] == user_id and e['date'] == today]
    
    return jsonify({'meals': entries}), 200


@app.route('/api/food/<int:meal_id>', methods=['DELETE'])
@login_required
def api_delete_food(meal_id):
    global food_entries
    food_entries = [e for e in food_entries if e['id'] != meal_id]
    
    return jsonify({
        'success': True,
        'message': 'Meal deleted successfully'
    }), 200


@app.route('/api/gym', methods=['GET', 'POST'])
@login_required
def api_gym():
    if request.method == 'POST':
        data = request.get_json()
        
        entry = {
            'id': len(gym_entries) + 1,
            'user_id': session['user_id'],
            'type': data.get('workout_type', ''),
            'duration': int(data.get('duration', 0)),
            'intensity': data.get('intensity', 'Medium'),
            'calories': int(data.get('calories', 0)) if data.get('calories') else None,
            'notes': data.get('notes', ''),
            'timestamp': datetime.now(),
            'date': datetime.now().date()
        }
        
        gym_entries.append(entry)
        
        return jsonify({
            'success': True,
            'message': 'Workout logged successfully',
            'entry': {'id': entry['id']}
        }), 201
    
    # GET
    user_id = session['user_id']
    entries = [e for e in gym_entries if e['user_id'] == user_id]
    
    return jsonify({'workouts': entries}), 200


@app.route('/api/gym/<int:workout_id>', methods=['DELETE'])
@login_required
def api_delete_gym(workout_id):
    global gym_entries
    gym_entries = [e for e in gym_entries if e['id'] != workout_id]
    
    return jsonify({
        'success': True,
        'message': 'Workout deleted successfully'
    }), 200


@app.route('/api/tamagotchi/health', methods=['GET', 'POST'])
@login_required
def api_tamagotchi_health():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        health = data.get('health')
        if health is None:
            return jsonify({'error': 'Health field is required'}), 400
        
        # Convert to float if it's a string
        try:
            health = float(health)
        except (ValueError, TypeError):
            return jsonify({'error': 'Health must be a number'}), 400
        
        # Validate health value
        if health < 0 or health > 100:
            return jsonify({'error': 'Health must be between 0 and 100'}), 400
        
        # Store in session for this dev server
        session['override_health'] = health
        print(f"🩺 Health manually set to {health}% (DEV MODE)")
        
        return jsonify({
            'success': True,
            'message': 'Health updated successfully',
            'health': health
        }), 200
    
    # GET request
    # Check if health was manually overridden
    if 'override_health' in session:
        health = session['override_health']
    else:
        health = calculate_tamagotchi_health()
    
    return jsonify({
        'health': health,
        'status': 'healthy' if health >= 70 else 'needs_attention'
    }), 200


if __name__ == '__main__':
    print("\n" + "="*60)
    print("⚠️  TEMPORARY DEVELOPMENT SERVER")
    print("="*60)
    print("🌐 Server starting at: http://localhost:5000")
    print("👤 Test account: email='test@example.com', password='test123'")
    print("📝 Or register a new account with email, username, and pet name")
    print("\n⚠️  Remember: DELETE temp_dev_server folder before production!")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
