import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import SwiftCode
from app.routers.swift_codes import create_swift_code
from app.schemas import SwiftCodeCreate, MessageResponse
from app.database import SessionDep


class TestCreateSwiftCodeUnit:
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    @pytest.fixture
    def valid_hq_data(self):
        return {
            "swiftCode": "CITIPLPPXXX",
            "bankName": "CITIBANK POLAND HQ",
            "address": "UL. CENTRALNA 1, WARSAW",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": True,
        }

    @pytest.fixture
    def valid_branch_data(self):
        return {
            "swiftCode": "CITIPLPP123",
            "bankName": "CITIBANK POLAND BRANCH",
            "address": "UL. TESTOWA 1, KRAKOW",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": False,
        }

    async def test_create_hq_success(self, mock_db, valid_hq_data):
        mock_db.get.return_value = None

        response = await create_swift_code(swiftCode=SwiftCodeCreate(**valid_hq_data), db=mock_db)

        assert isinstance(response, MessageResponse)
        assert "CITIPLPPXXX" in response.message
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_create_branch_success(self, mock_db, valid_branch_data):
        # Mock HQ exists
        mock_db.get.side_effect = [
            None,  # For branch check
            MagicMock(spec=SwiftCode),  # For HQ check
        ]

        response = await create_swift_code(
            swiftCode=SwiftCodeCreate(**valid_branch_data), db=mock_db
        )

        assert "CITIPLPP123" in response.message

    async def test_reject_duplicate_code(self, mock_db, valid_hq_data):
        mock_db.get.return_value = MagicMock(spec=SwiftCode)

        with pytest.raises(HTTPException) as exc:
            await create_swift_code(swiftCode=SwiftCodeCreate(**valid_hq_data), db=mock_db)

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in str(exc.value.detail)

    async def test_reject_branch_without_hq(self, mock_db, valid_branch_data):
        mock_db.get.side_effect = [None, None]  # Branch doesn't exist, HQ doesn't exist

        with pytest.raises(HTTPException) as exc:
            await create_swift_code(swiftCode=SwiftCodeCreate(**valid_branch_data), db=mock_db)

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "headquarter not found" in str(exc.value.detail)


class TestCreateResponseStructure:
    """Tests for verifying create endpoint response structure"""

    @pytest.fixture
    def mock_db(self):
        mock = MagicMock(spec=Session)
        mock.get.return_value = None  # Simulate no existing code
        mock.add = MagicMock()
        mock.commit = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_create_response_structure(self, mock_db):
        """Verify create response contains exactly the required fields"""
        swift_code_data = SwiftCodeCreate(
            swiftCode="NEWCODE1XXX",
            bankName="New Bank",
            address="New Address",
            countryISO2="US",
            countryName="UNITED STATES",
            isHeadquarter=True,
        )

        response = await create_swift_code(swift_code_data, mock_db)

        # Verify response has exactly these fields
        assert set(response.model_dump().keys()) == {"message"}
