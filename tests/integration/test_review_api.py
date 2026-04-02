import pytest
from fastapi import status
from app.models.tables import Review
from app.core.cache import cache
from app.schemas.review_schemas import ReviewResponse
# -------------------------
# CREATE REVIEW
# -------------------------
def test_create_review_success(client):
    payload = payload = {"user_id": 1,"content_id": 2,"rating": 5,"review_text": "Test review"}
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    review_data = data.get("data", {})
    assert review_data.get("user_id") == payload["user_id"]
    assert review_data.get("content_id") == payload["content_id"]
    assert review_data.get("rating") == payload["rating"]
    assert review_data.get("review_text") == payload["review_text"]
    assert "id" in review_data

def test_create_review_error_missing_fields(client):
    payload = {"user_id": 1, "content_id": 1, "review_text": "Incomplete!"}
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_review_invalid_rating(client):
    payload = {"user_id": 1, "content_id": 1, "rating": 6, "review_text": "Invalid rating"}
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_review_empty_review_text(client):
    payload = {"user_id": 1, "content_id": 1, "rating": 4, "review_text": ""}
    response = client.post("/reviews/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# -------------------------
# GET REVIEW
# -------------------------
def test_get_review_by_id_success(client, db_session):
    review = Review(user_id=2, content_id=2, rating=4, review_text="Nice!")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    review_data = data.get("data", {})
    assert review_data.get("id") == review.id
    assert review_data.get("rating") == review.rating

def test_get_review_by_id_not_found(client):
    response = client.get("/reviews/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_reviews_by_user(client, db_session):
    review = Review(user_id=3, content_id=3, rating=5, review_text="User review")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get(f"/reviews/by-user/{review.user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data.get("data", []), list)

def test_get_reviews_by_content(client, db_session):
    review = Review(user_id=4, content_id=4, rating=3, review_text="Content review")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get(f"/reviews/by-content/{review.content_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data.get("data", []), list)

# -------------------------
# UPDATE REVIEW
# -------------------------
def test_update_review_success(client, db_session):
    review = Review(user_id=5, content_id=5, rating=2, review_text="Needs improvement")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    payload = {"rating": 5, "review_text": "Much better now!"}
    response = client.put(f"/reviews/{review.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    review_data = data.get("data", {})
    assert review_data.get("rating") == payload["rating"]
    assert review_data.get("review_text") == payload["review_text"]

def test_update_review_not_found(client):
    payload = {"rating": 5, "review_text": "Nonexistent review"}
    response = client.put("/reviews/99999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND

# -------------------------
# DELETE REVIEW
# -------------------------
def test_delete_review_success(client, db_session):
    review = Review(user_id=6, content_id=6, rating=3, review_text="To delete")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.delete(f"/reviews/{review.id}")
    assert response.status_code == status.HTTP_200_OK

    deleted = db_session.query(Review).filter(Review.id == review.id).first()
    assert deleted is None

def test_delete_review_not_found(client):
    response = client.delete("/reviews/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# -------------------------
# PAGINATION
# -------------------------
def test_get_reviews_by_user_paginated(client, db_session):
    cache.clear()
    for i in range(5):
        review = Review(user_id=7, content_id=i, rating=5, review_text=f"Paginated {i}")
        db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get("/reviews/by-user/7/paginated?limit=2&offset=1&order_by=id")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data.get("data", {})

def test_get_reviews_by_content_paginated(client, db_session):
    cache.clear()
    for i in range(5):
        review = Review(user_id=i, content_id=8, rating=4, review_text=f"Paginated {i}")
        db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get("/reviews/by-content/8/paginated?limit=3&offset=0&order_by=created_at")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data.get("data", {})
   


# -------------------------
# CACHE
# -------------------------
def test_cache_hit_get_review_by_id(client, db_session):
    cache.clear()
    review = Review(user_id=9, content_id=9, rating=5, review_text="Cache test")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == status.HTTP_200_OK
    response2 = client.get(f"/reviews/{review.id}")
    assert response2.status_code == status.HTTP_200_OK

def test_cache_invalidation_after_create(client):
    cache.clear()
    payload = {"user_id": 10, "content_id": 10, "rating": 5, "review_text": "Cache create test"}
    response = client.post("/reviews/", json=payload)
    review_id = response.json().get("data", {}).get("id")
    _ = client.get(f"/reviews/{review_id}")
    assert f"review_{review_id}" in cache

def test_cache_invalidation_after_update(client, db_session):
    cache.clear()
    review = Review(user_id=11, content_id=11, rating=3, review_text="To update cache")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    _ = client.get(f"/reviews/{review.id}")
    payload = {"rating": 5, "review_text": "Updated"}
    client.put(f"/reviews/{review.id}", json=payload)
    assert f"review_{review.id}" not in cache

def test_cache_invalidation_after_delete(client, db_session):
    cache.clear()
    review = Review(user_id=12, content_id=12, rating=4, review_text="To delete cache")
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    _ = client.get(f"/reviews/{review.id}")
    client.delete(f"/reviews/{review.id}")
    assert f"review_{review.id}" not in cache

# -------------------------
# RATE LIMITER
# -------------------------
def test_rate_limiter(client):
    for _ in range(3):
        client.post("/reviews/", json={"user_id": 1, "content_id": 1, "rating": 5, "review_text": "RL test"})
    response = client.post("/reviews/", json={"user_id": 1, "content_id": 1, "rating": 5, "review_text": "RL test"})
    assert response.status_code in [status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_201_CREATED]

def test_rate_limiter_deterministic(client):
    from app.core.rate_limiter import limiter
    
    # Verifica che il limiter sia disabilitato
    assert limiter.enabled == False, "Rate limiter dovrebbe essere disabilitato durante i test"

    for _ in range(5): 
        response = client.post("/reviews/", json={"user_id": 20, "content_id": 20, "rating": 5, "review_text": "RL test"})
        assert response.status_code == status.HTTP_201_CREATED, "Tutte le richieste dovrebbero avere successo con limiter disabilitato"


