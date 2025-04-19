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
from app.validators import CountryISO2CodeValidationError, SwiftCodeValidationError, validate_countryISO2code_format, validate_swift_code_format
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
        logger.exception(f"Unexpected error during swift_code validation: {e}")
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
        return BranchSwiftCodeResponse.model_validate(db_code.model_dump())


@router.get(
    "/country/{countryISO2code}",
    response_model=CountrySwiftCodesResponse,
)
async def get_country_swift_codes(countryISO2code: str, db: SessionDep):
    try:
        countryISO2code = validate_countryISO2code_format(countryISO2code)
    except CountryISO2CodeValidationError as e:
        logger.error(f"Validation error for country code {countryISO2code}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during countryISO2code alidation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    logger.info(f"Country code: {countryISO2code} is valid")
    
    db_codes = db.exec(
        select(SwiftCode).where(SwiftCode.countryISO2 == countryISO2code)
    ).all()
    
    country_codes_converted = [code.model_dump() for code in db_codes]
    
    if not country_codes_converted:
        logger.warning(f"No SWIFT codes found for country code: {countryISO2code}")
        raise HTTPException(status_code=404, detail="No SWIFT codes found for this country code")
    
    countryName = country_codes_converted[0]["countryName"]

    logger.info(f"Found {len(country_codes_converted)} SWIFT codes for country code: {countryISO2code}")
    
    return CountrySwiftCodesResponse.model_validate(
        {"countryISO2":countryISO2code,
        "countryName":countryName,
        "swiftCodes": country_codes_converted}
    )