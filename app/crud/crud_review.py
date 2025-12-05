from sqlalchemy.orm import Session
from app.models.tables import Review
from math import ceil



# create ---------------------------------------------------------------------------------------------------------------------

def create_review(db: Session , user_id : int , content_id : int , rating : int , review_text : str = None) :
    new_review  = Review(user_id=user_id , content_id = content_id , rating= rating , review_text = review_text)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
# lho commentato perche cosi per sbaglio nonne creo una doppia tabella. non più necessario.

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

# PAGINATION -------------------------------------------------------------------------------------------------------------------
# E filtri and ordinamenti------------------------------------------------------------------------------------------------------ 
from sqlalchemy.orm import Session
from app.models.tables import Review
from math import ceil

def paginated_reviews(     # Non serve più avere due funzioni separate (by_user e by_content), perché ora si puo  filtrare usando parametri.
    db: Session,
    user_id: int = None,
    content_id: int = None,
    rating_min: int = None,
    rating_max: int = None,
    limit: int = 10,
    offset: int = 0,
    order_by: str = "id",
    order_desc: bool = False
):
    query = db.query(Review)

    # FILTRI
    if user_id is not None:
        query = query.filter(Review.user_id == user_id)
    if content_id is not None:
        query = query.filter(Review.content_id == content_id)
    if rating_min is not None:
        query = query.filter(Review.rating >= rating_min)
    if rating_max is not None:
        query = query.filter(Review.rating <= rating_max)

    total = query.count()

    # ORDINAMENTO
    if hasattr(Review, order_by):
        column = getattr(Review, order_by)
        if order_desc:
            column = column.desc()
        query = query.order_by(column)
    else:
        query = query.order_by(Review.id)  # default fallback

    # PAGINAZIONE
    items = query.offset(offset).limit(limit).all()
    total_pages = ceil(total / limit) if total > 0 else 1
    current_page = offset // limit + 1
    next_offset = offset + limit if offset + limit < total else None
    prev_offset = offset - limit if offset - limit >= 0 else None

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "total_pages": total_pages,
        "current_page": current_page,
        "next_offset": next_offset,
        "prev_offset": prev_offset
    }




