from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.db.models import User, Document
from app.services.document import process_document, delete_document_chunks


router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/upload', status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ('application/pdf', 'text/plain'):
        raise HTTPException(status_code=400, detail='Only PDF and plain text files are supported')

    namespace = await process_document(file, current_user.id)

    document = Document(
        filename=file.filename,
        content_type=file.content_type,
        pinecone_namespace=namespace,
        owner_id=current_user.id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {'id': document.id, 'filename': document.filename}


@router.get('/')
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    return [{'id': doc.id, 'filename': doc.filename, 'created_at': doc.created_at} for doc in documents]


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if document is None:
        raise HTTPException(status_code=404, detail='Document not found')

    await delete_document_chunks(str(document.pinecone_namespace))
    db.delete(document)
    db.commit()
