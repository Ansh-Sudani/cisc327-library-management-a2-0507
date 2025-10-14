import pytest
from database import init_database, add_sample_data

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Initialize the database and add sample data before tests."""
    init_database()
    add_sample_data()
