from pinecone import Pinecone

from app.core.config import settings


pc = Pinecone(api_key=settings.pinecone_api_key)
index = pc.Index(settings.pinecone_index_name)


async def upsert_chunks(chunks: list[dict], namespace: str) -> None:
    records = [
        {
            'id': chunk['id'],
            'text': chunk['metadata']['text']
        }
        for chunk in chunks
    ]
    index.upsert_records(namespace=namespace, records=records)


async def retrieve_chunks(question: str, namespaces: list[str]) -> list[str]:
    all_chunks = []
    for namespace in namespaces:
        results = index.search(
            namespace=namespace,
            query={'inputs': {'text': question}, 'top_k': 5},
            fields=['text']
        )
        all_chunks.extend([hit['fields']['text'] for hit in results.result.hits])
    return all_chunks
