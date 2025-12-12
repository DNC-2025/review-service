import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.tables import Base
from fastapi.testclient import TestClient
from main import app


@pytest.fixture()
def db_session():
    # Database in memoria
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Creazione tabelle
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):

    # Override della dipendenza del DB usata dagli endpoint
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # IMPORTANTE: qui non usiamo get_test_db ma get_db!
    from app.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)
