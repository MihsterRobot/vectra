import anthropic
from anthropic.types import TextBlock

from app.core.config import settings


client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def generate_response(question: str, chunks: list[str]) -> str:
    '''Generates a response to a question using retrieved document chunks as context.

    Passes the question and relevant chunks to Claude, which uses them to
    produce a grounded answer.

    Args:
        question: The natural language question to answer.
        chunks: A list of relevant text chunks retrieved from Pinecone.

    Returns:
        The generated response as a string.
    '''
    context = '\n\n'.join(chunks)

    message = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1024,
        messages=[
            {
                'role': 'user',
                'content': f'Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion:\n{question}'
            }
        ]
    )

    text_block = next(block for block in message.content if isinstance(block, TextBlock))
    return text_block.text
