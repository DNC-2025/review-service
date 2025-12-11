import pytest
from fastapi.testclient import TestClient
from main import app

# ============================
# Fixture: TestClient senza DB
# ============================
@pytest.fixture(scope="function")
def client():
    """
    TestClient per simulare richieste HTTP all'app FastAPI.
    Nessuna connessione a DB reale.
    """
    with TestClient(app) as c:
        yield c

# ============================
# Fixture: utente fittizio
# ============================
@pytest.fixture(scope="function")
def create_user_for_test():
    """
    Ritorna un dizionario che rappresenta un utente di test.
    """
    return {"id": 1, "username": "testuser", "email": "test@example.com"}

# ============================
# Fixture: contenuto fittizio
# ============================
@pytest.fixture(scope="function")
def create_content_for_test():
    """
    Ritorna un dizionario che rappresenta un contenuto di test.
    """
    return {"id": 1, "title": "Test Content", "description": "Some description"}

# ============================
# Fixture: review fittizia
# ============================
@pytest.fixture(scope="function")
def create_review_for_test(create_user_for_test, create_content_for_test):
    """
    Ritorna un dizionario che rappresenta una review di test.
    """
    return {
        "id": 1,
        "user_id": create_user_for_test["id"],
        "content_id": create_content_for_test["id"],
        "rating": 5,
        "review_text": "Great content!"
    }



