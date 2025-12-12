

from sqlalchemy.orm import Session

def get_db():
    """
    Dipendenza originale del DB usata dagli endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
