from fastapi import Depends, FastAPI
from fastapi.responses import Response
from sqlalchemy.orm import Session
from db import models, schemas, crud
from db.database import SessionLocal, engine

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
def add_book(book: schemas.BookAdd, db: Session = Depends(get_db)):
    return crud.add_book(db=db, book=book)