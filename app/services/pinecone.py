from pinecone import Pinecone

from app.core.config import settings


pc = Pinecone(api_key=settings.pinecone_api_key)
index = pc.Index(settings.pinecone_index_name)


async def upsert_chunks(chunks: list[dict], namespace: str) -> None:
    index.upsert(vectors=chunks, namespace=namespace)


async def retrieve_chunks(question: str, user_id: int, document_id: int | None = None) -> list[str]:
    namespace = f'user_{user_id}' if document_id is None else f'user_{user_id}_doc_{document_id}'

    results = index.query(
        namespace=namespace,
        top_k=5,
        include_metadata=True,
        inputs={'text': question}
    )

    return [match['metadata']['text'] for match in results.get('matches', []) if 'text' in match.get('metadata', {})]
