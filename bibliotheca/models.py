from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(current_path, '..')
sys.path.append(ROOT_PATH)

from bibliotheca import database


authors_book_table = Table("authors_books", database.Base.metadata,
			   Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
			   Column("book_id", Integer, ForeignKey("books.id"), primary_key=True)
			   )


class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)


class Book(database.Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default=None)
    authors = relationship("Author", secondary=authors_book_table, back_populates="books")


class Author(database.Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, nullable=False)
    fast_facts = Column(String, default=None)
    books = relationship("Book", secondary=authors_book_table, back_populates="authors") #, cascade_backrefs=False
