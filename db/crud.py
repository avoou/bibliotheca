

import email
from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy import or_, and_
import hashlib

SALT = 'b8c4703bffd39be0729fe85bf4d798bd4d5809f8121a81f8cfb20a286fec6104'

def get_user_by_email(db: Session, email: str):
    pass


def add_book(db: Session, book: schemas.BookAdd):
    authors = [author.full_name for author in book.authors]
    expressions = [models.Author.full_name==author for author in authors]
    db_authors = db.query(models.Author).filter(or_(*expressions)).all()

    if len(authors) != len(db_authors):
        db_book = models.Book(title=book.title, description=book.description)
        for author in authors:
            db_author = get_author_by_fullname(db=db, full_name=author)
            if not db_author:
                db_author = models.Author(full_name=author)
                db.add(db_author)
            db_book.authors.append(db_author)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    queries_for_exists = [db.query(models.Author)
                        .join(models.authors_book_table)
                        .filter(expression, models.Book.id==models.authors_book_table.c.book_id).exists() 
                        for expression in expressions]
    last_expression = db.query(models.Author) \
                        .join(models.authors_book_table) \
                        .filter(and_(~models.Author.full_name.in_(authors), models.Book.id==models.authors_book_table.c.book_id))

    all_books_by_authors = db.query(models.Book).filter(*queries_for_exists, ~last_expression.exists()).all()
    for db_book in all_books_by_authors:
        if db_book.title == book.title:
            return False

    db_book = models.Book(title=book.title, description=book.description)
    db_book.authors.extend(db_authors)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books_by_title(db: Session, title: str):
    return db.query(models.Book).filter(models.Book.title == title).all()

def get_author_by_fullname(db: Session, full_name: str):
    return db.query(models.Author).filter(models.Author.full_name == full_name).first()

def get_authors_by_fullnames(db: Session, authors: list[str]):
    expressions = [models.Author.full_name==author for author in authors]
    
    queries_for_exists = [db.query(models.Author)
                        .join(models.authors_book_table)
                        .filter(expression, models.Book.id==models.authors_book_table.c.book_id).exists() 
                        for expression in expressions]
    last_expression = db.query(models.Author) \
                        .join(models.authors_book_table) \
                        .filter(and_(~models.Author.full_name.in_(authors), models.Book.id==models.authors_book_table.c.book_id))
    all_books_by_authors = db.query(models.Book).filter(*queries_for_exists, ~last_expression.exists()).all()

    return all_books_by_authors

def book_change(db: Session, book: schemas.BookChange):
    #id=5 title='book2' authors=[Author(id=None, full_name='author1', fast_facts=None), Author(id=None, full_name='author2', fast_facts=None)]
    authors = [author.full_name for author in book.authors]
    db_book = db.query(models.Book).filter(models.Book.id == book.id).first()
    for author in authors:
        db_author = get_author_by_fullname(db=db, full_name=author)
        if not db_author:
            db_author = models.Author(full_name=author)
            db.add(db_author)
        db_book.authors.append(db_author)
    db_book.title = book.title
    db_book.description = book.description
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_user_by_email(db: Session, users_email: str):
    return db.query(models.User).filter(models.User.email==users_email).first()

def create_user(db: Session, user: schemas.UserIn):
    hashed_password = hashlib.sha256((SALT + user.password).encode()).hexdigest()
    db_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user