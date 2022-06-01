from statistics import mode
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, delete
from database import engine
import hashlib
import models
import schemas
import configparser
import os

config = configparser.ConfigParser()
current_path = os.path.dirname(os.path.abspath(__file__))
path_to_config = os.path.join(current_path, 'settings.ini')
config.read(path_to_config)

#SALT = 'b8c4703bffd39be0729fe85bf4d798bd4d5809f8121a81f8cfb20a286fec6104'
SALT = config["Bibliotheca"]["salt"]

def get_user_by_email(db: Session, email: str):
    pass

def get_all_authors_books(db: Session, list_of_authors_fullnames: list):
    expressions = [models.Author.full_name==full_name for full_name in list_of_authors_fullnames]
    queries_for_exists = [db.query(models.Author)
                        .join(models.authors_book_table)
                        .filter(expression, models.Book.id==models.authors_book_table.c.book_id).exists() 
                        for expression in expressions]
    last_expression = db.query(models.Author) \
                        .join(models.authors_book_table) \
                        .filter(and_(~models.Author.full_name.in_(list_of_authors_fullnames), models.Book.id==models.authors_book_table.c.book_id))

    all_books_by_authors = db.query(models.Book).filter(*queries_for_exists, ~last_expression.exists()).all()
    return all_books_by_authors

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
    all_books_by_authors = get_all_authors_books(db=db, list_of_authors_fullnames=authors)
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


def book_change(db: Session, book: schemas.BookChange):
    #id=5 title='book2' authors=[Author(id=None, full_name='author1', fast_facts=None), Author(id=None, full_name='author2', fast_facts=None)]
    db_book = db.query(models.Book).get(book.id)
    db_authors_book = [author.full_name for author in db_book.authors]
    authors = [author.full_name for author in book.authors]
    if db_book.title == book.title and set(db_authors_book) == set(authors):
        db_book.description = book.description
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    all_auth_books = get_all_authors_books(db=db, list_of_authors_fullnames=authors)
    if all_auth_books:
        for auth_book in all_auth_books:
            if book.title == auth_book.title:
                return False
    db_book = db.query(models.Book).filter(models.Book.id == book.id).first()
    db_book.authors = []
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


def delete_book_by_id(db: Session, id: int):
    db_book = db.query(models.Book).get(id)
    if db_book:
        db_book.authors = []
        db.commit()
        engine.execute(delete(models.Book).where(models.Book.id==id))
        return True
    return False


def get_user_by_email(db: Session, users_email: str):
    return db.query(models.User).filter(models.User.email==users_email).first()

def create_user(db: Session, user: schemas.UserIn):
    hashed_password = hashlib.sha256((SALT + user.password).encode()).hexdigest()
    db_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user