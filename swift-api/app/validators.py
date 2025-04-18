from fastapi import HTTPException


def validate_swift_code(swift_code: str) -> str:
    swift_code = swift_code.upper()
    if len(swift_code) not in (8, 11):
        raise HTTPException(
            status_code=400, detail="SWIFT code must be 8 or 11 characters long"
        )
    if not swift_code[:6].isalpha():
        raise HTTPException(
            status_code=400, detail="First 6 characters must be alphabetic"
        )
    if not swift_code[6:].isalnum():
        raise HTTPException(
            status_code=400, detail="Characters 7-8 or 7-11 must be alphanumeric"
        )
    # TODO : Add more specific validation rules for the SWIFT code format
    return swift_code
