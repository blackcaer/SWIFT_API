from pydantic import BaseModel, field_validator, model_validator
from typing import List
from app.validators import (
    SwiftCodeValidationError,
    validate_swift_code_format,
    validate_countryISO2code_format,
    validate_bank_name,
    validate_country_name,
)


class SwiftCodeBase(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    isHeadquarter: bool
    swiftCode: str


class SwiftCodeCreate(BaseModel):
    swiftCode: str
    bankName: str
    address: str
    countryISO2: str
    countryName: str
    isHeadquarter: bool

    @field_validator("swiftCode")
    @classmethod
    def validate_swiftCode(cls, v: str) -> str:
        try:
            return validate_swift_code_format(v)
        except SwiftCodeValidationError as e:
            raise ValueError(str(e))

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        return validate_address(v)

    @field_validator("countryISO2")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        return validate_countryISO2code_format(v)

    @field_validator("bankName")
    @classmethod
    def validate_bank_name(cls, v: str) -> str:
        return validate_bank_name(v)

    @field_validator("countryName")
    @classmethod
    def validate_country_name(cls, v: str) -> str:
        return validate_country_name(v)

    @model_validator(mode="after")
    def validate_headquarter_status(self) -> "SwiftCodeCreate":
        if self.isHeadquarter != self.swiftCode.endswith("XXX"):
            raise ValueError("isHeadquarter must match swiftCode suffix")
        return self


class HeadquarterSwiftCodeResponse(SwiftCodeBase):
    countryName: str
    branches: List[SwiftCodeBase]


class BranchSwiftCodeResponse(SwiftCodeBase):
    countryName: str


class CountrySwiftCodesResponse(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeBase]


class SwiftCodeCreateResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str
