

from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy import or_, and_
from sqlalchemy import exists

def get_user_by_email(db: Session, email: str):
    pass


def add_book(db: Session, book: schemas.BookAdd):
    authors = [author.full_name for author in book.authors]
    expressions = [models.Author.full_name==author for author in authors]
    db_authors = db.query(models.Author).filter(or_(*expressions)).all()

    if len(authors) != len(db_authors):
        print("Какой то из авторов не найден")
        db_book = models.Book(title=book.title, description=book.description)
        for author in authors:
            db_author = get_author_by_fullname(db=db, full_name=author)
            if not db_author:
                db_author = models.Author(full_name=author)
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
            print('This book already exists', db_book.title)
            return False

    db_book = models.Book(title=book.title, description=book.description)
    db_book.authors.extend(db_authors)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    print('new book added')
    return db_book


def get_books_by_title(db: Session, title: str):
    return db.query(models.Book).filter(models.Book.title == title).all()

def get_author_by_fullname(db: Session, full_name: str):
    return db.query(models.Author).filter(models.Author.full_name == full_name).first()

def get_authors_by_fullnames(db: Session, authors: list[str]):
    print(authors)
    expressions = [models.Author.full_name==author for author in authors]
    #db_authors = db.query(models.Author).filter(or_(*expressions)).all()
    
    queries_for_exists = [db.query(models.Author)
                        .join(models.authors_book_table)
                        .filter(expression, models.Book.id==models.authors_book_table.c.book_id).exists() 
                        for expression in expressions]
    last_expression = db.query(models.Author) \
                        .join(models.authors_book_table) \
                        .filter(and_(~models.Author.full_name.in_(authors), models.Book.id==models.authors_book_table.c.book_id))
    all_books_by_authors = db.query(models.Book).filter(*queries_for_exists, ~last_expression.exists()).all()
    print(len(all_books_by_authors))

    return all_books_by_authors

def book_change(db: Session, book: schemas.BookChange):
    pass

