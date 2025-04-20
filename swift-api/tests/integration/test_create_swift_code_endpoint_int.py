from fastapi.testclient import TestClient
import pytest
from fastapi import status
from app.models import SwiftCode
from app.schemas import SwiftCodeCreate


class TestCreateSwiftCodeIntegration:
    @pytest.fixture
    def valid_hq_payload(self):
        return {
            "swiftCode": "CITIPLPPXXX",
            "bankName": "CITIBANK POLAND HQ",
            "address": "UL. CENTRALNA 1, WARSAW",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": True,
        }

    @pytest.fixture
    def valid_branch_payload(self):
        return {
            "swiftCode": "CITIPLPP123",
            "bankName": "CITIBANK POLAND BRANCH",
            "address": "UL. TESTOWA 1, KRAKOW",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": False,
        }

    async def test_create_hq_success(self, client, valid_hq_payload):
        response = client.post("/v1/swift-codes/", json=valid_hq_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert "CITIPLPPXXX" in response.json()["message"]

    async def test_create_branch_success(
        self, client, session, valid_hq_payload, valid_branch_payload
    ):
        # Create HQ
        client.post("/v1/swift-codes/", json=valid_hq_payload)

        # Create branch
        response = client.post("/v1/swift-codes/", json=valid_branch_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert "CITIPLPP123" in response.json()["message"]

    async def test_reject_duplicate_code(self, client, valid_hq_payload):
        # First
        client.post("/v1/swift-codes/", json=valid_hq_payload)

        # Second
        response = client.post("/v1/swift-codes/", json=valid_hq_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    async def test_reject_branch_without_hq(self, client, valid_branch_payload):
        response = client.post("/v1/swift-codes/", json=valid_branch_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "headquarter not found" in response.json()["detail"]


class TestPostResponseStructures:
    """Response structure validation for POST endpoint"""

    def test_success_response_structure(self, client: TestClient):
        response = client.post(
            "/v1/swift-codes",
            json={
                "swiftCode": "NEWCODE1XXX",
                "bankName": "Bank",
                "address": "Address",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": True,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

        assert set(response.json().keys()) == {"message"}

    def test_error_response_structure(self, client: TestClient):
        response = client.post(
            "/v1/swift-codes",
            json={
                "swiftCode": "TESTHQXXX",  # Too short
                "bankName": "Bank",
                "address": "Address",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": True,
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert set(response.json().keys()) == {"detail"}
