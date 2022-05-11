from fastapi import Depends, FastAPI, Body, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from db import models, schemas, crud
from db.database import SessionLocal, engine
import json

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
    db_book = crud.get_book_by_title(db, title=book.title)
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists")
    return crud.add_book(db=db, book=book)