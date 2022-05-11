from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    pass

def add_book(db: Session, book: schemas.BookAdd):
    db_book = models.Book(title=book.title, description=book.description)
    db_author = models.Author(full_name=book.authors)
    db_book.authors.append(db_author)
    db.add(db_book)
    db.commit()
    db.refresh()
    return db_book

def search_book(db: Session, book: schemas.BookAuthorSearch):
    pass

def search_author(db: Session, book: schemas.BookAuthorSearch):
    pass

def book_change(db: Session, book: schemas.BookChange):
    pass
