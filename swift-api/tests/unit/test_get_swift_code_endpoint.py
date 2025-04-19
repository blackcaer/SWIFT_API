import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.routers.swift_codes import get_swift_code
from app.models import SwiftCode
from app.schemas import HeadquarterSwiftCodeResponse, BranchSwiftCodeResponse
from sqlalchemy.sql import Select

class TestGetSwiftCodeEndpoint:
    """Unit tests for GET /v1/swift-codes/{swift-code} endpoint"""
    
    @pytest.fixture
    def mock_db(self) -> MagicMock:
        mock = MagicMock()
        mock.get = MagicMock(return_value=None)
        mock_exec_result = MagicMock()
        mock_exec_result.all.return_value = []
        mock.exec = MagicMock(return_value=mock_exec_result)
        return mock

    @pytest.mark.asyncio
    async def test_valid_hq_code_with_branches(self, mock_db):
        """Test HQ code returns with branches"""
        # Mock HQ data
        hq_data = SwiftCode(
            swiftCode="CITIUS33XXX",
            bankName="Citibank",
            address="New York",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=True
        )
        
        # Mock branch data
        branch_data = [
            SwiftCode(
                swiftCode="CITIUS33MIA",
                bankName="Citibank Miami",
                address="Miami",
                countryISO2="US",
                countryName="USA",
                isHeadquarter=False
            )
        ]
        
        mock_db.get.return_value = hq_data
        mock_db.exec.return_value.all.return_value = branch_data
        
        response = await get_swift_code("CITIUS33XXX", mock_db)
        
        assert isinstance(response, HeadquarterSwiftCodeResponse)
        assert response.swiftCode == "CITIUS33XXX"
        assert response.isHeadquarter is True
        assert len(response.branches) == 1, f"Expected 1 branch, got {len(response.branches)}"
        assert response.branches[0].swiftCode == "CITIUS33MIA"
        

    @pytest.mark.asyncio
    async def test_branch_code_returns_without_branches(self, mock_db):
        """Test branch code returns without branches field"""
        branch_data = SwiftCode(
            swiftCode="CITIUS33MIA",
            bankName="Citibank Miami",
            address="Miami",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=False
        )
        
        mock_db.get.return_value = branch_data
        
        response = await get_swift_code("CITIUS33MIA", mock_db)
        
        assert isinstance(response, BranchSwiftCodeResponse)
        assert response.swiftCode == "CITIUS33MIA"
        assert response.isHeadquarter is False
        assert not hasattr(response, 'branches')
        mock_db.exec.assert_not_called()


    @pytest.mark.asyncio
    async def test_branch_code_returns_without_branches(self, mock_db):
        """Test branch code returns without branches field"""
        branch_data = SwiftCode(
            swiftCode="CITIUS33MIA",
            bankName="Citibank Miami",
            address="Miami",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=False
        )
        
        mock_db.get.return_value = branch_data
        
        response = await get_swift_code("CITIUS33MIA", mock_db)
        
        assert isinstance(response, BranchSwiftCodeResponse)
        assert response.swiftCode == "CITIUS33MIA"
        assert response.isHeadquarter is False
        assert not hasattr(response, 'branches')

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_code,expected_error", [
        ("INVALID", "SWIFT code must be 8 or 11 characters long"),
        ("12345678XXX", "First 6 characters must be alphabetic"),
        ("CITI@S33XXX", "First 6 characters must be alphabetic"),
        ("CITIUS3@XXX", "Characters 7-8 must be alphanumeric"),
    ])
    async def test_invalid_swift_code_format(self, mock_db, invalid_code, expected_error):
        """Test invalid swift code formats raise validation errors"""
        with pytest.raises(HTTPException) as exc_info:
            await get_swift_code(invalid_code, mock_db)
        
        assert exc_info.value.status_code == 400
        assert expected_error.lower() in str(exc_info.value.detail).lower()
        mock_db.get.assert_not_called()  # Powinno failować przed zapytaniem do bazy

    @pytest.mark.asyncio
    @pytest.mark.parametrize("valid_code", [
        "CITIUS33XXX",  # HQ
        "CITIUS33",  # Short HQ
        "CITIUS33MIA",  # Branch
        "ABCDEF12XXX",  # HQ z cyframi w pozycjach 7-8
        "ABCDEF12123",  # Branch z cyframi
    ])
    async def test_valid_swift_code_format(self, mock_db, valid_code):
        """Test valid swift code formats pass validation"""
        mock_db.get.return_value = SwiftCode(
            swiftCode=valid_code,
            bankName="Test Bank",
            address="Test Address",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=valid_code.endswith("XXX")
        )
        
        response = await get_swift_code(valid_code, mock_db)
        
        if valid_code.endswith("XXX"):
            assert isinstance(response, HeadquarterSwiftCodeResponse)
        else:
            assert isinstance(response, BranchSwiftCodeResponse)
        assert response.swiftCode == valid_code
    
    @pytest.mark.asyncio
    async def test_nonexistent_swift_code(self, mock_db):
        """Test non-existent swift code returns 404"""
        mock_db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_swift_code("NONEXIST", mock_db)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    @patch('app.routers.swift_codes.validate_swift_code_format')
    async def test_swift_code_normalization(self, mock_validate, mock_db):
        """Test swift code is normalized before processing"""
        mock_validate.return_value = "CITIUS33XXX"
        mock_db.get.return_value = SwiftCode(
            swiftCode="CITIUS33XXX",
            bankName="Test",
            address="Test",
            countryISO2="US",
            countryName="USA",
            isHeadquarter=True
        )
        
        await get_swift_code("  citius33xxx  ", mock_db)
        mock_validate.assert_called_with("  citius33xxx  ")