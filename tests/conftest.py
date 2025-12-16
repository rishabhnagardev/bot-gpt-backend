import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path so tests can import `app` package
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
