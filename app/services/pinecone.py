from typing import Any

from pinecone import Pinecone

from app.core.config import settings


pc = Pinecone(api_key=settings.pinecone_api_key)
index = pc.Index(settings.pinecone_index_name)


async def upsert_chunks(chunks: list[dict[str, Any]], namespace: str) -> None:
    '''Upserts document chunks into a Pinecone namespace.

    Transforms the chunks into Pinecone records and upserts them using the
    integrated embedding model.

    Args:
        chunks: A list of chunk dictionaries containing id and metadata.
        namespace: The Pinecone namespace to upsert the records into.
    '''
    records = [
        {
            'id': chunk['id'],
            'text': chunk['metadata']['text']
        }
        for chunk in chunks
    ]
    index.upsert_records(namespace=namespace, records=records)


async def retrieve_chunks(question: str, namespaces: list[str]) -> list[str]:
    '''Retrieves relevant text chunks from Pinecone for a given question.

    Searches each namespace and collects the top matching chunks based on
    semantic similarity to the question.

    Args:
        question: The natural language question to search for.
        namespaces: A list of Pinecone namespaces to search across.

    Returns:
        A list of text chunks relevant to the question.
    '''
    all_chunks = []
    for namespace in namespaces:
        results = index.search(
            namespace=namespace,
            query={'inputs': {'text': question}, 'top_k': 5},
            fields=['text']
        )
        all_chunks.extend([hit['fields']['text'] for hit in results.result.hits])
    return all_chunks
