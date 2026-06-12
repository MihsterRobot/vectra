import uuid

from fastapi import UploadFile
from pypdf import PdfReader
import io

from app.services.pinecone import upsert_chunks, index


async def process_document(file: UploadFile, user_id: int) -> str:
    contents = await file.read()
    text = extract_text(file.content_type, contents)
    chunks = chunk_text(text)
    namespace = f'user_{user_id}_doc_{uuid.uuid4().hex}'

    vectors = [
        {
            'id': f'{namespace}_chunk_{i}',
            'values': [],
            'metadata': {'text': chunk}
        }
        for i, chunk in enumerate(chunks)
    ]

    await upsert_chunks(vectors, namespace)
    return namespace


async def delete_document_chunks(namespace: str) -> None:
    index.delete(delete_all=True, namespace=namespace)


def extract_text(content_type: str, contents: bytes) -> str:
    if content_type == 'application/pdf':
        reader = PdfReader(io.BytesIO(contents))
        return '\n'.join(page.extract_text() for page in reader.pages if page.extract_text())
    return contents.decode('utf-8')


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(' '.join(words[start:end]))
        start = end - overlap

    return chunks
