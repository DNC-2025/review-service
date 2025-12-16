import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from app.schemas.response_model import ResponseModel

TESTING = os.getenv("TESTING", "0") == "1"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=not TESTING  # 🔧 Disabilita se TESTING=1
)

def rate_limit_exceeded_handler(request: Request, exc):
    response = ResponseModel(
        success=False,
        message="Troppi tentativi. Riprova tra qualche minuto.",
        status_code=429
    )
    return JSONResponse(status_code=429, content=response.dict())

