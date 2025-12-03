"""REST API endpoints for the TamagotchMe Tracker."""

import logging
from flask import Blueprint, request, jsonify, session
from datetime import datetime

logger = logging.getLogger(__name__)


def create_api_blueprint(coordinator):
    """Create and configure the API blueprint."""
    api = Blueprint('api', __name__)
    
    def require_auth():
        """Check if user is authenticated."""
        if 'user_id' not in session:
            return None
        return session['user_id']
    
    @api.route('/water', methods=['GET', 'POST'])
    def water():
        """Water tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'POST':
            data = request.get_json()
            amount = data.get('amount')
            notes = data.get('notes', '')
            
            # TODO: Save to database via service
            logger.info(f"Water logged: {amount}ml for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Water logged successfully'
            }), 201
        
        # GET request
        # TODO: Fetch from database
        return jsonify({'entries': []}), 200
    
    @api.route('/water/<int:entry_id>', methods=['DELETE'])
    def delete_water(entry_id):
        """Delete water entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # TODO: Delete from database
        logger.info(f"Water entry {entry_id} deleted for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Entry deleted successfully'
        }), 200
    
    @api.route('/food', methods=['GET', 'POST'])
    def food():
        """Food tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'POST':
            data = request.get_json()
            meal_name = data.get('meal_name')
            calories = data.get('calories')
            protein = data.get('protein', 0)
            carbs = data.get('carbs', 0)
            fats = data.get('fats', 0)
            
            # TODO: Save to database via service
            logger.info(f"Meal logged: {meal_name} - {calories}cal for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Meal logged successfully'
            }), 201
        
        # GET request
        return jsonify({'meals': []}), 200
    
    @api.route('/food/<int:meal_id>', methods=['DELETE'])
    def delete_meal(meal_id):
        """Delete meal entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # TODO: Delete from database
        logger.info(f"Meal {meal_id} deleted for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Meal deleted successfully'
        }), 200
    
    @api.route('/gym', methods=['GET', 'POST'])
    def gym():
        """Gym tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'POST':
            data = request.get_json()
            workout_type = data.get('workout_type')
            duration = data.get('duration')
            intensity = data.get('intensity')
            calories = data.get('calories', 0)
            notes = data.get('notes', '')
            
            # TODO: Save to database via service
            logger.info(f"Workout logged: {workout_type} - {duration}min for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Workout logged successfully'
            }), 201
        
        # GET request
        return jsonify({'workouts': []}), 200
    
    @api.route('/gym/<int:workout_id>', methods=['DELETE'])
    def delete_workout(workout_id):
        """Delete workout entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # TODO: Delete from database
        logger.info(f"Workout {workout_id} deleted for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Workout deleted successfully'
        }), 200
    
    @api.route('/TamagotchMe/health', methods=['GET', 'POST'])
    def TamagotchMe_health():
        """Get or set TamagotchMe health status."""
        user_id = require_auth()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                logger.error("No JSON data received in POST request")
                return jsonify({'error': 'No data provided'}), 400
            
            health = data.get('health')
            if health is None:
                logger.error(f"Health field missing in data: {data}")
                return jsonify({'error': 'Health field is required'}), 400
            
            # Convert to int/float if it's a string
            try:
                health = float(health)
            except (ValueError, TypeError):
                return jsonify({'error': 'Health must be a number'}), 400
            
            # Validate health value
            if health < 0 or health > 100:
                return jsonify({'error': 'Health must be between 0 and 100'}), 400
            
            # TODO: Save to database via service
            logger.info(f"Health set to {health}% for user {user_id} (DEV MODE)")
            
            return jsonify({
                'success': True,
                'message': 'Health updated successfully',
                'health': health
            }), 200
        
        # GET request
        # TODO: Calculate health based on user activities
        health = 85
        
        return jsonify({
            'health': health,
            'status': 'healthy' if health >= 70 else 'needs_attention'
        }), 200
    
    logger.info("API Blueprint created successfully")
    return api
