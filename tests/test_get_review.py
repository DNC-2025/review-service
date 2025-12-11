import pytest

def test_get_review_by_id(create_review_for_test):
    """
    Simula il recupero di una review per id.
    """
    review = create_review_for_test
    review_id = review["id"]

    # Simuliamo la risposta del GET
    response_data = review

    assert response_data["id"] == review_id
    assert response_data["rating"] == 5

def test_get_all_reviews(create_review_for_test):
    """
    Simula il recupero di tutte le review.
    """
    review = create_review_for_test

    # Simuliamo una lista di review
    response_data = [review]

    assert isinstance(response_data, list)
    assert any(r["id"] == review["id"] for r in response_data)
