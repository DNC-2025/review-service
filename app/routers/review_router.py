from fastapi import APIRouter, Depends, Query, status, Request  # <-- aggiunto Request
from sqlalchemy.orm import Session
from typing import List

from app.database.config import get_db
from app.schemas.review_schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.schemas.response_model import ResponseModel
from app.schemas.pagination import PaginatedResponse
from app.crud.crud_review import (
    create_review,
    get_review_by_id,
    get_reviews_by_user,
    get_reviews_by_content,
    update_review,
    delete_review,
    paginated_reviews
)
from app.core.rate_limiter import limiter
from app.core.logger import logger  # <-- import logger
from app.core.cache import cache, make_cache_key, get_from_cache, set_in_cache
router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not Found"}}
)

# ---------------------------- CREATE ---------------------------------
@router.post(
    "/",
    response_model=ResponseModel[ReviewResponse],
    summary="Crea una nuova recensione",
    description="Permette di creare una nuova recensione associata ad un utente e un contenuto.",
    status_code=status.HTTP_201_CREATED,
    responses={201: {"description": "Recensione creata con successo"}, 400: {"description": "Dati non validi"}, 500: {"description": "Errore interno del server"}}
)
@limiter.limit("3/minute")
def create_review_endpoint(request: Request, review_data: ReviewCreate, db: Session = Depends(get_db)):
    logger.info(f"[CREATE] Richiesta creazione recensione user_id={review_data.user_id}, content_id={review_data.content_id}")
    review = create_review(
        db=db,
        user_id=review_data.user_id,
        content_id=review_data.content_id,
        rating=review_data.rating,
        review_text=review_data.review_text
    )
    logger.success(f"[CREATE] Recensione creata con id={review.id}")

    # Invalidate cache: rimuove le pagine che potrebbero essere interessate
    cache_keys_to_invalidate = [
        make_cache_key(f"reviews_user_{review_data.user_id}"),
        make_cache_key(f"reviews_content_{review_data.content_id}")
    ]
    for key in cache_keys_to_invalidate:
        if key in cache:
            del cache[key]
            logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {key}")

    return ResponseModel(
        success=True,
        message="Review created successfully",
        data=review,
        status_code=status.HTTP_201_CREATED
    )


# ---------------------------- READ by ID -----------------------------
@router.get(
    "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Ottieni una recensione tramite ID",
    description="Restituisce una singola recensione basata sul suo ID.",
    responses={200: {"description": "Recensione trovata"}, 404: {"description": "Recensione non trovata"}}
)
@limiter.limit("10/minute")
def get_review_by_id_endpoint(request: Request, review_id: int, db: Session = Depends(get_db)):
    logger.info(f"[READ] Richiesta recensione id={review_id}")

    cache_key = make_cache_key(f"review_{review_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] review_id={review_id}")
        return ResponseModel(success=True, data=cached, status_code=status.HTTP_200_OK)
    else:
        logger.info(f"[CACHE MISS] review_id={review_id}")

    review = get_review_by_id(db, review_id)
    if not review:
        logger.warning(f"[READ] Recensione non trovata: id={review_id}")
        return ResponseModel(success=False, message="Review not found", data=None, status_code=status.HTTP_404_NOT_FOUND)

    # Set cache
    set_in_cache(cache_key, review)
    logger.info(f"[CACHE SET] review_id={review_id}")
    return ResponseModel(success=True, data=review, status_code=status.HTTP_200_OK)


# ---------------------------- READ by USER ---------------------------
@router.get(
    "/by-user/{user_id}",
    response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite User ID",
    description="Restituisce tutte le recensioni create da uno specifico utente.",
)
@limiter.limit("10/minute")
def get_reviews_by_user_endpoint(request: Request, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"[READ] Richiesta recensioni per user_id={user_id}")

    cache_key = make_cache_key(f"reviews_user_{user_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] reviews_user_id={user_id}")
        return ResponseModel(success=True, data=cached, status_code=status.HTTP_200_OK)
    else:
        logger.info(f"[CACHE MISS] reviews_user_id={user_id}")

    reviews = get_reviews_by_user(db, user_id)
    set_in_cache(cache_key, reviews)
    logger.info(f"[CACHE SET] reviews_user_id={user_id}")
    return ResponseModel(success=True, data=reviews, status_code=status.HTTP_200_OK)
# ---------------------------- READ by CONTENT ------------------------
@router.get(
    "/by-content/{content_id}",
    response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite Content ID",
    description="Restituisce tutte le recensioni relative ad uno specifico contenuto.",
)
@limiter.limit("10/minute")
def get_reviews_by_content_endpoint(request: Request, content_id: int, db: Session = Depends(get_db)):
    logger.info(f"[READ] Richiesta recensioni per content_id={content_id}")

    cache_key = make_cache_key(f"reviews_content_{content_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] reviews_content_id={content_id}")
        return ResponseModel(success=True, data=cached, status_code=status.HTTP_200_OK)
    else:
        logger.info(f"[CACHE MISS] reviews_content_id={content_id}")

    reviews = get_reviews_by_content(db, content_id)
    set_in_cache(cache_key, reviews)
    logger.info(f"[CACHE SET] reviews_content_id={content_id}")
    return ResponseModel(success=True, data=reviews, status_code=status.HTTP_200_OK)
# ---------------------------- UPDATE --------------------------------
@router.put(
    "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Aggiorna una recensione",
    description="Permette di modificare rating e/o testo di una recensione esistente.",
    responses={200: {"description": "Recensione aggiornata con successo"}, 404: {"description": "Recensione non trovata"}, 400: {"description": "Dati non validi"}}
)
@limiter.limit("5/minute")
def update_review_endpoint(request: Request, review_id: int, update_data: ReviewUpdate, db: Session = Depends(get_db)):
    logger.info(f"[UPDATE] Richiesta aggiornamento recensione id={review_id}")
    review = update_review(db=db, review_id=review_id, rating=update_data.rating, review_text=update_data.review_text)
    if not review:
        logger.warning(f"[UPDATE] Recensione non trovata: id={review_id}")
        return ResponseModel(success=False, message="Review not found", data=None, status_code=status.HTTP_404_NOT_FOUND)

    # Invalidate cache
    cache_key = make_cache_key(f"review_{review_id}")
    if cache_key in cache:
        del cache[cache_key]
        logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {cache_key}")

    logger.success(f"[UPDATE] Recensione aggiornata: id={review_id}")
    return ResponseModel(success=True, message="Review updated successfully", data=review, status_code=status.HTTP_200_OK)


# ---------------------------- DELETE --------------------------------
@router.delete(
    "/{review_id}",
    response_model=ResponseModel[None],
    summary="Elimina una recensione",
    description="Elimina una recensione esistente tramite ID.",
    responses={200: {"description": "Recensione eliminata con successo"}, 404: {"description": "Recensione non trovata"}}
)
@limiter.limit("3/minute")
def delete_review_endpoint(request: Request, review_id: int, db: Session = Depends(get_db)):
    logger.info(f"[DELETE] Richiesta eliminazione recensione id={review_id}")
    review = delete_review(db, review_id)
    if not review:
        logger.warning(f"[DELETE] Recensione non trovata: id={review_id}")
        return ResponseModel(success=False, message="Review not found", data=None, status_code=status.HTTP_404_NOT_FOUND)

    # Invalidate cache
    cache_key = make_cache_key(f"review_{review_id}")
    if cache_key in cache:
        del cache[cache_key]
        logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {cache_key}")

    logger.success(f"[DELETE] Recensione eliminata: id={review_id}")
    return ResponseModel(success=True, message="Review deleted successfully", status_code=status.HTTP_200_OK)


# ------------------------- PAGINATION by USER -----------------------
@router.get(
    "/by-user/{user_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per User ID",
    description="Restituisce le recensioni di un utente in formato paginato, con ordinamento e filtri opzionali.",
    responses={200: {"description": "Lista paginata restituita con successo"}}
)
@limiter.limit("10/minute")
def get_reviews_by_user_paginated_endpoint(
    request: Request,
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di elementi da restituire"),
    offset: int = Query(0, ge=0, description="Offset degli elementi"),
    order_by: str = Query("id", description="Campo su cui ordinare"),
    order_desc: bool = Query(False, description="True per ordinamento discendente"),
    db: Session = Depends(get_db)
):
    logger.info(f"[PAGINATION] Richiesta recensioni paginate per user_id={user_id}")
    cache_key = make_cache_key(f"reviews_user_{user_id}_limit{limit}_offset{offset}_orderby{order_by}_desc{order_desc}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] {cache_key}")
        return ResponseModel(success=True, data=cached, status_code=status.HTTP_200_OK)
    else:
        logger.info(f"[CACHE MISS] {cache_key}")

    result = paginated_reviews(db=db, user_id=user_id, content_id=None, limit=limit, offset=offset, order_by=order_by, order_desc=order_desc)
    set_in_cache(cache_key, result)
    logger.info(f"[CACHE SET] {cache_key}")
    return ResponseModel(success=True, data=result, status_code=status.HTTP_200_OK)


# ------------------------- PAGINATION by CONTENT -----------------------
@router.get(
    "/by-content/{content_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per Content ID",
    description="Restituisce le recensioni di un contenuto in formato paginato, con ordinamento e filtri opzionali.",
    responses={200: {"description": "Lista paginata restituita con successo"}}
)
@limiter.limit("10/minute")
def get_reviews_by_content_paginated_endpoint(
    request: Request,
    content_id: int,
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di elementi da restituire"),
    offset: int = Query(0, ge=0, description="Offset degli elementi"),
    order_by: str = Query("created_at", description="Campo su cui ordinare"),
    order_desc: bool = Query(True, description="True per ordinamento discendente"),
    db: Session = Depends(get_db)
):
    logger.info(f"[PAGINATION] Richiesta recensioni paginate per content_id={content_id}")
    cache_key = make_cache_key(f"reviews_content_{content_id}_limit{limit}_offset{offset}_orderby{order_by}_desc{order_desc}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] {cache_key}")
        return ResponseModel(success=True, data=cached, status_code=status.HTTP_200_OK)
    else:
        logger.info(f"[CACHE MISS] {cache_key}")

    result = paginated_reviews(db=db, user_id=None, content_id=content_id, limit=limit, offset=offset, order_by=order_by, order_desc=order_desc)
    set_in_cache(cache_key, result)
    logger.info(f"[CACHE SET] {cache_key}")
    return ResponseModel(success=True, data=result, status_code=status.HTTP_200_OK)
