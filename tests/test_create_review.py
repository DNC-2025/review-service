import pytest

def test_create_review_success(create_review_for_test):
    """
    Testa la creazione di una review.
    Usa la fixture fittizia create_review_for_test.
    """
    review = create_review_for_test
    assert review["rating"] == 5
    assert review["review_text"] == "Great content!"
    assert review["user_id"] == 1
    assert review["content_id"] == 1
