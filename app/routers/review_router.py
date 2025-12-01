from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.crud.crud_review import (
    create_review,
    get_review_by_id,
    get_reviews_by_user,
    get_reviews_by_content,
    update_review,
    delete_review
)
from app.schemas.review_schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not Found"}}
)

# ---------------------------- CREATE ---------------------------------
@router.post("/", response_model=ReviewResponse)
def create_review_endpoint(review_data: ReviewCreate, db: Session = Depends(get_db)):
    review = create_review(
        db=db,
        user_id=review_data.user_id,
        content_id=review_data.content_id,
        rating=review_data.rating,
        review_text=review_data.review_text
    )
    return review

# ---------------------------- READ by ID -----------------------------
@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_by_id_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

# ---------------------------- READ by USER ---------------------------
@router.get("/by-user/{user_id}", response_model=list[ReviewResponse])
def get_reviews_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_reviews_by_user(db, user_id)

# ---------------------------- READ by CONTENT ------------------------
@router.get("/by-content/{content_id}", response_model=list[ReviewResponse])
def get_reviews_by_content_endpoint(content_id: int, db: Session = Depends(get_db)):
    return get_reviews_by_content(db, content_id)

# ---------------------------- UPDATE --------------------------------
@router.put("/{review_id}", response_model=ReviewResponse)
def update_review_endpoint(review_id: int, update_data: ReviewUpdate, db: Session = Depends(get_db)):
    review = update_review(
        db=db,
        review_id=review_id,
        rating=update_data.rating,
        review_text=update_data.review_text
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

# ---------------------------- DELETE --------------------------------
@router.delete("/{review_id}")
def delete_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = delete_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}
