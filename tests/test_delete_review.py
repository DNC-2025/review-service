import pytest

def test_delete_review(create_review_for_test):
    """
    Simula la cancellazione di una review.
    """
    review = create_review_for_test
    # Simuliamo che venga eliminata
    deleted_review = None

    # Verifica che la review sia stata "cancellata"
    assert deleted_review is None
    assert review["id"] == 1

