from fastapi import Depends, FastAPI, Body, HTTPException, Cookie
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
from db import models, schemas, crud
from db.database import SessionLocal, engine
from typing import Optional
from pydantic import Json
import json
import re
import hmac
import hashlib
import base64
from db.crud import SALT 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add", response_model=schemas.BookOut)
def add_book(book: schemas.BookAdd = Body(...), db: Session = Depends(get_db)):
    db_book = crud.add_book(db=db, book=book)
    if not db_book:
        raise HTTPException(status_code=400, detail="Book already exists")
    return db_book

@app.get("/search/")
def search_book_author(search_request: str, db: Session = Depends(get_db)):
    db_book = crud.get_books_by_title(db=db, title=search_request)
    if db_book:
        book_list = {"books":[schemas.BookOut.from_orm(book).dict() for book in db_book]} 
        return Response(json.dumps(book_list), media_type='application/json')
    authors_list = [author.strip() for author in re.split(r'[;,]',search_request)]
    all_books_by_author = crud.get_authors_by_fullnames(db=db, authors=authors_list)
    if all_books_by_author:
        book_list = {"books":[schemas.BookOut.from_orm(book).dict() for book in all_books_by_author]} 
        return Response(json.dumps(book_list), media_type='application/json')
    raise HTTPException(status_code=400, detail="Nothing was found for your query")
    

@app.put("/edit")
def edit_exists_book(book: schemas.BookChange, db: Session = Depends(get_db)):
    db_book = crud.book_change(book=book, db=db)
    if db_book:
        return db_book
    raise HTTPException(status_code=400, detail="Something wrong!")


@app.delete("/book/{id}")
def delete_book(id: int, db: Session = Depends(get_db)):
    if crud.delete_book_by_id(db=db, id=id):
        return Response(json.dumps({"details": 'This book is deleted!'}), media_type='application/json')
    raise HTTPException(status_code=400, detail="Something wrong!")


SECRET_KEY = '6dfd98adf2601c1f54c794fb8376794805972d71d906a3021525b90e54911a4f'



class CheckSession():
    def __init__(self) -> None:
        self.SESSION_IS_NOT = None
        self.SESSION_IS_INVALID = None
        self.bad_response = None
    
    def check(self, session: Optional[str]) -> None:
        if not session:
            self.SESSION_IS_NOT = True
            return
        if self.get_permission(session):
            self.SESSION_IS_INVALID = False
            self.SESSION_IS_NOT = False
        else:
            self.SESSION_IS_INVALID = True

    def set_bad_response(self, response):
        self.bad_response = response

    #return correct email of username or None if sign is not True
    @staticmethod
    def get_permission(session):
        username_b64, sign = session.split(".")
        username = base64.b64decode(username_b64).decode()
        if hmac.compare_digest(sign_data(username), sign):
            return username



#Creates hmac for username with secret key
def sign_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

#Check the user's password hash in the database with the password from the web form
def check_password(db: Session, users_email: str, password: str):
    user = crud.get_user_by_email(db=db, users_email=users_email)
    users_hash_password = user.hashed_password
    verifiable_hash_password = hashlib.sha256((SALT + password).encode()).hexdigest()
    return users_hash_password == verifiable_hash_password
    



@app.get('/')
def index_page(session: Optional[str] = Cookie(default=None)):
    with open('./templates/main_page_non_login.html', 'r') as html_file:
        non_login_page = html_file.read()

    check_session = CheckSession()
    check_session.check(session)

    if check_session.SESSION_IS_NOT:
        return Response(non_login_page, media_type='text/html')

    if check_session.SESSION_IS_INVALID:
        response = Response(non_login_page, media_type='text/html')
        response.delete_cookie(key="session")
        return response
    with open('./templates/main_page.html', 'r') as html_file:
        main_page = html_file.read()
    return Response(main_page, media_type='text/html')


@app.get('/login')
def login(session: Optional[str] = Cookie(default=None)):
    with open('./templates/login.html', 'r') as html_file:
        login_page = html_file.read()

    check_session = CheckSession()
    check_session.check(session)

    if check_session.SESSION_IS_NOT:
        return Response(login_page, media_type='text/html')

    if check_session.SESSION_IS_INVALID:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key="session")
        return response
    with open('./templates/main_page.html', 'r') as html_file:
        main_page = html_file.read()
    return Response(main_page, media_type='text/html')


@app.post('/login')
def process_login_page(user: schemas.UserIn = Body(...), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, users_email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Dont auth")
    elif check_password(db=db, users_email=user.email, password=user.password):
        key_for_cookie = 'session'
        signed_username = base64.b64encode(db_user.email.encode()).decode() + '.' + sign_data(db_user.email)
        response = Response(json.dumps({"username": f'{db_user.name}'}), media_type='application/json')
        response.set_cookie(key=key_for_cookie, value=signed_username)
        return response
    raise HTTPException(status_code=400, detail="Dont auth")


@app.get('/logout')
def logout():
    try:
        response = Response(json.dumps({"sucsess": True}), media_type='text/html')
        response.delete_cookie(key="session")
    except Exception:
        return Response(json.dumps({"sucsess": False}), media_type='text/html')
    return response


@app.get('/registration')
def get_registration(session: Optional[str] = Cookie(default=None)):
    check_session = CheckSession()
    check_session.check(session)
    if check_session.SESSION_IS_NOT:
        with open('./templates/registration_page.html', 'r') as regiistation_html:
            registration_page = regiistation_html.read()
        return Response(registration_page, media_type='text/html')
    if check_session.SESSION_IS_INVALID:
        response = Response(registration_page, media_type='text/html')
        response.delete_cookie(key="session")
        return response
    return RedirectResponse(url='/', status_code=303)



@app.post('/registration')
def post_registration(user: schemas.UserIn = Body(...), db: Session = Depends(get_db)): 
    db_user = crud.get_user_by_email(db=db, users_email=user.email)
    if not db_user:
        db_user = crud.create_user(db=db, user=user)
        key_for_cookie = 'session'
        signed_username = base64.b64encode(user.email.encode()).decode() + '.' + sign_data(user.email)
        response = Response(json.dumps({"name": f'{user.name}'}), media_type='application/json')
        response.set_cookie(key=key_for_cookie, value=signed_username)
        return response
    else:
        raise HTTPException(status_code=400, detail="The user already exists")