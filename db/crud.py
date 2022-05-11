from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    pass

def add_book(db: Session, book: schemas.BookAdd):
    db_book = models.Book(title=book.title, description=book.description)
    db_author = get_author_by_fullname(db=db, full_name=book.authors)
    if not db_author:
        db_author = models.Author(full_name=book.authors, fast_facts=None)

    """for author in book.authors:
        db_author = get_author_by_fullname(db=db, full_name=author)
        if not db_author:
            db_book = models.Book(title=book.title, description=book.description)
        db_book.authors.append(db_author)"""

    db_book.authors.append(db_author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book_by_title(db: Session, title: str):
    return db.query(models.Book).filter(models.Book.title == title).first()

def get_author_by_fullname(db: Session, full_name: str):
    return db.query(models.Author).filter(models.Author.full_name == full_name).first()

def book_change(db: Session, book: schemas.BookChange):
    pass
