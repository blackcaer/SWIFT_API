from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from app.models import SwiftCode
from app.schemas import SwiftCodeResponse, BranchResponse
from app.database import SessionDep

router = APIRouter(prefix="/v1/swift-codes")


@router.get("/{swiftCode}", response_model=SwiftCodeResponse)
async def get_swiftCode(swiftCode: str, db: SessionDep):
    db_code = db.get(SwiftCode, swiftCode.upper())
    if not db_code:
        raise HTTPException(status_code=404, detail="SWIFT code not found")

    response = SwiftCodeResponse.model_validate(db_code)

    if db_code.isHeadquarter:
        branches = db.exec(
            select(SwiftCode).where(
                SwiftCode.swiftCode.startswith(db_code.swiftCode[:8]),
                SwiftCode.swiftCode != db_code.swiftCode,
            )
        ).all()
        response.branches = [BranchResponse.model_validate(b) for b in branches]

    return response
