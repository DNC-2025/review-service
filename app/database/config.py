from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:2025mysql%40@localhost:3306/review-service"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():            # Questa funzione serve a creare una sessione temporanea con il database per ogni richiesta HTTP,
    db = SessionLocal()  # fornendola agli endpoint in modo sicuro e chiudendo automaticamente la connessione dopo l’uso.
    try:
        yield db
    finally:
        db.close()
