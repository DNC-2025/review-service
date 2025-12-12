import pytest
from fastapi import status
from app.models.tables import Review

# -------------------------
# CREATE REVIEW
# -------------------------
def test_create_review_success(client):
    payload = {
        "user_id": 1,
        "content_id": 1,
        "rating": 5,
        "review_text": "Amazing content!"
    }
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == payload["user_id"]
    assert data["content_id"] == payload["content_id"]
    assert data["rating"] == payload["rating"]
    assert data["review_text"] == payload["review_text"]
    assert "id" in data


def test_create_review_error_missing_fields(client):
    # payload mancante di rating
    payload = {
        "user_id": 1,
        "content_id": 1,
        "review_text": "Incomplete!"
    }
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# -------------------------
# GET REVIEW
# -------------------------
def test_get_review_by_id_success(client, db_session):
    review = Review(user_id=2, content_id=2, rating=4, review_text="Nice!")
    db_session.add(review)
    db_session.commit()

    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == review.id
    assert data["rating"] == review.rating


def test_get_review_by_id_not_found(client):
    response = client.get("/reviews/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# -------------------------
# DELETE REVIEW
# -------------------------
def test_delete_review_success(client, db_session):
    review = Review(user_id=3, content_id=3, rating=3, review_text="To delete")
    db_session.add(review)
    db_session.commit()

    response = client.delete(f"/reviews/{review.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = db_session.query(Review).filter(Review.id == review.id).first()
    assert deleted is None


def test_delete_review_not_found(client):
    response = client.delete("/reviews/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# -------------------------
# UPDATE REVIEW
# -------------------------
def test_update_review_success(client, db_session):
    review = Review(user_id=4, content_id=4, rating=2, review_text="Needs improvement")
    db_session.add(review)
    db_session.commit()

    payload = {"rating": 5, "review_text": "Much better now!"}
    response = client.put(f"/reviews/{review.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == payload["rating"]
    assert data["review_text"] == payload["review_text"]


def test_update_review_not_found(client):
    payload = {"rating": 5, "review_text": "Nonexistent review"}
    response = client.put("/reviews/99999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_review_invalid_rating(client):
    payload = { "user_id" : 1,
               "content_id": 1,
                "rating" : 6, 
                "review_text" :"invalid rating"
                }

    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_review_empty_review_text(client):
    payload  = {
        "user_id": 1,
        "content_id": 1,
        "rating": 4,
        "review_text": ""
        }
    
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



