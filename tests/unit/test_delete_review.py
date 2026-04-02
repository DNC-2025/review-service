from app.crud.crud_review import create_review, delete_review, get_review_by_id

def test_delete_review(db_session):
    created = create_review(db_session, 1, 1, 3, "To delete")

    deleted = delete_review(db_session, created.id)

    assert deleted.id == created.id

    # Verifica che non esista più
    assert get_review_by_id(db_session, created.id) is None
