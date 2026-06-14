import io
import uuid

from fastapi import UploadFile, HTTPException
from pypdf import PdfReader

from app.services.pinecone import upsert_chunks, index


async def process_document(file: UploadFile, user_id: int) -> str:
    '''Processes an uploaded document and stores its chunks in Pinecone.

    Reads the file contents, extracts text, splits it into overlapping chunks,
    and upserts them into a unique Pinecone namespace for the user and document.

    Args:
        file: The uploaded file to process.
        user_id: The ID of the user uploading the document.

    Returns:
        The Pinecone namespace where the document chunks are stored.

    Raises:
        HTTPException: 400 if the file content type cannot be determined.
    '''
    contents = await file.read()

    if file.content_type is None:
        raise HTTPException(status_code=400, detail='Could not determine file content type')

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
    '''Deletes all chunks associated with a document namespace from Pinecone.

    Args:
        namespace: The Pinecone namespace whose records should be deleted.
    '''
    index.delete(delete_all=True, namespace=namespace)


def extract_text(content_type: str, contents: bytes) -> str:
    '''Extracts plain text from a file based on its content type.

    Supports PDF and plain text files. PDFs are parsed page by page using
    pypdf, with empty pages skipped.

    Args:
        content_type: The MIME type of the file.
        contents: The raw file bytes.

    Returns:
        The extracted text as a string.
    '''
    if content_type == 'application/pdf':
        reader = PdfReader(io.BytesIO(contents))
        return '\n'.join(page.extract_text() for page in reader.pages if page.extract_text())
    return contents.decode('utf-8')


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    '''Splits text into overlapping chunks of a fixed word count.

    Args:
        text: The text to split into chunks.
        chunk_size: The number of words per chunk.
        overlap: The number of words to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    '''
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(' '.join(words[start:end]))
        start = end - overlap

    return chunks
