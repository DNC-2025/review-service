from app.crud.crud_review import create_review, get_review_by_id

def test_get_review_by_id(db_session):
    created = create_review(db_session, 1, 1, 4, "Nice")

    result = get_review_by_id(db_session, created.id)

    assert result.id == created.id
    assert result.rating == 4
    assert result.review_text == "Nice"
