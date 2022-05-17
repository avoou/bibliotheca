from email.policy import default
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base


authors_book_table = Table("authors_books", Base.metadata,
			   Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
			   Column("book_id", Integer, ForeignKey("books.id"), primary_key=True)
			   )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default=None)
    authors = relationship("Author", secondary=authors_book_table, back_populates="books")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, nullable=False)
    fast_facts = Column(String, default=None)
    books = relationship("Book", secondary=authors_book_table, back_populates="authors")