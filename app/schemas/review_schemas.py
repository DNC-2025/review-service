# review_schemas.py
from pydantic import BaseModel, Field, validator

# -------------------- CREATE --------------------
class ReviewCreate(BaseModel):
    user_id: int                          # id dell'utente
    content_id: int                       # id del contenuto
    rating: int = Field(..., ge=1, le=5)  # rating da 1 a 5
    review_text: str | None = None        # testo recensione, opzionale

    # -------------------- VALIDATOR --------------------
    @validator("review_text", always=True)
    def review_text_not_empty(cls, v):
        # se review_text esiste, non deve essere vuoto
        if v is not None and v.strip() == "":
            raise ValueError("Il testo della recensione non può essere vuoto")
        return v

# -------------------- UPDATE --------------------
class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)  # rating opzionale
    review_text: str | None = None                 # testo opzionale

    @validator("review_text")
    def review_text_not_empty(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Il testo della recensione non può essere vuoto")
        return v

# -------------------- RESPONSE --------------------
class ReviewResponse(BaseModel):
    id: int
    user_id: int
    content_id: int
    rating: int
    review_text: str | None

    class Config: orm_mode = True  # permette la serializzazione da oggetti SQLAlchemy


