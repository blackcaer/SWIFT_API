# tests/test_validators.py
import pytest
from app.validators import validate_swift_code_format, SwiftCodeValidationError

VALID_HQ_CODE = "AAISALTRXXX"
VALID_SHORT_HQ_CODE = "AAISALTR"
VALID_BRANCH_CODE = "BCHICLR10R2"


@pytest.mark.parametrize(
    "code",[VALID_HQ_CODE,VALID_SHORT_HQ_CODE,VALID_BRANCH_CODE]
    )
def test_valid_swift_code(code):
    assert validate_swift_code_format(code) == code

@pytest.mark.parametrize(
    "code",[VALID_HQ_CODE,VALID_SHORT_HQ_CODE,VALID_BRANCH_CODE]
    )
def test_valid_lowercase_swift_code(code):
    assert validate_swift_code_format(code.lower()) == code

@pytest.mark.parametrize(
    "code",[VALID_HQ_CODE,VALID_SHORT_HQ_CODE,VALID_BRANCH_CODE]
    )
def test_valid_swift_code_with_spaces(code):
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
def test_invalid_swift_code(code):
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format(code)


@pytest.mark.parametrize(
    "code",
    [
        "AAISALTRXX",  # Too short
        "AAISALTRX",  # Too short
        "BCHICLR10R23",  # Too long
        "",  # Empty string
        "A",  # Too short
        "AAISALT",  # Too short (7 characters)
        "AAISALTRXXXX",  # Too long (12 characters)
    ],
)
def test_invalid_swift_code_length(code):
    with pytest.raises(SwiftCodeValidationError):
        validate_swift_code_format(code)
