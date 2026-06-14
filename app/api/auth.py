from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.db.session import get_db
from app.db.models import User


router = APIRouter(prefix='/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


class UserCreate(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    '''Registers a new user.

    Args:
        payload: The registration payload containing email and password.
        db: The database session.

    Returns:
        A dictionary containing the new user's id and email.

    Raises:
        HTTPException: 400 if the email is already registered.
    '''
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'id': user.id, 'email': user.email}


@router.post('/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict[str, str]:
    '''Authenticates a user and returns a JWT access token.

    Args:
        form_data: The login form containing username and password.
        db: The database session.

    Returns:
        A dictionary containing the access token and token type.

    Raises:
        HTTPException: 401 if the credentials are invalid.
    '''
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token(data={'sub': user.email})
    return {'access_token': token, 'token_type': 'bearer'}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    '''Resolves the current authenticated user from a JWT token.

    Args:
        token: The JWT token extracted from the Authorization header.
        db: The database session.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or the user is not found.
    '''
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    email: str | None = payload.get('sub')
    if email is None:
        raise HTTPException(status_code=401, detail='Invalid token payload')

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')

    return user
