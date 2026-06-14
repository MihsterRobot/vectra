from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict, cast

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


class TokenPayload(TypedDict):
    sub: str
    exp: int


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__truncate_error=False)


def hash_password(password: str) -> str:
    '''Hashes a plaintext password using bcrypt.

    Truncates the password to 72 bytes before hashing, as bcrypt does not
    support passwords longer than 72 bytes.

    Args:
        password: The plaintext password to hash.

    Returns:
        The bcrypt-hashed password string.
    '''
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Verifies a plaintext password against a hashed password.

    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The bcrypt-hashed password to verify against.

    Returns:
        `True` if the password matches, `False` otherwise.
    '''
    return pwd_context.verify(plain_password[:72], hashed_password)


def create_access_token(data: dict[str, Any]) -> str:
    '''Creates a signed JWT access token.

    Args:
        data: A dictionary of claims to encode in the token.

    Returns:
        A signed JWT token string.
    '''
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload | None:
    '''Decodes and validates a JWT access token.

    Args:
        token: The JWT token string to decode.

    Returns:
        The decoded token payload as a dictionary, or `None` if the token is
        invalid or expired.
    '''
    try:
        return cast(TokenPayload, jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm]))
    except JWTError:
        return None
