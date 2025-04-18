class SwiftCodeValidationError(ValueError):
    """Custom exception for SWIFT code validation"""
    pass

def validate_swift_code_format(swift_code: str) -> str:
    """
    Returns validated swift_code or raises SwiftCodeValidationError
    """
    swift_code = swift_code.upper().strip()
    
    if len(swift_code) not in (8, 11):
        raise SwiftCodeValidationError("SWIFT code must be 8 or 11 characters long")
    
    if not swift_code[:6].isalpha():
        raise SwiftCodeValidationError("First 6 characters must be alphabetic")
    
    if not swift_code[6:8].isalnum():
        raise SwiftCodeValidationError("Characters 7-8 must be alphanumeric")
    
    if len(swift_code) == 11 and not swift_code[8:].isalnum():
        raise SwiftCodeValidationError("Characters 9-11 must be alphanumeric")
    
    return swift_code