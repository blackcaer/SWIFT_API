from typing import Union
from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from app.models import SwiftCode
from app.schemas import (
    HeadquarterSwiftCodeResponse,
    BranchSwiftCodeResponse,
    CountrySwiftCodesResponse,
    MessageResponse,
    SwiftCodeBase,
)
from app.database import SessionDep
from app.validators import (
    CountryISO2CodeValidationError,
    SwiftCodeValidationError,
    validate_countryISO2code_format,
    validate_swift_code_format,
)
from app.logger import logger
from fastapi import status
from app.schemas import SwiftCodeCreate, SwiftCodeCreateResponse
from app.models import SwiftCode
from app.utils import validate_with_logging

router = APIRouter(prefix="/v1/swift-codes")


@router.get(
    "/{swiftCode}",
    response_model=Union[HeadquarterSwiftCodeResponse, BranchSwiftCodeResponse],
)
async def get_swift_code(swiftCode: str, db: SessionDep):
    swiftCode = validate_with_logging(validate_swift_code_format, swiftCode, "SWIFT code")
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

    countryISO2code = validate_with_logging(
        validate_countryISO2code_format, countryISO2code, "countryISO2code"
    )

    db_codes = db.exec(select(SwiftCode).where(SwiftCode.countryISO2 == countryISO2code)).all()

    country_codes_converted = [code.model_dump() for code in db_codes]

    if not country_codes_converted:
        logger.warning(f"No SWIFT codes found for country code: {countryISO2code}")
        raise HTTPException(status_code=404, detail="No SWIFT codes found for this country code")

    countryName = country_codes_converted[0]["countryName"]

    logger.info(
        f"Found {len(country_codes_converted)} SWIFT codes for country code: {countryISO2code}"
    )

    return CountrySwiftCodesResponse.model_validate(
        {
            "countryISO2": countryISO2code,
            "countryName": countryName,
            "swiftCodes": country_codes_converted,
        }
    )


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_swift_code(swiftCode: SwiftCodeCreate, db: SessionDep):   
    # Schema automatically validates the SWIFT code format
    logger.info(f"Received request to create SWIFT code: {swiftCode.swiftCode}")

    if db.get(SwiftCode, swiftCode.swiftCode):
        logger.warning(f"SWIFT code {swiftCode.swiftCode} already exists in the database")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SWIFT code already exists"
        )

    # For branches, verify headquarters exists
    if not swiftCode.isHeadquarter:
        hq_code = swiftCode.swiftCode[:8] + "XXX"
        if not db.get(SwiftCode, hq_code):
            logger.error(
                f"Headquarter SWIFT code {hq_code} not found for branch {swiftCode.swiftCode}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corresponding headquarter not found. Add headquarter first",
            )
        else:
            logger.info(
                f"Headquarter SWIFT code {hq_code} exists for branch {swiftCode.swiftCode}"
            )

    try:
        logger.info(f"Creating new SWIFT code: {swiftCode.swiftCode}")
        db_swift = SwiftCode(**swiftCode.model_dump())
        db.add(db_swift)
        db.commit()
        logger.info(f"SWIFT code {swiftCode.swiftCode} created successfully")
        return MessageResponse(message=f"SWIFT code {swiftCode.swiftCode} created successfully")
    except Exception as e:
        logger.exception(f"Failed to create SWIFT code {swiftCode.swiftCode}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed"
        )
