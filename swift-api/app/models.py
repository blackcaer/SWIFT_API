from typing import Optional
from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str


class SwiftCodeModelBase(SQLModel):
    swiftCode: str = Field(
        primary_key=True, max_length=11, description="SWIFT code (8 or 11 chars)"
    )

    bankName: str = Field(max_length=100)
    address: str = Field(max_length=250)
    countryISO2: str = Field(
        max_length=2, index=True, description="ISO 2-letter country code"
    )
    countryName: str = Field(max_length=60)
    isHeadquarter: bool = Field(default=False)


class SwiftCode(SwiftCodeModelBase, table=True):
    pass


class SwiftCodeRead(SwiftCodeModelBase):
    pass


class SwiftCodeCreate(SwiftCodeModelBase):
    pass
