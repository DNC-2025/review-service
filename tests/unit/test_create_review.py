from app.crud.crud_review import create_review
from app.models.tables import Review

def test_create_review(db_session):
    # ACT
    review = create_review(
        db=db_session,
        user_id=1,
        content_id=2,
        rating=5,
        review_text="Great!"
    )

    # ASSERT
    assert isinstance(review, Review)
    assert review.id == 1  # primo inserimento
    assert review.user_id == 1
    assert review.content_id == 2
    assert review.rating == 5
    assert review.review_text == "Great!"
