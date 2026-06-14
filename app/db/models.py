from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    '''Represents a registered user.

    Attributes:
        id: Primary key.
        email: The user's unique email address.
        hashed_password: The bcrypt-hashed password.
        created_at: Timestamp of when the user was created.
        documents: The user's uploaded documents.
    '''

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship('Document', back_populates='owner', cascade='all, delete-orphan')


class Document(Base):
    '''Represents an uploaded document.

    Attributes:
        id: Primary key.
        filename: The name of the uploaded file.
        content_type: The MIME type of the uploaded file.
        pinecone_namespace: The namespace in Pinecone where the document's chunks are stored.
        created_at: Timestamp of when the document was created.
        owner_id: The ID of the user who owns the document.
    '''

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    pinecone_namespace = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship('User', back_populates='documents')
