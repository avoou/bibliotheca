from fastapi import Depends, FastAPI, Body, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from db import models, schemas, crud
from db.database import SessionLocal, engine
import json
import re

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_main_page():
    with open("./templates/main_page.html", "r") as html_file:
        main_page = html_file.read()
    return Response(main_page, media_type='text/html')


@app.post("/add", response_model=schemas.BookOut)
def add_book(book: schemas.BookAdd = Body(...), db: Session = Depends(get_db)):
    db_book = crud.add_book(db=db, book=book)
    if not db_book:
        raise HTTPException(status_code=400, detail="Book already exists")
    return db_book

@app.get("/search/")
def search_book_author(search_request: str, db: Session = Depends(get_db)):
    print(search_request)
    db_book = crud.get_books_by_title(db=db, title=search_request)
    if db_book:
        print()
        #book_list = {"books":[schemas.BookOut.from_orm(db_book).dict()]}
        book_list = {"books":[schemas.BookOut.from_orm(book).dict() for book in db_book]} 
        return Response(json.dumps(book_list), media_type='application/json')
    #all_books_by_author = crud.get_author_by_fullname(db=db, full_name=search_request)
    #if all_books_by_author:
        #return Response(json.dumps(schemas.BooksList.from_orm(all_books_by_author).dict()), media_type='application/json')
    authors_list = [author.strip() for author in re.split(r'[;,]',search_request)]
    print()
    all_books_by_author = crud.get_authors_by_fullnames(db=db, authors=authors_list)
    if all_books_by_author:
        book_list = {"books":[schemas.BookOut.from_orm(book).dict() for book in all_books_by_author]} 
        return Response(json.dumps(book_list), media_type='application/json')
    raise HTTPException(status_code=400, detail="Nothing was found for your query")
    
