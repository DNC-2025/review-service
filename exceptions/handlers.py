from fastapi import Request , HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError , SQLAlchemyError
from app.schemas.response_model import ResponseModel

#--------------------404 and http EXCEPTION HANDLER --------------------
async def http_exception_handler(request: Request, exc: HTTPException):
    response = ResponseModel(success=False, message=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )
#--------------------sqlalchemy EXCEPTION HANDLER --------------------
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    response = ResponseModel(
        success=False,
        message="SQLAlchemy / DB error",
        data={"type": str(exc.__class__.__name__)}
    )
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )

#--------------------unbexpected  errors EXCEPTION HANDLER --------------------
async def unhandled_exception_handler(request: Request, exc: Exception):
    response = ResponseModel(
        success=False,
        message="Errore imprevisto nel server/db",
        data={"type": str(exc.__class__.__name__)}
    )
    return JSONResponse(
        status_code=500,
        content=response.dict()
    ) 
