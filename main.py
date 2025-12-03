1                       # qui faccio creare la tabella 
from fastapi import FastAPI
from app.database.config import Base, engine
#from app.models.tables import Review 
from app.routers.review_router import router as review_router
from exceptions.handlers import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    HTTPException,
    SQLAlchemyError
)

print("Table 'review' creata correttamente")

app = FastAPI(title="Review-Service" ,
              description="Servizio per la gestione delle recensioni",
              version="1.0.0")

# crea tutte le tabelle dei modelli importati
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Benvenuto al Review-Service API. Usa /docs per vedere gli endpoint disponibili."}

# il router per le recensioni
app.include_router(review_router)   # ** Senza questo comando, gli endpoint non funzionano.**  Diciamo come il base metadata create all.


# E qui  ci sono li   global handlers 
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)