# tests/test_validators.py
import pytest
from app.validators import validate_swift_code_format, SwiftCodeValidationError

# Example valid codes
VALID_HQ_CODE = "AAISALTRXXX"
VALID_SHORT_HQ_CODE = "AAISALTR"
VALID_BRANCH_CODE = "BCHICLR10R2"


def test_valid_swift_code():
    assert validate_swift_code_format(VALID_HQ_CODE) == VALID_HQ_CODE
    assert validate_swift_code_format(VALID_SHORT_HQ_CODE) == VALID_SHORT_HQ_CODE
    assert validate_swift_code_format(VALID_BRANCH_CODE) == VALID_BRANCH_CODE
    
def test_valid_lowercase_swift_code():
    assert validate_swift_code_format(VALID_HQ_CODE.lower()) == VALID_HQ_CODE
    assert validate_swift_code_format(VALID_SHORT_HQ_CODE.lower()) == VALID_SHORT_HQ_CODE
    assert validate_swift_code_format(VALID_BRANCH_CODE.lower()) == VALID_BRANCH_CODE

def test_valid_swift_code_with_spaces():
    ws=" \n\t\r\f\v "*2
    assert validate_swift_code_format(ws+VALID_HQ_CODE+ws) == VALID_HQ_CODE # Leading/trailing whitespace
    assert validate_swift_code_format(ws+VALID_SHORT_HQ_CODE+ws) == VALID_SHORT_HQ_CODE # Leading/trailing whitespace
    assert validate_swift_code_format(ws+VALID_BRANCH_CODE+ws) == VALID_BRANCH_CODE # Leading/trailing whitespace

def test_invalid_swift_code():
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("BCH1CLR10R2")  # Numeric at position 4
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("BCHI1LR10R2")  # Numeric at position 5
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("BCHICLR10R$")  # Invalid character '$'
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISAL$R")  # Invalid character '$' at position 7
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("123456TRXXX")  # Numeric in first 6 characters
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format(
            "ABC@#LTRXXX"
        )  # Special characters in first 6 characters
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISAL@RXXX")  # Invalid character '@' at position 7
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALTR#XX")  # Invalid character '#' at position 8
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("        ")  # Only whitespace
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISAL RXXX")  # Space in the middle
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("A ISALTRXXX")  # Space in the middle
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISAL R")  # Space in the middle
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALTRXX ")  # Space at the end
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format(" AISALTRXXX")  # Space at position 0

def test_invalid_swift_code_length():
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALTRXX")  # Too short
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALTRX")  # Too short
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("BCHICLR10R23")  # Too long
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("")  # Empty string
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("A")  # Too short
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALT")  # Too short (7 characters)
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format("AAISALTRXXXX")  # Too long (12 characters)
