# tests/integration/test_database.py

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
import importlib
import sys

DATABASE_MODULE = "app.database"

@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to mock the settings.DATABASE_URL before app.database is imported."""
    mock_url = "postgresql://user:password@localhost:5434/test_db"
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = mock_url
    
    # Ensure 'app.database' is not loaded to allow fresh patching
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
        
    # Patch settings in 'app.database' context
    monkeypatch.setattr("app.config.settings", mock_settings)
    return mock_settings

def reload_database_module():
    """Helper function to reload the database module after patches."""
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)

def test_base_declaration(mock_settings):
    """Test that Base is an instance of declarative_base."""
    database = reload_database_module()
    Base = database.Base
    # Checking against the internal class structure of declarative_base
    assert hasattr(Base, "metadata")

def test_get_engine_success(mock_settings):
    """Test that get_engine returns a valid engine."""
    database = reload_database_module()
    engine = database.get_engine()
    assert isinstance(engine, Engine)

def test_get_engine_failure(mock_settings):
    """Test that get_engine raises an error if the engine cannot be created."""
    database = reload_database_module()
    with patch("app.database.create_engine", side_effect=SQLAlchemyError("Engine error")):
        with pytest.raises(SQLAlchemyError, match="Engine error"):
            database.get_engine()

def test_get_sessionmaker(mock_settings):
    """Test that get_sessionmaker returns a valid sessionmaker."""
    database = reload_database_module()
    engine = database.get_engine()
    SessionLocal = database.get_sessionmaker(engine)
    assert isinstance(SessionLocal, sessionmaker)

def test_get_db_generator(mock_settings):
    """
    Test the get_db generator to cover lines 60-64.
    This ensures the session is yielded and subsequently closed.
    """
    database = reload_database_module()
    
    # We need to mock the SessionLocal that is created inside the module
    mock_session = MagicMock(spec=Session)
    mock_sessionmaker = MagicMock(return_value=mock_session)
    
    with patch("app.database.SessionLocal", mock_sessionmaker):
        db_gen = database.get_db()
        
        # 1. Start the generator (executes code up to 'yield')
        db_instance = next(db_gen)
        assert db_instance == mock_session
        
        # 2. Close the generator (triggers the 'finally' block)
        with pytest.raises(StopIteration):
            next(db_gen)
            
        # 3. Verify the session was closed (Line 64)
        mock_session.close.assert_called_once()