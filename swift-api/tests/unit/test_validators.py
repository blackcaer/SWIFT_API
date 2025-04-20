# tests/test_validators.py
from ast import List
import pytest
from app.validators import (
    CountryISO2CodeValidationError,
    validate_countryISO2code_format,
    validate_swift_code_format,
    SwiftCodeValidationError,
)


class TestValidateSwiftCodeFormat:
    VALID_HQ_CODE = "AAISALTRXXX"
    VALID_BRANCH_CODE = "BCHICLR10R2"

    @pytest.mark.parametrize("code", [VALID_HQ_CODE, VALID_BRANCH_CODE])
    def test_valid_swift_code(self, code):
        assert validate_swift_code_format(code) == code

    @pytest.mark.parametrize("code", [VALID_HQ_CODE, VALID_BRANCH_CODE])
    def test_valid_lowercase_swift_code(self, code):
        assert validate_swift_code_format(code.lower()) == code

    @pytest.mark.parametrize("code", [VALID_HQ_CODE, VALID_BRANCH_CODE])
    def test_valid_swift_code_with_spaces(self, code):
        ws = " \n\t\r\f\v " * 2
        assert validate_swift_code_format(ws + code + ws) == code

    @pytest.mark.parametrize(
        "code",
        [
            "BCH1CLR10R2",  # Numeric at position 4
            "BCHI1LR10R2",  # Numeric at position 5
            "BCHICLR10R$",  # Invalid character '$'
            "AAISAL$R",  # Invalid character '$' at position 7
            "123456TRXXX",  # Numeric in first 6 characters
            "ABC@#LTRXXX",  # Special characters in first 6 characters
            "AAISAL@RXXX",  # Invalid character '@' at position 7
            "AAISALTR#XX",  # Invalid character '#' at position 8
            "        ",  # Only whitespace
            "AAISAL RXXX",  # Space in the middle
            "A ISALTRXXX",  # Space in the middle
            "AAISAL R",  # Space in the middle
            "AAISALTRXX ",  # Space at the end
            " AISALTRXXX",  # Space at position 0
        ],
    )
    def test_invalid_swift_code(self, code):
        with pytest.raises(SwiftCodeValidationError):
            validate_swift_code_format(code)

    @pytest.mark.parametrize(
        "code",
        [
            "AAISALTR",  # Too short (do not support short SWIFT codes)
            "AAISALTRXX",  # Too short
            "AAISALTRX",  # Too short
            "BCHICLR10R23",  # Too long
            "",  # Empty string
            "A",  # Too short
            "AAISALT",  # Too short (7 characters)
            "AAISALTRXXXX",  # Too long (12 characters)
        ],
    )
    def test_invalid_swift_code_length(self, code):
        with pytest.raises(SwiftCodeValidationError):
            validate_swift_code_format(code)


class TestCountryISO2CodeFormat:
    VALID_COUNTRY_ISO2_CODES = ["US", "PL", "AU"]

    @pytest.mark.parametrize("code", VALID_COUNTRY_ISO2_CODES)
    def test_valid_countryISO2code(self, code):
        assert validate_countryISO2code_format(code) == code

    @pytest.mark.parametrize("code", VALID_COUNTRY_ISO2_CODES)
    def test_valid_lowercase_countryISO2code(self, code):
        assert validate_countryISO2code_format(code.lower()) == code

    @pytest.mark.parametrize("code", VALID_COUNTRY_ISO2_CODES)
    def test_valid_whitespace_countryISO2code(self, code):
        ws = " \n\t\r\f\v " * 2
        assert validate_countryISO2code_format(ws + code + ws) == code

    @pytest.mark.parametrize(
        "code",
        [
            "U",  # Too short
            "U ",  # Whitespace instead of character
            " U",  # Whitespace instead of character
            "USA",  # Too long
            "1A",  # Contains numeric character
            "A1",  # Contains numeric character
            "U$",  # Contains special character
            "P L",  # Space in the middle
            "US1",  # Extra numeric character
            "",  # Empty string
            "  ",  # Only whitespace
        ],
    )
    def test_invalid_countryISO2code(self, code):
        with pytest.raises(CountryISO2CodeValidationError):
            validate_countryISO2code_format(code)
