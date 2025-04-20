import pytest
from app.models import SwiftCode
from app.schemas import SwiftCodeCreate


def test_swift_code_model_creation():
    """Test that SwiftCode model can be created with valid data"""
    code = SwiftCode(
        swiftCode="CITIUS33XXX",
        bankName="Citibank",
        address="New York",
        countryISO2="US",
        countryName="UNITED STATES",
        isHeadquarter=True,
    )
    assert code.swiftCode == "CITIUS33XXX"
    assert code.isHeadquarter is True


def test_swift_code_validations():
    """Test all validation scenarios"""
    # Test cases for isHeadquarter validation
    test_cases = [
        # (swift_code, is_headquarter, should_pass)
        ("CITIUS33XXX", True, True),  # Valid HQ
        ("CITIUS33XXX", False, False),  # Invalid HQ
        ("CITIUS33001", False, True),  # Valid branch
        ("CITIUS33001", True, False),  # Invalid branch
    ]

    for swift_code, is_headquarter, should_pass in test_cases:
        if should_pass:
            SwiftCodeCreate(
                swiftCode=swift_code,
                bankName="Bank",
                address="Address",
                countryISO2="US",
                countryName="USA",
                isHeadquarter=is_headquarter,
            )
        else:
            with pytest.raises(ValueError, match="must match swiftCode suffix"):
                SwiftCodeCreate(
                    swiftCode=swift_code,
                    bankName="Bank",
                    address="Address",
                    countryISO2="US",
                    countryName="USA",
                    isHeadquarter=is_headquarter,
                )


def test_countryISO2code_validation():
    """Test country ISO2 validation"""
    with pytest.raises(ValueError):
        SwiftCodeCreate(
            swiftCode="CITIUS33XXX",
            bankName="Bank",
            address="Address",
            countryISO2="USA",  # Too long
            countryName="USA",
            isHeadquarter=True,
        )
