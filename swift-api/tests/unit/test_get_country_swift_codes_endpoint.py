"""
Unit tests for GET /v1/swift-codes/country/{countryISO2code} endpoint
Testing the country-specific SWIFT code retrieval logic in isolation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.routers.swift_codes import get_country_swift_codes
from app.models import SwiftCode
from app.schemas import CountrySwiftCodesResponse
from app.validators import CountryISO2CodeValidationError


class TestGetCountrySwiftCodesEndpoint:
    """Unit tests for country SWIFT codes endpoint"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session with exec() and all() methods"""
        mock = AsyncMock()

        # Setup execute chain mock
        mock_exec_result = MagicMock()
        mock_exec_result.all.return_value = []
        mock.exec = MagicMock(return_value=mock_exec_result)

        return mock

    @pytest.mark.asyncio
    async def test_valid_country_with_codes(self, mock_db):
        """Test successful retrieval for country with SWIFT codes"""
        # Mock data
        mock_codes = [
            SwiftCode(
                swiftCode="CITIUS33XXX",
                bankName="Citibank",
                address="New York",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            ),
            SwiftCode(
                swiftCode="CITIUS33MIA",
                bankName="Citibank Miami",
                address="Miami",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=False,
            ),
        ]

        # Configure mocks
        mock_db.exec.return_value.all.return_value = mock_codes

        # Test
        response = await get_country_swift_codes("US", mock_db)

        # Verify
        assert isinstance(response, CountrySwiftCodesResponse)
        assert response.countryISO2 == "US"
        assert response.countryName == "UNITED STATES"
        assert len(response.swiftCodes) == 2
        assert response.swiftCodes[0].swiftCode == "CITIUS33XXX"
        assert response.swiftCodes[1].swiftCode == "CITIUS33MIA"

    @pytest.mark.asyncio
    async def test_country_with_no_codes(self, mock_db):
        """Test country with no SWIFT codes returns 404"""
        mock_db.exec.return_value.all.return_value = []

        with pytest.raises(HTTPException) as exc_info:
            await get_country_swift_codes("FR", mock_db)

        assert exc_info.value.status_code == 404
        assert "No SWIFT codes found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_code,expected_error",
        [
            ("USA", "must be exactly 2 characters"),
            ("U", "must be exactly 2 characters"),
            ("12", "alphabetic"),
            ("U$", "alphabetic"),
        ],
    )
    async def test_invalid_country_codes(self, mock_db, invalid_code, expected_error):
        """Test validation of invalid country codes"""
        with pytest.raises(HTTPException) as exc_info:
            await get_country_swift_codes(invalid_code, mock_db)

        assert exc_info.value.status_code == 400
        assert expected_error.lower() in str(exc_info.value.detail).lower()
        mock_db.exec.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.routers.swift_codes.validate_countryISO2code_format")
    async def test_country_code_normalization(self, mock_validate, mock_db):
        """Test country code normalization and whitespace handling"""
        mock_validate.return_value = "US"
        mock_codes = [
            SwiftCode(
                swiftCode="TESTUS33XXX",
                bankName="Test Bank",
                address="Test",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            )
        ]
        mock_db.exec.return_value.all.return_value = mock_codes

        response = await get_country_swift_codes("  us  ", mock_db)

        mock_validate.assert_called_with("  us  ")
        assert response.countryISO2 == "US"

    @pytest.mark.asyncio
    async def test_response_structure(self, mock_db):
        """Verify complete response structure"""
        mock_codes = [
            SwiftCode(
                swiftCode="TESTUS33XXX",
                bankName="Test Bank",
                address="Test",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            )
        ]
        mock_db.exec.return_value.all.return_value = mock_codes

        response = await get_country_swift_codes("US", mock_db)

        assert hasattr(response, "countryISO2")
        assert hasattr(response, "countryName")
        assert hasattr(response, "swiftCodes")
        assert isinstance(response.swiftCodes, list)

        if response.swiftCodes:
            code = response.swiftCodes[0]
            assert hasattr(code, "swiftCode")
            assert hasattr(code, "bankName")
            assert hasattr(code, "address")
            assert hasattr(code, "countryISO2")
            assert hasattr(code, "isHeadquarter")

    @pytest.mark.asyncio
    async def test_mixed_country_codes(self, mock_db):
        """Ensure only codes for requested country are returned"""
        all_mock_codes = [
            SwiftCode(
                swiftCode="BARCGB21XXX",
                bankName="Xyz",
                address="Abc",
                countryISO2="PL",
                countryName="POLAND",
                isHeadquarter=True,
            ),
            SwiftCode(
                swiftCode="BARCGB21ABC",
                bankName="Xyz",
                address="Abc",
                countryISO2="PL",
                countryName="POLAND",
                isHeadquarter=False,
            ),
            SwiftCode(
                swiftCode="CITIUS33XXX",
                bankName="Citibank",
                address="New York",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            ),
            SwiftCode(
                swiftCode="BARCGB22XXX",
                bankName="Barclays",
                address="London",
                countryISO2="GB",
                countryName="UNITED KINGDOM",
                isHeadquarter=True,
            ),
            SwiftCode(
                swiftCode="CITIUS32XXX",
                bankName="Citibank1",
                address="New Yorkx",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            ),
            SwiftCode(
                swiftCode="CITIUS31XXX",
                bankName="Citibank2",
                address="New Yorky",
                countryISO2="US",
                countryName="UNITED STATES",
                isHeadquarter=True,
            ),
        ]

        # Modify mock to filter by country code
        def mock_exec(query):
            # Extract the where condition from the query
            where_condition = query.whereclause
            if where_condition is not None:
                # Get the country code from the where condition
                country_code = where_condition.right.value
                # Filter codes by country
                filtered_codes = [
                    code for code in all_mock_codes if code.countryISO2 == country_code
                ]
            else:
                filtered_codes = all_mock_codes

            mock_result = MagicMock()
            mock_result.all.return_value = filtered_codes
            return mock_result

        mock_db.exec.side_effect = mock_exec

        response = await get_country_swift_codes("US", mock_db)

        # print([code.countryISO2 for code in response.swiftCodes])
        # Verify only US codes returned
        assert all(code.countryISO2 == "US" for code in response.swiftCodes)
        assert len(response.swiftCodes) == 3
