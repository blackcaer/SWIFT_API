"""
Integration tests for GET /v1/swift-codes/country/{countryISO2code} endpoint
Testing country-specific SWIFT code retrieval with real database interactions
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from app.main import app
from app.models import SwiftCode
from app.database import get_session


@pytest.fixture(name="engine")
def engine_fixture():
    """Create fresh in-memory database for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Database session with test data for multiple countries"""
    with Session(engine) as session:
        # US data
        us_hq = SwiftCode(
            swiftCode="CITIUS33XXX",
            bankName="Citibank HQ",
            address="New York",
            countryISO2="US",
            countryName="UNITED STATES",
            isHeadquarter=True,
        )
        us_branch = SwiftCode(
            swiftCode="CITIUS33MIA",
            bankName="Citibank Miami",
            address="Miami",
            countryISO2="US",
            countryName="UNITED STATES",
            isHeadquarter=False,
        )

        # UK data
        uk_hq = SwiftCode(
            swiftCode="BARCGB22XXX",
            bankName="Barclays HQ",
            address="London",
            countryISO2="GB",
            countryName="UNITED KINGDOM",
            isHeadquarter=True,
        )

        session.add_all([us_hq, us_branch, uk_hq])
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """Test client with database dependency override"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_get_country_swift_codes_valid(client: TestClient):
    """Test retrieving SWIFT codes for valid country"""
    response = client.get("/v1/swift-codes/country/US")

    assert response.status_code == 200
    data = response.json()
    assert data["countryISO2"] == "US"
    assert data["countryName"] == "UNITED STATES"
    assert len(data["swiftCodes"]) == 2
    assert {code["swiftCode"] for code in data["swiftCodes"]} == {"CITIUS33XXX", "CITIUS33MIA"}


def test_get_country_swift_codes_case_insensitive(client: TestClient):
    """Test country code case insensitivity"""
    response = client.get("/v1/swift-codes/country/gb")
    assert response.status_code == 200
    assert response.json()["countryISO2"] == "GB"


def test_get_country_swift_codes_whitespace_handling(client: TestClient):
    """Test whitespace around country code is trimmed"""
    response = client.get("/v1/swift-codes/country/  US  ")
    assert response.status_code == 200
    assert response.json()["countryISO2"] == "US"


def test_get_country_swift_codes_not_found(client: TestClient):
    """Test country with no SWIFT codes returns 404"""
    response = client.get("/v1/swift-codes/country/FR")
    assert response.status_code == 404
    assert "No SWIFT codes found" in response.json()["detail"]


@pytest.mark.parametrize(
    "invalid_code,expected_error",
    [
        ("USA", "must be exactly 2 characters"),  # Too long
        ("U", "must be exactly 2 characters"),  # Too short
        ("12", "alphabetic"),  # Numeric
        ("U$", "alphabetic"),  # Special character
    ],
)
def test_invalid_country_codes(client: TestClient, invalid_code, expected_error):
    """Test various invalid country code formats"""
    response = client.get(f"/v1/swift-codes/country/{invalid_code}")
    assert response.status_code == 400
    assert expected_error.lower() in response.json()["detail"].lower()


def test_response_structure(client: TestClient):
    """Verify complete response structure"""
    response = client.get("/v1/swift-codes/country/US")
    data = response.json()

    assert all(field in data for field in ["countryISO2", "countryName", "swiftCodes"])
    assert isinstance(data["swiftCodes"], list)

    if data["swiftCodes"]:
        code = data["swiftCodes"][0]
        assert all(
            field in code
            for field in ["swiftCode", "bankName", "address", "countryISO2", "isHeadquarter"]
        )


class TestCountryResponseStructures:
    """Response structure validation for country endpoint"""

    def test_success_response_structure(self, client: TestClient):
        response = client.get("/v1/swift-codes/country/US")
        data = response.json()

        assert set(data.keys()) == {"countryISO2", "countryName", "swiftCodes"}
        assert isinstance(data["swiftCodes"], list)

        for code in data["swiftCodes"]:
            assert set(code.keys()) == {
                "address",
                "bankName",
                "countryISO2",
                "isHeadquarter",
                "swiftCode",
            }
            assert "countryName" not in code

    def test_error_response_structure(self, client: TestClient):
        response = client.get("/v1/swift-codes/country/INVALID")
        assert set(response.json().keys()) == {"detail"}
