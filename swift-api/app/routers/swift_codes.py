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
from app.validators import SwiftCodeValidationError, validate_swift_code_format
from app.logger import logger  # Import logger

router = APIRouter(prefix="/v1/swift-codes")


@router.get(
    "/{swiftCode}",
    response_model=Union[HeadquarterSwiftCodeResponse, BranchSwiftCodeResponse],
)
async def get_swift_code(swiftCode: str, db: SessionDep):
    try:
        swiftCode = validate_swift_code_format(swiftCode)
    except SwiftCodeValidationError as e:
        logger.error(f"Validation error for SWIFT code {swiftCode}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during validation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    logger.info(f"SWIFT code: {swiftCode} is valid")
    
    db_code = db.get(SwiftCode, swiftCode)
    
    if not db_code:
        logger.warning(f"SWIFT code not found: {swiftCode}")
        raise HTTPException(status_code=404, detail="SWIFT code not found")

    if db_code.isHeadquarter:
        logger.info(f"SWIFT code {swiftCode} is a headquarter code")
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
    else:
        logger.info(f"SWIFT code {swiftCode} is a branch code")
        logger.warning(f"Branch swift code: {db_code}, {type(db_code)}")
        logger.warning(
            f"Branch swift code: {db_code.swiftCode}, {type(db_code.swiftCode)}"
        )
        logger.warning(
            f"Branch swift code: {db_code.model_dump()}, {type(db_code.model_dump())}"
        )

        return BranchSwiftCodeResponse.model_validate(db_code)
