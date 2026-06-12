from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models import User
from app.services.pinecone import retrieve_chunks
from app.services.anthropic import generate_response


router = APIRouter(prefix='/query', tags=['query'])


class QueryRequest(BaseModel):
    question: str
    document_id: int | None = None


@router.post('/')
async def query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail='Question cannot be empty')

    chunks = await retrieve_chunks(
        question=payload.question,
        user_id=current_user.id,
        document_id=payload.document_id
    )

    if not chunks:
        raise HTTPException(status_code=404, detail='No relevant content found')

    answer = await generate_response(question=payload.question, chunks=chunks)
    return {'answer': answer}
