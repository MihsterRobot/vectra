from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ''
    pinecone_api_key: str
    pinecone_index_name: str
    anthropic_api_key: str
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    class Config:
        env_file = '.env'


settings = Settings()  # type: ignore
