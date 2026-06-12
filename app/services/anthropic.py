import anthropic

from app.core.config import settings


client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def generate_response(question: str, chunks: list[str]) -> str:
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

    return message.content[0].text
