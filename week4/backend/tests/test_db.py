from unittest.mock import patch

import pytest
from backend.app.db import get_session
from backend.app.models import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def test_get_session_context_manager():
    # Create a temporary in-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Patch SessionLocal to use our test session
    with patch("backend.app.db.SessionLocal", TestSessionLocal):
        # Test successful session usage
        with get_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1


def test_get_session_rollback_on_exception():
    # Create a temporary in-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Patch SessionLocal to use our test session
    with patch("backend.app.db.SessionLocal", TestSessionLocal):
        # Test that exception triggers rollback
        with pytest.raises(ValueError):
            with get_session() as session:
                session.execute(text("SELECT 1"))
                raise ValueError("Test error")
