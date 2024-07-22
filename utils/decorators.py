from functools import wraps

from fastapi import HTTPException


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Here you can add error logging
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500, detail="Internal server error")
    return wrapper
