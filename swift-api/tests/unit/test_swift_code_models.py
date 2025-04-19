from sqlmodel import Session, SQLModel, create_engine
from app.models import SwiftCode


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
    assert code.countryISO2 == "US"
    assert code.countryName == "UNITED STATES"
