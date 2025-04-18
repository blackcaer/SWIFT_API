from typing import Union
from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from app.models import SwiftCode
from app.schemas import (
    HeadquarterSwiftCodeResponse,
    BranchSwiftCodeResponse,
    CountrySwiftCodesResponse,
    SwiftCodeBase,
)
from app.database import SessionDep
from app.validators import validate_swift_code

router = APIRouter(prefix="/v1/swift-codes")


@router.get(
    "/{swiftCode}",
    response_model=Union[HeadquarterSwiftCodeResponse, BranchSwiftCodeResponse],
)
async def get_swift_code(swiftCode: str, db: SessionDep):
    try:
        swiftCode = validate_swift_code(swiftCode)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_code = db.get(SwiftCode, swiftCode)
    if not db_code:
        raise HTTPException(status_code=404, detail="SWIFT code not found")

    if db_code.isHeadquarter:
        branches = db.exec(
            select(SwiftCode).where(
                SwiftCode.swiftCode.startswith(swiftCode[:8]),
                SwiftCode.swiftCode != swiftCode,
            )
        ).all()  # Temporary query to get branches TODO

        branches_converted = [
            SwiftCodeBase.model_validate(branch.model_dump()) for branch in branches
        ]

        return HeadquarterSwiftCodeResponse.model_validate(
            {**db_code.model_dump(), "branches": branches_converted}
        )

    return BranchSwiftCodeResponse.model_validate(db_code)
