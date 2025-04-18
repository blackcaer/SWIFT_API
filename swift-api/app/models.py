from typing import Optional
from sqlmodel import Field, SQLModel


# Model testowy
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str


# Modele dla SWIFT codes
class SwiftCodeBase(SQLModel):
    swiftCode: str = Field(primary_key=True)
    bankName: str
    address: str
    countryISO2: str = Field(max_length=2)
    countryName: str
    isHeadquarter: bool = False


class SwiftCode(SwiftCodeBase, table=True):
    pass


class SwiftCodeRead(SwiftCodeBase):
    pass


class SwiftCodeCreate(SwiftCodeBase):
    pass
