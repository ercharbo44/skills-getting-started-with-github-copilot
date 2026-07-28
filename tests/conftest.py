"""
Pytest configuration and shared fixtures for API tests.
"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Store original activities state for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    """Provide TestClient for testing the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def valid_email():
    """Provide a valid email for signup tests."""
    return "newstudent@mergington.edu"


@pytest.fixture
def another_email():
    """Provide another valid email for signup tests."""
    return "anotherstudent@mergington.edu"


@pytest.fixture
def valid_activity_name():
    """Provide a valid activity name."""
    return "Chess Club"


@pytest.fixture
def invalid_activity_name():
    """Provide an invalid activity name."""
    return "Nonexistent Activity"
