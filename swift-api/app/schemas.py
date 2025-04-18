from pydantic import BaseModel, field_validator
from typing import List

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
    isHeadquarter: bool = False

    @field_validator("swiftCode")
    @classmethod
    def validate_swiftCode(cls, v: str) -> str:
        if len(v) not in (8, 11):
            raise ValueError("SWIFT code must be 8 or 11 chars")
        return v.upper()

class HeadquarterSwiftCodeResponse(SwiftCodeBase):
    countryName: str
    branches: List[SwiftCodeBase]

class BranchSwiftCodeResponse(SwiftCodeBase):
    countryName: str

class CountrySwiftCodesResponse(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeBase]