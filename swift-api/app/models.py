from typing import Optional, Self
from sqlmodel import Field, SQLModel
from pydantic import field_validator, model_validator
from app.validators import (
    validate_swift_code_format,
    validate_countryISO2code_format,
    validate_address,
    validate_bank_name,
    validate_country_name,
)
from pydantic import ValidationInfo


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str


class SwiftCodeModelBase(SQLModel):
    swiftCode: str = Field(
        primary_key=True, max_length=11, description="SWIFT code (8 or 11 chars)"
    )

    bankName: str = Field(max_length=100)
    address: str = Field(max_length=250, default="")
    countryISO2: str = Field(min_length=2, max_length=2, description="ISO 2-letter country code")
    countryName: str = Field(max_length=60)
    isHeadquarter: Optional[bool] = Field(default=None)

    @field_validator("swiftCode")
    @classmethod
    def validate_swift_code(cls, v: str) -> str:
        return validate_swift_code_format(v)

    @field_validator("countryISO2")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        return validate_countryISO2code_format(v)

    @field_validator("address")
    @classmethod
    def validate_address_field(cls, v: str) -> str:
        return validate_address(v)

    @field_validator("bankName")
    @classmethod
    def validate_bank_name_field(cls, v: str) -> str:
        return validate_bank_name(v)

    @field_validator("countryName")
    @classmethod
    def validate_country_name_field(cls, v: str) -> str:
        return validate_country_name(v)

    # I would only set isHeadquarter automatically but task requires it to be set manually in POST request, so I have to handle it
    @model_validator(mode="after")
    def validate_headquarter_logic(self) -> Self:
        expected_status = self.swiftCode.endswith("XXX")

        # Manual setting of isHeadquarter (not None)
        if self.isHeadquarter is not None:
            if self.isHeadquarter != expected_status:
                raise ValueError(
                    f"Invalid isHeadquarter. For SWIFT '{self.swiftCode}' "
                    f"expected {expected_status}, got {self.isHeadquarter}"
                )
            return self

        # Automatic setting of isHeadquarter (None)
        self.isHeadquarter = expected_status
        return self

    @field_validator("swiftCode", mode="after")
    @classmethod
    def update_headquarter_status(cls, v: str, info: ValidationInfo) -> str:
        if info.data and "isHeadquarter" in info.data:
            expected = v.endswith("XXX")
            if info.data["isHeadquarter"] != expected:
                info.data["isHeadquarter"] = expected
        return v


class SwiftCode(SwiftCodeModelBase, table=True):
    pass


class SwiftCodeRead(SwiftCodeModelBase):
    pass


class SwiftCodeCreate(SwiftCodeModelBase):
    pass
