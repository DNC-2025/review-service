1                       # qui faccio creare la tabella 
from fastapi import FastAPI
from app.database.config import Base, engine
from app.models.tables import Review 
# crea tutte le tabelle dei modelli importati
Base.metadata.create_all(bind=engine)

print("Table 'review' creata correttamente")

app = FastAPI(title="Review-Service")
