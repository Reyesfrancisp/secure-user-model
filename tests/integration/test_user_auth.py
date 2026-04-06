# tests/integration/test_user_auth.py

import pytest
from jose import jwt
from unittest.mock import patch
from app.models.user import User, SECRET_KEY, ALGORITHM

# ======================================================================================
# Registration & Exception Reraise (Kills Line 108 & 111)
# ======================================================================================

def test_register_validation_error_reraise(db_session):
    """
    KILLS LINE 108: Trigger except ValidationError -> raise ValueError.
    We pass data missing required fields to force a Pydantic failure.
    """
    bad_data = {
        "email": "invalid-data@example.com",
        "username": "baduser",
        "password": "Password123!" 
        # Missing first_name and last_name
    }
    with pytest.raises(ValueError, match="Invalid user data"):
        User.register(db_session, bad_data)

def test_register_value_error_reraise_coverage(db_session):
    """
    KILLS LINE 111: Targets except ValueError -> raise.
    We mock the flush() to raise a ValueError inside the try block.
    """
    user_data = {
        "first_name": "Line", 
        "last_name": "108",
        "email": "111@example.com", 
        "username": "user111",
        "password": "Password123!"
    }
    # Mocking flush to raise a ValueError during the database operation
    with patch.object(db_session, "flush", side_effect=ValueError("flush error")):
        with pytest.raises(ValueError, match="flush error"):
            User.register(db_session, user_data)

def test_register_manual_value_errors(db_session):
    """Covers manual checks for short passwords and duplicates."""
    user_data = {
        "first_name": "Check", "last_name": "User",
        "email": "check@example.com", "username": "checkuser",
        "password": "Password123!"
    }
    # 1. Register once
    User.register(db_session, user_data)
    db_session.commit()
    
    # 2. Test Duplicate (triggers manual ValueError)
    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user_data)
        
    # 3. Test Short Password (triggers manual ValueError)
    short_data = user_data.copy()
    short_data["password"] = "123"
    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, short_data)

# ======================================================================================
# Token Logic & Ternary Branches (Kills Lines 78, 81, 85)
# ======================================================================================

def test_verify_token_logic_branches():
    """
    KILLS LINE 78, 81, 85: Targets all branches in verify_token.
    """
    # 1. Sub exists but is not a UUID (Triggers ValueError -> except block)
    token_bad_uuid = jwt.encode({"sub": "not-a-uuid"}, SECRET_KEY, algorithm=ALGORITHM)
    assert User.verify_token(token_bad_uuid) is None

    # 2. Token is cryptographically valid but MISSING 'sub' (Triggers 'return None')
    token_no_sub = jwt.encode({"data": "hello"}, SECRET_KEY, algorithm=ALGORITHM)
    assert User.verify_token(token_no_sub) is None

    # 3. Token is 'None' or malformed (Triggers JWTError -> except block)
    assert User.verify_token("completely.invalid.token") is None

def test_token_standard_flow(db_session, test_user):
    """Valid token creation and verification success path."""
    token = User.create_access_token({"sub": str(test_user.id)})
    assert User.verify_token(token) == test_user.id

# ======================================================================================
# Authentication & State
# ======================================================================================

def test_password_hashing_basic():
    """Verify hashing and instance verification."""
    pwd = "TestPass123"
    hashed = User.hash_password(pwd)
    # Instantiate user manually to verify password_hash logic
    user = User(password_hash=hashed)
    assert user.verify_password(pwd) is True
    assert user.verify_password("wrong") is False

def test_authenticate_logic_branches(db_session, test_user):
    """Covers all failure and success branches of authenticate."""
    # Success
    assert User.authenticate(db_session, test_user.username, "TestPassword123!") is not None
    # Wrong Password
    assert User.authenticate(db_session, test_user.username, "wrong") is None
    # User Not Found
    assert User.authenticate(db_session, "nobody", "pass") is None

def test_user_last_login_update(db_session, test_user):
    """Verify last_login update upon successful auth."""
    assert test_user.last_login is None
    User.authenticate(db_session, test_user.username, "TestPassword123!")
    db_session.refresh(test_user)
    assert test_user.last_login is not None

def test_user_model_representation(test_user):
    """Verify the model's __repr__ string."""
    expected = f"<User(name={test_user.first_name} {test_user.last_name}, email={test_user.email})>"
    assert str(test_user) == expected