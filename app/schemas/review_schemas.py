from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

# ---------------------- Input per creare review ----------------------
class ReviewCreate(BaseModel):
    user_id: int = Field(..., description="ID dell'utente")
    content_id: int = Field(..., description="ID del contenuto")
    rating: int = Field(..., ge=1, le=5, description="Valutazione da 1 a 5")
    review_text: Optional[str] = Field(None, description="Testo della recensione")

    # --- VALIDAZIONE: se review_text è presente deve avere almeno 10 caratteri ---
    @field_validator("review_text")
    def validate_review_text(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError("La recensione deve contenere almeno 10 caratteri")
        return v

    # --- VALIDAZIONE CONDIZIONALE ---
    # Se rating è 1 o 2, review_text diventa obbligatoria
    @model_validator(mode="after")
    def check_text_required_for_low_rating(self):
        if self.rating <= 2:
            if not self.review_text or len(self.review_text.strip()) < 10:
                raise ValueError(
                    "Per un rating basso (1-2) è obbligatorio inserire una recensione descrittiva (minimo 10 caratteri)."
                )
        return self


# ---------------------- Input per aggiornare review -------------------
class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Valutazione da 1 a 5")
    review_text: Optional[str] = Field(None, description="Testo della recensione")

    # --- VALIDAZIONE: se review_text presente deve avere min. 10 caratteri ---
    @field_validator("review_text")
    def validate_review_text(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError("Il testo della recensione deve contenere almeno 10 caratteri")
        return v


# ---------------------- Output dei dati ------------------------------
class ReviewResponse(BaseModel):
    id: int
    user_id: int
    content_id: int
    rating: int
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permette di restituire direttamente oggetti SQLAlchemy , pero se usi pydantic v1 bisogna usare il from_attributes **
