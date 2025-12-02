from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ---------------------- Input per creare review ----------------------
class ReviewCreate(BaseModel):
    user_id: int = Field(..., description="ID dell'utente")
    content_id: int = Field(..., description="ID del contenuto")
    rating: int = Field(..., ge=1, le=5, description="Valutazione da 1 a 5")
    review_text: Optional[str] = Field(None, description="Testo della recensione")

# ---------------------- Input per aggiornare review -------------------
class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Valutazione da 1 a 5")
    review_text: Optional[str] = Field(None, description="Testo della recensione")

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

        
