from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base

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
    description = Column(String)
    authors = relationship("Author", secodary=authors_book_table, back_populates="books")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    fast_facts = Column(String)
    books = relationship("Book", secondary=authors_book_table, back_populates="authors")


authors_book_table = Table("authors_books", Base.metadata,
			   Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
			   Column("book_id", Integer, ForeignKey("books.id"), primary_key=True)
			   )

