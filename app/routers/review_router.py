from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.schemas.review_schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.schemas.response_model import ResponseModel
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

# ---------------------------- CREATE ---------------------------------
@router.post("/", response_model=ResponseModel[ReviewResponse])
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
@router.get("/{review_id}", response_model=ResponseModel[ReviewResponse])
def get_review_by_id_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = get_review_by_id(db, review_id)
    if not review:
        return ResponseModel(success=False, message="Review not found")
    return ResponseModel(success=True, data=review)

# ---------------------------- READ by USER ---------------------------
@router.get("/by-user/{user_id}", response_model=ResponseModel[List[ReviewResponse]])
def get_reviews_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    reviews = get_reviews_by_user(db, user_id)
    return ResponseModel(success=True, data=reviews)

# ---------------------------- READ by CONTENT ------------------------
@router.get("/by-content/{content_id}", response_model=ResponseModel[List[ReviewResponse]])
def get_reviews_by_content_endpoint(content_id: int, db: Session = Depends(get_db)):
    reviews = get_reviews_by_content(db, content_id)
    return ResponseModel(success=True, data=reviews)

# ---------------------------- UPDATE --------------------------------
@router.put("/{review_id}", response_model=ResponseModel[ReviewResponse])
def update_review_endpoint(review_id: int, update_data: ReviewUpdate, db: Session = Depends(get_db)):
    review = update_review(
        db=db,
        review_id=review_id,
        rating=update_data.rating,
        review_text=update_data.review_text
    )
    if not review:
        return ResponseModel(success=False, message="Review not found")
    return ResponseModel(success=True, message="Review updated successfully", data=review)

# ---------------------------- DELETE --------------------------------
@router.delete("/{review_id}", response_model=ResponseModel[None])
def delete_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    review = delete_review(db, review_id)
    if not review:
        return ResponseModel(success=False, message="Review not found")
    return ResponseModel(success=True, message="Review deleted successfully")


