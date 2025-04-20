import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import SwiftCode
from app.routers.swift_codes import delete_swift_code
from app.schemas import MessageResponse

class TestDeleteSwiftCodeUnit:
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    async def test_successful_branch_deletion(self, mock_db):
        mock_branch = SwiftCode(
            swiftCode="CITIPLPP123",
            bankName="CITIBANK POLAND",
            countryISO2="PL",
            countryName="POLAND",
            address="UL. TESTOWA 123, WARSAW",
            isHeadquarter=False
        )
        mock_db.get.return_value = mock_branch
        mock_db.exec.return_value.first.return_value = None

        response = await delete_swift_code("CITIPLPP123", mock_db)

        assert response == MessageResponse(
            message="SWIFT code CITIPLPP123 deleted successfully"
        )
        mock_db.delete.assert_called_once_with(mock_branch)

    async def test_successful_hq_deletion(self, mock_db):
        mock_hq = SwiftCode(
            swiftCode="CITIPLPPXXX",
            bankName="CITIBANK POLAND HQ",
            isHeadquarter=True
        )
        mock_db.get.return_value = mock_hq
        mock_db.exec.return_value.first.return_value = None

        response = await delete_swift_code("CITIPLPPXXX", mock_db)

        assert "CITIPLPPXXX" in response.message

class TestDeleteResponseStructures:
    def test_success_response_structure(self):
        response = MessageResponse(
            message="SWIFT code CITIPLPP123 deleted successfully"
        )
        
        assert response.model_dump() == {
            "message": "SWIFT code CITIPLPP123 deleted successfully"
        }