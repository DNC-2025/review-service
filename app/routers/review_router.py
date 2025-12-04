from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.schemas.review_schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.schemas.response_model import ResponseModel
from typing import List  
from app.crud.crud_review import (
    create_review,
    get_review_by_id,
    get_reviews_by_user,
    get_reviews_by_content,
    update_review,
    delete_review
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not Found"}}
)
from fastapi import Query
from app.schemas.pagination import PaginatedResponse
from app.crud.crud_review import paginated_reviews


# ---------------------------- CREATE ---------------------------------
@router.post(
    "/",
    response_model=ResponseModel[ReviewResponse],
    summary="Crea una nuova recensione",
    description="Permette di creare una nuova recensione associata ad un utente e un contenuto.",
    status_code=201,
    responses={
        201: {"description": "Recensione creata con successo"},
        400: {"description": "Dati non validi"},
        500: {"description": "Errore interno del server"}
    }
)
def create_review_endpoint(review_data: ReviewCreate, db: Session = Depends(get_db)):
    review = create_review(
        db=db,
        user_id=review_data.user_id,
        content_id=review_data.content_id,
        rating=review_data.rating,
        review_text=review_data.review_text
    )
    return ResponseModel(success=True, message="Review created successfully", data=review)

# ---------------------------- READ by ID -----------------------------
@router.get(
    "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Ottieni una recensione tramite ID",
    description="Restituisce una singola recensione basata sul suo ID.",
    responses={
        200: {"description": "Recensione trovata"},
        404: {"description": "Recensione non trovata"}
    }
)
def get_review_by_id_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ResponseModel(success=True, data=review)

# ---------------------------- READ by USER ---------------------------
@router.get(
    "/by-user/{user_id}",
    response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite User ID",
    description="Restituisce tutte le recensioni create da uno specifico utente.",
)
def get_reviews_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    reviews = get_reviews_by_user(db, user_id)
    return ResponseModel(success=True, data=reviews)

# ---------------------------- READ by CONTENT ------------------------
@router.get(
    "/by-content/{content_id}",
    response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite Content ID",
    description="Restituisce tutte le recensioni relative ad uno specifico contenuto.",
)
def get_reviews_by_content_endpoint(content_id: int, db: Session = Depends(get_db)):
    reviews = get_reviews_by_content(db, content_id)
    return ResponseModel(success=True, data=reviews)

# ---------------------------- UPDATE --------------------------------
@router.put(
    "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Aggiorna una recensione",
    description="Permette di modificare rating e/o testo di una recensione esistente.",
    responses={
        200: {"description": "Recensione aggiornata con successo"},
        404: {"description": "Recensione non trovata"},
        400: {"description": "Dati non validi"}
    }
)
def update_review_endpoint(review_id: int, update_data: ReviewUpdate, db: Session = Depends(get_db)):
    review = update_review(
        db=db,
        review_id=review_id,
        rating=update_data.rating,
        review_text=update_data.review_text
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ResponseModel(success=True, message="Review updated successfully", data=review)

# ---------------------------- DELETE --------------------------------
@router.delete(
    "/{review_id}",
    response_model=ResponseModel[None],
    summary="Elimina una recensione",
    description="Elimina una recensione esistente tramite ID.",
    responses={
        200: {"description": "Recensione eliminata con successo"},
        404: {"description": "Recensione non trovata"}
    }
)
def delete_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = delete_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ResponseModel(success=True, message="Review deleted successfully")

# ------------------------- PAGINATION by USER -----------------------
@router.get(
    "/by-user/{user_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per User ID",
    description="Restituisce le recensioni di un utente in formato paginato, con ordinamento e filtri opzionali.",
    responses={200: {"description": "Lista paginata restituita con successo"}}
)
def get_reviews_by_user_paginated_endpoint(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di elementi da restituire"),
    offset: int = Query(0, ge=0, description="Offset degli elementi"),
    order_by: str = Query("id", description="Campo su cui ordinare"),
    order_desc: bool = Query(False, description="True per ordinamento discendente"),
    db: Session = Depends(get_db)
):
    result = paginated_reviews(
        db=db,
        user_id=user_id,
        content_id=None,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_desc=order_desc
    )
    return ResponseModel(success=True, data=result)

# ------------------------- PAGINATION by CONTENT -----------------------
@router.get(
    "/by-content/{content_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per Content ID",
    description="Restituisce le recensioni di un contenuto in formato paginato, con ordinamento e filtri opzionali.",
    responses={200: {"description": "Lista paginata restituita con successo"}}
)
def get_reviews_by_content_paginated_endpoint(
    content_id: int,
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di elementi da restituire"),
    offset: int = Query(0, ge=0, description="Offset degli elementi"),
    order_by: str = Query("created_at", description="Campo su cui ordinare"),
    order_desc: bool = Query(True, description="True per ordinamento discendente"),
    db: Session = Depends(get_db)
):
    result = paginated_reviews(
        db=db,
        user_id=None,
        content_id=content_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_desc=order_desc
    )
    return ResponseModel(success=True, data=result)
 