"""
Integration tests for GET /v1/swift-codes/{swift-code} endpoint
Testing the full HTTP request/response cycle with real database interactions
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Import app directly to avoid factory pattern issues
from app.main import app
from app.models import SwiftCode
from app.database import get_session

@pytest.fixture(name="engine")
def engine_fixture():
    """Fixture for creating a fresh database engine for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    """Fixture for database session with test data"""
    with Session(engine) as session:
        # Headquarters (both 11-char and 8-char versions)
        hq1 = SwiftCode(
            swiftCode="CITIUS33XXX",  # 11-char HQ
            bankName="Citibank HQ",
            address="New York",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=True
        )

        branch = SwiftCode(
            swiftCode="CITIUS33MIA",  # Branch
            bankName="Citibank Miami",
            address="Miami",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=False
        )
        session.add(hq1)
        session.add(branch)
        session.commit()
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    """Fixture for test client with overridden database dependency"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_get_11char_hq_with_branches(client: TestClient):
    """Test 11-character HQ code returns with branches"""
    response = client.get("/v1/swift-codes/CITIUS33XXX")
    
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "CITIUS33XXX"
    assert data["isHeadquarter"] is True
    print(data["branches"])
    assert len(data["branches"]) == 1
    assert data["branches"][0]["swiftCode"] == "CITIUS33MIA"

def test_get_branch_swift_code(client: TestClient):
    """Test branch code returns without branches field"""
    response = client.get("/v1/swift-codes/CITIUS33MIA")
    
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "CITIUS33MIA"
    assert data["isHeadquarter"] is False
    assert "branches" not in data

def test_whitespace_handling(client: TestClient):
    """Test that whitespace around SWIFT codes is properly trimmed"""
    # Test leading/trailing whitespace
    response = client.get("/v1/swift-codes/  CITIUS33MIA  ")
    assert response.status_code == 200
    assert response.json()["swiftCode"] == "CITIUS33MIA"
    
def test_get_nonexistent_swift_code(client: TestClient):
    """Test non-existent swift code returns 404"""
    response = client.get("/v1/swift-codes/NONEXIST")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.parametrize("invalid_code,expected_error", [
    ("INVALID", "must be 8 or 11 characters"),
    ("CITIUS3", "must be 8 or 11 characters"),  # Too short
    ("CITIUS33XX", "must be 8 or 11 characters"),  # 10 chars invalid
    ("12345678XXX", "First 6 characters must be alphabetic"),
    ("CITI@S33XXX", "First 6 characters must be alphabetic"),
])
def test_invalid_swift_code_format(client: TestClient, invalid_code, expected_error):
    """Test various invalid swift code formats"""
    response = client.get(f"/v1/swift-codes/{invalid_code}")
    assert response.status_code == 400
    assert expected_error.lower() in response.json()["detail"].lower()

def test_case_insensitivity(client: TestClient):
    """Test that SWIFT code is case-insensitive in the URL"""
    response = client.get("/v1/swift-codes/citius33mia")
    assert response.status_code == 200
    assert response.json()["swiftCode"] == "CITIUS33MIA"  # Response should be normalized