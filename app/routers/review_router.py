from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
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
from app.core.logger import logger
from app.core.cache import cache, make_cache_key, get_from_cache, set_in_cache

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not Found"}}
)

# ---------------------------- CREATE ---------------------------------
@router.post(
    "/",
    response_model=ReviewResponse,
    summary="Crea una nuova recensione",
    description="Permette di creare una nuova recensione associata ad un utente e un contenuto.",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
def create_review_endpoint(request : Request , review_data: ReviewCreate, db: Session = Depends(get_db)):
    logger.info(f"[CREATE] Richiesta creazione recensione user_id={review_data.user_id}, content_id={review_data.content_id}")
    review = create_review(
        db=db,
        user_id=review_data.user_id,
        content_id=review_data.content_id,
        rating=review_data.rating,
        review_text=review_data.review_text
    )
    logger.success(f"[CREATE] Recensione creata con id={review.id}")

    # Invalidate cache
    cache_keys_to_invalidate = [
        make_cache_key(f"reviews_user_{review_data.user_id}"),
        make_cache_key(f"reviews_content_{review_data.content_id}")
    ]
    for key in cache_keys_to_invalidate:
        if key in cache:
            del cache[key]
            logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {key}")

    return {
    "success": True,
    "data": review
}   # restituiamo direttamente il Pydantic model

# ---------------------------- READ by ID -----------------------------
@router.get(
    "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Ottieni una recensione tramite ID",
)
@limiter.limit("10/minute")
def get_review_by_id_endpoint(
    request: Request,
    review_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"[READ] Richiesta recensione id={review_id}")

    cache_key = make_cache_key(f"review_{review_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] review_id={review_id}")
        return cached

    review = get_review_by_id(db, review_id)
    if not review:
        logger.warning(f"[READ] Recensione non trovata: id={review_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    response = {
        "success": True,
        "data": review
    }

    set_in_cache(cache_key, response)
    logger.info(f"[CACHE SET] review_id={review_id}")

    return response


# ---------------------------- READ by USER ---------------------------
@router.get(
    "/by-user/{user_id}",
     response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite User ID",
)
@limiter.limit("10/minute")
def get_reviews_by_user_endpoint(request: Request, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"[READ] Richiesta recensioni per user_id={user_id}")

    cache_key = make_cache_key(f"reviews_user_{user_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] reviews_user_id={user_id}")
        return cached

    reviews = get_reviews_by_user(db, user_id)
    response = {
        "success": True,
        "data": reviews
    }

    set_in_cache(cache_key, response)
    logger.info(f"[CACHE SET] reviews_user_id={user_id}")

    return response

# ---------------------------- READ by CONTENT ------------------------
@router.get(
   "/by-content/{content_id}",
    response_model=ResponseModel[List[ReviewResponse]],
    summary="Ottieni recensioni tramite Content ID",
)
@limiter.limit("10/minute")
def get_reviews_by_content_endpoint(
    request: Request,
    content_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"[READ] Richiesta recensioni per content_id={content_id}")

    cache_key = make_cache_key(f"reviews_content_{content_id}")
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] reviews_content_id={content_id}")
        return cached

    reviews = get_reviews_by_content(db, content_id)

    response = {
        "success": True,
        "data": reviews
    }

    set_in_cache(cache_key, response)
    logger.info(f"[CACHE SET] reviews_content_id={content_id}")

    return response

# ---------------------------- UPDATE --------------------------------
@router.put(
     "/{review_id}",
    response_model=ResponseModel[ReviewResponse],
    summary="Aggiorna una recensione",
)
@limiter.limit("5/minute")
def update_review_endpoint(
    request: Request,
    review_id: int,
    update_data: ReviewUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"[UPDATE] Richiesta aggiornamento recensione id={review_id}")

    review = update_review(
        db=db,
        review_id=review_id,
        rating=update_data.rating,
        review_text=update_data.review_text
    )
    if not review:
        logger.warning(f"[UPDATE] Recensione non trovata: id={review_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    # Cache invalidation
    keys_to_invalidate = [
        make_cache_key(f"review_{review_id}"),
        make_cache_key(f"reviews_user_{review.user_id}"),
        make_cache_key(f"reviews_content_{review.content_id}")
    ]
    for key in keys_to_invalidate:
        if key in cache:
            del cache[key]
            logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {key}")

    logger.success(f"[UPDATE] Recensione aggiornata: id={review_id}")

    return {
        "success": True,
        "data": review
    }
# ---------------------------- DELETE --------------------------------
@router.delete(
    "/{review_id}",
    response_model=ResponseModel[None],
    status_code=status.HTTP_200_OK,
    summary="Elimina una recensione",
)
@limiter.limit("3/minute")
def delete_review_endpoint(
    request: Request,
    review_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"[DELETE] Richiesta eliminazione recensione id={review_id}")

    # Recuperiamo la review per cache invalidation
    review = get_review_by_id(db, review_id)
    if not review:
        logger.warning(f"[DELETE] Recensione non trovata: id={review_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    delete_review(db, review_id)

    # Cache invalidation
    keys_to_invalidate = [
        make_cache_key(f"review_{review_id}"),
        make_cache_key(f"reviews_user_{review.user_id}"),
        make_cache_key(f"reviews_content_{review.content_id}")
    ]
    for key in keys_to_invalidate:
        if key in cache:
            del cache[key]
            logger.info(f"[CACHE INVALIDATE] Chiave rimossa: {key}")

    logger.success(f"[DELETE] Recensione eliminata: id={review_id}")

    return {
        "success": True,
        "data": None
    }

# ------------------------- PAGINATION by USER -----------------------
@router.get(
     "/by-user/{user_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per User ID",
)
@limiter.limit("10/minute")
def get_reviews_by_user_paginated_endpoint(
    request: Request,
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("id"),
    order_desc: bool = Query(False),
    db: Session = Depends(get_db)
):
    logger.info(f"[PAGINATION] Richiesta recensioni paginate per user_id={user_id}")
    cache_key = make_cache_key(
        f"reviews_user_{user_id}_limit{limit}_offset{offset}_orderby{order_by}_desc{order_desc}"
    )
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] {cache_key}")
        return cached

    result = paginated_reviews(
        db=db,
        user_id=user_id,
        content_id=None,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_desc=order_desc
    )

    response = {"success": True, "data": result}
    set_in_cache(cache_key, response)
    logger.info(f"[CACHE SET] {cache_key}")

    return response
# ------------------------- PAGINATION by CONTENT -----------------------
@router.get(
    "/by-content/{content_id}/paginated",
    response_model=ResponseModel[PaginatedResponse[ReviewResponse]],
    summary="Recensioni paginate per Content ID",
)
@limiter.limit("10/minute")
def get_reviews_by_content_paginated_endpoint(
    request: Request,
    content_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    db: Session = Depends(get_db)
):
    logger.info(f"[PAGINATION] Richiesta recensioni paginate per content_id={content_id}")
    cache_key = make_cache_key(
        f"reviews_content_{content_id}_limit{limit}_offset{offset}_orderby{order_by}_desc{order_desc}"
    )
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"[CACHE HIT] {cache_key}")
        return cached

    result = paginated_reviews(
        db=db,
        user_id=None,
        content_id=content_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_desc=order_desc
    )

    response = {"success": True, "data": result}
    set_in_cache(cache_key, response)
    logger.info(f"[CACHE SET] {cache_key}")

    return response

