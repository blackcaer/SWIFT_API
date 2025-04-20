from fastapi import HTTPException
from app.logger import logger


def validate_with_logging(validator, value, name):
    try:
        validated = validator(value)
        logger.info(f"Validation for {name} passed")
        return validated
    except ValueError as e:
        logger.error(f"Validation failed for {name}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during validation of {name}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
