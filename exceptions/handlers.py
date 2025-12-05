from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.response_model import ResponseModel

# -------------------- 404 and HTTP EXCEPTION HANDLER --------------------
async def http_exception_handler(request: Request, exc: HTTPException):
    response = ResponseModel(
        success=False,
        message=exc.detail,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )

# -------------------- SQLALCHEMY EXCEPTION HANDLER --------------------
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    response = ResponseModel(
        success=False,
        message="SQLAlchemy / DB error",
        data={"type": str(exc.__class__.__name__)},
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )

# -------------------- Unexpected errors EXCEPTION HANDLER --------------------
async def unhandled_exception_handler(request: Request, exc: Exception):
    response = ResponseModel(
        success=False,
        message="Errore imprevisto nel server/db",
        data={"type": str(exc.__class__.__name__)},
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )



