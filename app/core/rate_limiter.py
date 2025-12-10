from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.schemas.response_model import ResponseModel


# Limiter principale (usa IP come identificatore)
limiter = Limiter(key_func=get_remote_address)


# Handler per limite superato (HTTP 429)
def rate_limit_handler(request, exc):
    response = ResponseModel(
        success=False,
        message="Hai superato il limite massimo di richieste consentite.",
        status_code=429
    )
    return JSONResponse(status_code=429, content=response.dict())


# Funzione per inizializzare SlowAPI dentro FastAPI
def init_rate_limiter(app):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
