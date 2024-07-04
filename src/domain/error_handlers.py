from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Кастомный обработчик ошибки при неккоректном вводе параметров since и until"""
    errors = exc.errors()
    details = [
        {
            "loc": error["loc"],
            "msg": f"Invalid parameter: {error['loc'][-1]}. {error['msg']}"
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": 'Неверный формат параметров запроса since или until'}
    )