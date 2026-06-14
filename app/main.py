from fastapi import FastAPI

from app.api import auth, documents, query


app = FastAPI(title='Vectra')

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
