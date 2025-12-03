"""Unit tests for Authentication Service."""

import pytest
from src.modules.auth.service import AuthService, AuthenticationError


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def auth_service(self, db_session):
        """Create an auth service instance."""
        return AuthService(db_session)

    def test_register_success(self, auth_service):
        """Test successful user registration."""
        result = auth_service.register(
            email="newuser@example.com",
            password="securepassword123",
            daily_water_goal=2500,
            daily_calorie_goal=2200,
            weekly_exercise_goal=4
        )
        
        assert result is not None
        assert result["email"] == "newuser@example.com"
        assert result["daily_water_goal"] == 2500
        assert result["daily_calorie_goal"] == 2200
        assert result["weekly_exercise_goal"] == 4
        assert "password" not in result
        assert "password_hash" not in result

    def test_register_duplicate_email(self, auth_service, sample_user):
        """Test registration with existing email."""
        with pytest.raises(AuthenticationError, match="Email already registered"):
            auth_service.register(
                email=sample_user.email,
                password="anotherpassword"
            )

    def test_login_success(self, auth_service, sample_user):
        """Test successful login."""
        result = auth_service.login(
            email=sample_user.email,
            password="testpassword"
        )
        
        assert result is not None
        assert result["email"] == sample_user.email
        assert result["id"] == sample_user.id

    def test_login_wrong_password(self, auth_service, sample_user):
        """Test login with wrong password."""
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            auth_service.login(
                email=sample_user.email,
                password="wrongpassword"
            )

    def test_login_nonexistent_user(self, auth_service):
        """Test login with non-existent email."""
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            auth_service.login(
                email="nonexistent@example.com",
                password="password"
            )

    def test_get_user_by_id(self, auth_service, sample_user):
        """Test retrieving user by ID."""
        result = auth_service.get_user_by_id(sample_user.id)
        
        assert result is not None
        assert result["id"] == sample_user.id
        assert result["email"] == sample_user.email

    def test_get_user_by_id_not_found(self, auth_service):
        """Test retrieving non-existent user."""
        result = auth_service.get_user_by_id(99999)
        
        assert result is None

    def test_update_user_goals(self, auth_service, sample_user):
        """Test updating user goals."""
        result = auth_service.update_user_goals(
            user_id=sample_user.id,
            daily_water_goal=3000,
            daily_calorie_goal=2500,
            weekly_exercise_goal=5
        )
        
        assert result["daily_water_goal"] == 3000
        assert result["daily_calorie_goal"] == 2500
        assert result["weekly_exercise_goal"] == 5

    def test_password_hashing(self, auth_service):
        """Test that passwords are properly hashed."""
        user1 = auth_service.register(
            email="user1@example.com",
            password="samepassword"
        )
        user2 = auth_service.register(
            email="user2@example.com",
            password="samepassword"
        )
        
        # Same password should produce different hashes (due to salt)
        # We can't directly check hashes, but we can verify both can login
        login1 = auth_service.login("user1@example.com", "samepassword")
        login2 = auth_service.login("user2@example.com", "samepassword")
        
        assert login1["email"] == "user1@example.com"
        assert login2["email"] == "user2@example.com"

    def test_register_default_goals(self, auth_service):
        """Test registration with default goals."""
        result = auth_service.register(
            email="defaultuser@example.com",
            password="password"
        )
        
        assert result["daily_water_goal"] == 2000
        assert result["daily_calorie_goal"] == 2000
        assert result["weekly_exercise_goal"] == 3
