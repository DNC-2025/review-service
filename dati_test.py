# test_dati.py

from sqlalchemy.orm import Session
from app.database.config import SessionLocal, Base, engine
from app.models.tables import Review
from faker import Faker
import random

# Inizializza Faker
faker = Faker()

# Crea tutte le tabelle se non esistono
Base.metadata.create_all(bind=engine)

# Crea sessione DB
db: Session = SessionLocal()

try:
    # Popoliamo 10 review "fake"
    for i in range(10):
        review = Review(
            user_id=random.randint(1, 5),        # utenti casuali da 1 a 5
            content_id=random.randint(1, 5),     # contenuti casuali da 1 a 5
            rating=random.randint(1, 5),         # rating da 1 a 5
            review_text=faker.sentence()         # testo casuale
        )
        db.add(review)

    db.commit()
    print("Popolamento completato 10 recensioni aggiunte.")

finally:
    db.close()
