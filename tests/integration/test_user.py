# tests/integration/test_user.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User

def test_database_connection(db_session):
    """Test that the database connection is working."""
    assert db_session is not None

def test_create_user_with_faker(db_session, fake_user_data):
    """Test creating a user using fake data from a fixture."""
    # Since fake_user_data now contains 'password', we convert it to 'password_hash'
    password = fake_user_data.pop('password')
    user = User(**fake_user_data, password_hash=User.hash_password(password))
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == fake_user_data['email']

def test_create_multiple_users(db_session):
    """Test creating multiple users in one session."""

    initial_count = db_session.query(User).count()

    user1 = User(
        first_name="User", last_name="One",
        email="one@example.com", username="userone",
        password_hash=User.hash_password("Password123!")
    )
    user2 = User(
        first_name="User", last_name="Two",
        email="two@example.com", username="usertwo",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add_all([user1, user2])
    db_session.commit()
    
    assert db_session.query(User).count() == initial_count + 2

def test_unique_email_constraint(db_session):
    """Test that the database enforces unique email addresses."""
    user1 = User(
        first_name="First", last_name="Last",
        email="same@example.com", username="user1",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        first_name="Second", last_name="Last",
        email="same@example.com", username="user2",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_unique_username_constraint(db_session):
    """Test that the database enforces unique usernames."""
    user1 = User(
        first_name="First", last_name="Last",
        email="user1@example.com", username="sameuser",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        first_name="Second", last_name="Last",
        email="user2@example.com", username="sameuser",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_user_persistence_after_constraint(db_session):
    """Test that valid users remain in the DB even after a failed constraint attempt."""
    user1 = User(
        first_name="Valid", last_name="User",
        email="valid@example.com", username="validuser",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user1)
    db_session.commit()

    # Trigger a failure
    user2 = User(
        first_name="Invalid", last_name="User",
        email="valid@example.com", username="invalid",
        password_hash=User.hash_password("Password123!")
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Ensure user1 is still there
    queried_user = db_session.query(User).filter_by(username="validuser").first()
    assert queried_user is not None