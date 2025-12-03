# Life Planner - Python Modular Monolith

A comprehensive life planning application built as a Python modular monolith, featuring food tracking, water tracking, and gym tracking capabilities.

## ToDo
- [] Food Tracking Module
- [] Water Tracking Module
- [] Gym Tracking Module
- [] REST API with JSON responses
- [x] Shared Database Interface
- [] Modular architecture with dependency injection
- [] API Documentation
- [] Unit and Integration Tests
- [] Dockerization
- [] CI/CD Pipeline
- [] Frontend Web Interface
- [] User Authentication and Authorization
- [] Data Contracts and Validation

## Project Structure

```
devops-tamagotchme/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Local development setup
├── README.md                  # This file
├── docs/                       # Documentation
│   ├── FRONTEND_ARCHITECTURE.md         # Frontend structure guide
│   ├── FRONTEND_RESTRUCTURE_SUMMARY.md  # Restructuring changes
│   ├── AZURE_DEPLOYMENT_GUIDE.md        # Azure setup guide
│   ├── DEPLOYMENT_ARCHITECTURE.md       # Deployment overview
│   └── data_flow_contract.md            # Data contracts
├── .github/
│   └── workflows/
│       ├── dev-ci.yml          # CI for dev branch
│       └── prod-cicd.yml       # CI/CD for prod branch
├── src/
│   ├── core/                   # Core application logic
│   │   ├── __init__.py
│   │   ├── application.py      # Main application class
│   │   ├── config.py           # Configuration management
│   │   ├── coordinator.py      # Module coordinator
│   │   ├── database.py         # Database manager
│   │   ├── dashboard_service.py # Dashboard aggregation
│   │   └── health_calculator.py # Pet health logic
│   ├── shared/                 # Shared utilities
│   │   ├── __init__.py
│   │   ├── base_service.py     # Base service class
│   │   └── database_interface.py # Reusable database interface
│   ├── frontend/               # Web interface (modular structure)
│   │   ├── __init__.py
│   │   ├── web_app.py          # Flask app initialization
│   │   ├── api.py              # REST API endpoints
│   │   ├── utils.py            # Shared utilities & decorators
│   │   ├── routes/             # Route blueprints
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py  # Authentication routes
│   │   │   └── page_routes.py  # Application page routes
│   │   ├── templates/          # HTML templates
│   │   │   ├── base.html
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── home.html
│   │   │   ├── water.html
│   │   │   ├── food.html
│   │   │   └── gym.html
│   │   └── static/             # Static assets
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   └── modules/                # Business logic modules
│       ├── __init__.py
│       ├── auth/               # Authentication module
│       │   ├── __init__.py
│       │   ├── models.py       # User model
│       │   ├── service.py      # Auth business logic
│       │   ├── repository.py   # Data access
│       │   └── utils.py        # Password hashing
│       ├── food_tracker/       # Food tracking module
│       │   ├── __init__.py
│       │   ├── models.py       # Data models
│       │   └── service.py      # Business logic
│       ├── water_tracker/      # Water tracking module
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── service.py
│       └── gym_tracker/        # Gym tracking module
│           ├── __init__.py
│           ├── models.py
│           └── service.py
└── tests/                      # Test files
    ├── conftest.py
    ├── test_water_tracker.py
    ├── test_food_tracker.py
    ├── test_gym_tracker.py
    ├── test_auth_service.py
    ├── test_health_calculator.py
    ├── test_dashboard_service.py
    └── test_application.py
```

## Features

- **Food Tracker**: Track meals, calories, and nutritional information
- **Water Tracker**: Monitor daily water intake and hydration goals  
- **Gym Tracker**: Log workouts, exercises, and fitness progress
- **User Authentication**: Secure login and registration
- **Tamagotchi Pet**: Virtual pet that reflects your health habits
- **Dashboard**: Aggregated view of all activities
- **REST API**: Complete RESTful API for frontend communication
- **Modular Architecture**: Clean separation of concerns with reusable components
- **Database Interface**: Reusable database operations across modules

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL/MySQL)
- **API**: RESTful endpoints with JSON responses
- **Architecture**: Modular monolith with dependency injection

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd devops-tamagotchme
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp config/.env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - API: http://localhost:5000/api/v1
   - Health check: http://localhost:5000/health

## API Documentation

See [API_DOCS.md](API_DOCS.md) for complete API documentation.

## Architecture Overview

### Core Components

- **Application**: Main application coordinator
- **Config**: Environment-based configuration management
- **Database Manager**: Database connection and session management
- **Module Coordinator**: Manages and coordinates all tracker modules

### Database Interface

The shared database interface provides:
- Generic repository pattern for CRUD operations
- Date range filtering capabilities
- Bulk operations for performance
- Raw query execution for complex operations

### Module Structure

Each tracker module follows the same structure:
- **Models**: SQLAlchemy data models
- **Service**: Business logic and data operations
- **API Endpoints**: RESTful API integration

### REST API

The API provides:
- Standardized JSON responses
- Comprehensive error handling
- Date filtering capabilities
- Dashboard summary endpoints
- Module-specific CRUD operations

## Development

### Adding New Modules

1. Create module directory under `src/modules/`
2. Implement `models.py` with SQLAlchemy models
3. Implement `service.py` with business logic
4. Register service in `coordinator.py`
5. Add API endpoints in `frontend/api.py`

### Database Interface Usage

```python
from src.shared.database_interface import DatabaseInterface

# Initialize interface
db_interface = DatabaseInterface(db_session)

# Get repository for a model
repo = db_interface.get_repository(YourModel)

# Use repository methods
entity = repo.create(name="Example", value=123)
entities = repo.get_all()
entity = repo.update(entity.id, value=456)
repo.delete(entity.id)
```

## Configuration

Environment variables (see `config/.env.example`):
- Database settings
- Web server configuration
- Module enable/disable flags
- Security settings

## License

[License information]