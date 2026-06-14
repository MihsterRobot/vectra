from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models import User, Document
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
) -> dict[str, str]:
    '''Queries the user's documents using natural language.

    Retrieves relevant chunks from Pinecone based on the question and passes
    them to Claude to generate a response. If a document_id is provided, only
    that document is queried. Otherwise, all of the user's documents are searched.

    Args:
        payload: The query payload containing the question and optional document_id.
        db: The database session.
        current_user: The authenticated user.

    Returns:
        A dictionary containing the generated answer.

    Raises:
        HTTPException: 400 if the question is empty.
        HTTPException: 404 if the document is not found, or no relevant content is returned.
    '''
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail='Question cannot be empty')

    if payload.document_id is not None:
        document = db.query(Document).filter(
            Document.id == payload.document_id,
            Document.owner_id == current_user.id
        ).first()
        if document is None:
            raise HTTPException(status_code=404, detail='Document not found')
        namespaces = [str(document.pinecone_namespace)]
    else:
        documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
        namespaces = [str(doc.pinecone_namespace) for doc in documents]

    if not namespaces:
        raise HTTPException(status_code=404, detail='No relevant content found')

    chunks = await retrieve_chunks(question=payload.question, namespaces=namespaces)

    if not chunks:
        raise HTTPException(status_code=404, detail='No relevant content found')

    answer = await generate_response(question=payload.question, chunks=chunks)
    return {'answer': answer}
