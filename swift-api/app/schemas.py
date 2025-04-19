from pydantic import BaseModel, field_validator
from typing import List
from app.validators import SwiftCodeValidationError, validate_swift_code_format


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