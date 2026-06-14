from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    '''Application settings loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection string for the main database.
        test_database_url: PostgreSQL connection string for the test database.
        pinecone_api_key: API key for Pinecone vector database.
        pinecone_index_name: Name of the Pinecone index to use.
        anthropic_api_key: API key for the Anthropic API.
        secret_key: Secret key used for signing JWT tokens.
        algorithm: Algorithm used for JWT encoding.
        access_token_expire_minutes: JWT token expiry duration in minutes.
    '''

    model_config = ConfigDict(env_file='.env')  # type: ignore

    database_url: str
    test_database_url: str = ''
    pinecone_api_key: str
    pinecone_index_name: str
    anthropic_api_key: str
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30


settings = Settings()  # type: ignore
