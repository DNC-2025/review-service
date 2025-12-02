from fastapi import Request , HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError , SQLAlchemyError

#--------------------404 and http EXCEPTION HANDLER --------------------
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
        "error"  : True,
        "message": exc.detail,
        "path"   : str(request.url)
        },
    )
#--------------------sqlalchemy EXCEPTION HANDLER --------------------
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={
        "error"  : True,
        "message": "sqlalchemy/db error" ,
        "detail"   : str(exc.__class__.__name__),
        "path"   : str(request.url)
        },
    )

#--------------------unbexpected  errors EXCEPTION HANDLER --------------------
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Errore imprevisto nel server/db",
            "type": str(exc.__class__.__name__),
            "path": str(request.url),
        },
    )

