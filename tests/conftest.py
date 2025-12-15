import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.tables import Base
from fastapi.testclient import TestClient
from main import app
from app.database import get_db

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
    # Override la dipendenza get_db con la sessione di test
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
