1                       # qui faccio creare la tabella 
from fastapi import FastAPI , HTTPException                 
from app.database.config import Base, engine
#from app.models.tables import Review 
from app.routers.review_router import router as review_router
from exceptions.handlers import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler
)
from sqlalchemy.exc import SQLAlchemyError    # <-- IMPORT CORRETTO (prima era sbagliato)
from fastapi.middleware.cors import CORSMiddleware
from app.core.rate_limiter import init_rate_limiter
from app.core.logger import logger 


logger.info("Avvio del Review-Service API")
app = FastAPI(title="Review-Service" ,
              description="Servizio per la gestione delle recensioni",
              version="1.0.0")

# cors middleware (il localhost300 e il url del forntend**)  
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Origini consentite
    allow_credentials=True,         # Permette cookie / autenticazione
    allow_methods=["GET", "POST", "PUT", "DELETE"],   # Metodi ammessi
    allow_headers=["*"]            # Header ammessi / "*" vuole dire (all) 
)

#-------- Rate limiter -----------
init_rate_limiter(app)

# crea tutte le tabelle dei modelli importati
Base.metadata.create_all(bind=engine)
logger.info("creazione delle tabelle nel db , (workbench)")
#print("Table 'review' creata correttamente") se si usa loguru allora queste print di conferma non servono piu. 
logger.success("Tabelle create correttamente")

# E qui  ci sono li   global handlers 
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Benvenuto al Review-Service API. Usa /docs per vedere gli endpoint disponibili."}

# il router per le recensioni
app.include_router(review_router )   # ** Senza questo comando, gli endpoint non funzionano.**  Diciamo come il base metadata create all.


 