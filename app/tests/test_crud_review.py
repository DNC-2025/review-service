from app.database.config import SessionLocal
from app.crud.crud_review import (
    create_review,
    get_review_by_id,
    get_reviews_by_user,
    get_reviews_by_content,
    update_review,
    delete_review
)

def run_tests():
    print("INIZIO TEST CRUD REVIEW")
    
    db = SessionLocal()

    try:
        # CREATE
        print("1) TEST CREATE REVIEW")
        review = create_review(
            db=db,
            user_id=1,
            content_id=10,
            rating=5,
            review_text="Recensione iniziale"
        )
        print("   → CREATED:", review)

        # READ by ID
        print("\n2) TEST GET REVIEW BY ID")
        r = get_review_by_id(db, review.id)
        print("   → FETCHED:", r)

        # READ by USER
        print("\n3) TEST GET REVIEWS BY USER")
        r = get_reviews_by_user(db, review.user_id)
        print("   → USER REVIEWS:", r)

        # READ by CONTENT
        print("\n4) TEST GET REVIEWS BY CONTENT")
        r = get_reviews_by_content(db, review.content_id)
        print("   → CONTENT REVIEWS:", r)

        # UPDATE
        print("\n5) TEST UPDATE REVIEW")
        updated = update_review(
            db,
            review_id=review.id,
            rating=4,
            review_text="Recensione aggiornata"
        )
        print("   → UPDATED:", updated)

        # DELETE
        print("\n6) TEST DELETE REVIEW")
        deleted = delete_review(db, review.id)
        print("   → DELETED:", deleted)

        # VERIFY DELETE
        print("\n7) TEST VERIFY DELETE")
        check = get_review_by_id(db, review.id)
        print("   → AFTER DELETE FETCHED:", check)

        print("\n--- TUTTI I TEST CRUD ESEGUITI ---\n")

    finally:
        db.close()
