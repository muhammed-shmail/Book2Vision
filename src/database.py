from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = "sqlite:///./library.db"

# Engine
engine = create_engine(DATABASE_URL, echo=False)

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    full_text: str = Field() # Defer loading large text
    
    # Relationships
    analysis: Optional["Analysis"] = Relationship(back_populates="book")
    images: List["Image"] = Relationship(back_populates="book")

class Analysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    summary: str
    entities_json: str # JSON string
    scenes_json: str # JSON string
    keywords_json: str # JSON string
    podcast_json: Optional[str] = None # JSON string for podcast playlist
    
    book: Optional[Book] = Relationship(back_populates="analysis")

class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    type: str # "cover", "scene", "entity"
    path: str
    prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    book: Optional[Book] = Relationship(back_populates="images")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
