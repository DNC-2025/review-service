from sqlalchemy.orm import Session
from app.models.tables import Review

# create ---------------------------------------------------------------------------------------------------------------------

def create_review(db: Session , user_id : int , content_id : int , rating : int , review_text : str = None) :
    new_review = review = Review(user_id=user_id , content_id = content_id , rating= rating , review_text = review_text)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


# read ---------------------------------------------------------------------------------------------------------------------

def get_review_by_id(db: Session , review_id : int) :
    return db.query(Review).filter(Review.id == review_id).first()

def get_reviews_by_user(db:Session , user_id : int):
    return db.query(Review).filter(Review.user_id == user_id).all()


def get_reviews_by_content(db: Session, content_id: int):
    return db.query(Review).filter(Review.content_id == content_id).all()

# UPDATE ---------------------------------------------------------------------------------------------------------------------
def update_review(db: Session, review_id: int, rating: int = None, review_text: str = None):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    if rating is not None:
        review.rating = rating
    if review_text is not None:
        review.review_text = review_text
    db.commit()
    db.refresh(review)
    return review

# DELETE  ---------------------------------------------------------------------------------------------------------------------
def delete_review(db: Session, review_id: int):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    db.delete(review)
    db.commit()
    return review

