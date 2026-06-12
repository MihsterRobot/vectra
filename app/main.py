from fastapi import FastAPI

from app.api import auth, documents, query
from app.db.session import engine
from app.db.models import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title='Vectra')

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
