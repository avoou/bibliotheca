#created by roman
import json
import  pprint
import hmac
import hashlib
import base64
import typing
import datetime
import pytz
from fastapi import FastAPI, Cookie, Body
from fastapi.responses import Response, RedirectResponse
from typing import Dict, Optional
from fastapi.staticfiles import StaticFiles


from pydantic import Json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


users = {
    "roman@mail.com": {
        "password": "c1e76f31c18b1ee50711f0229a8199e328c39f94def2c24f899b9e2e8a87211b", #12345678
        "name": "roman",
        "sex": "male",
        "about": 'I am Roman)',
    }
}

anecdotes = {
    "today" : """Мужику звонят из милиции и говорят:</br>
                — У нас для вас три новости — плохая, хорошая и охуенная.</br>
                — Гм, ну давайте с плохой.</br>
                — Ваша жена погибла — утонула в реке.</br>
                — А хорошая?</br>
                — Когда мы ее достали — ее тело было облеплено раками и мы заебато попили пиво всем отделом.</br>
                — Гм, а охуенная тогда какая?— Мы ее снова забросили в реку и приглашаем вас завтра на пиво!)""",
    "all" : """Один дирижер, по национальности грузин, заболел, и в оркестр на замену прислали другого - русского дирижера.</br>
                Придя на первую репетицию, он открывает партитуру и видит надпись на первой странице:</br>
                Тональность - сол! Он взял да и дописал для грамотности в конце слова сол мягкий знак.</br>
                Прошло время, грузинский дирижер выздоровел. Появившись на репетиции и заглянув в партитуру, с изумлением воскликнул:</br>
                - Ничэго нэ понимаю! Уходил - был сол, пришел - стал сол-бемол!"""
}

SECRET_KEY = '6dfd98adf2601c1f54c794fb8376794805972d71d906a3021525b90e54911a4f'
SALT = 'b8c4703bffd39be0729fe85bf4d798bd4d5809f8121a81f8cfb20a286fec6104'


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
def check_password(username: str, password: str):
    users_hash_password = users[username]['password']
    verifiable_hash_password = hashlib.sha256((SALT + password).encode()).hexdigest()
    return users_hash_password == verifiable_hash_password
    



@app.get('/')
def index_page(session: Optional[str] = Cookie(default=None)):
    with open('./templates/login.html', 'r') as html_file:
        login_page = html_file.read()

    check_session = CheckSession()
    check_session.check(session)
    print('session', session)

    if check_session.SESSION_IS_NOT:
        return Response(login_page, media_type='text/html')

    if check_session.SESSION_IS_INVALID:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key="session")
        return response
    with open('./templates/index.html', 'r') as html_file:
        index_page = html_file.read()
    return Response(index_page, media_type='text/html')


@app.get('/anecdote/')
def get_anecdote(what_anecdote: Optional[str] = None, tz: Optional[str] = None, session: Optional[str] = Cookie(default=None)):
    user_timezone = tz
    print(user_timezone)
    check_session = CheckSession()
    check_session.check(session)
    check_session.set_bad_response(Response(json.dumps({"sucsess": False,"message": 'Ooops, whats wrong('}), media_type='application/json'))

    if check_session.SESSION_IS_NOT:
        return check_session.bad_response

    if not check_session.SESSION_IS_INVALID:
        if what_anecdote == "today":
            user_local_datetime = datetime.datetime.now(pytz.timezone(user_timezone))
            user_local_time = datetime.datetime.strftime(user_local_datetime, '%H:%M:%S')
            abs_time_delta = str(abs(datetime.datetime.strptime('23:59:59', '%H:%M:%S') - datetime.datetime.strptime(user_local_time, '%H:%M:%S')))

            return Response(json.dumps({"sucsess": False,"message": 'AAAAAAAAAAAAAAAAAA'}), media_type='application/json')
            #проверить в базе запись с названием today, если нет сделать запись и установить время жизни для записи: timedelta(00:00:00, usertime)
            #если есть просто отдать
        elif what_anecdote == "all":
            pass
            #отдать все залайканные анекдоты
        

    response = check_session.bad_response
    response.delete_cookie(key="session")
    return response


@app.post('/login')
def process_login_page(data: Json = Body(...)):
    username = data["username"]
    password = data["password"]
    user = users.get(username)
    if not user:
        return Response(json.dumps({"sucsess": False,"message": 'dont auth'}), media_type='application/json')
    elif check_password(username, password):
        user: dict = users[username]
        key_for_cookie = 'session'
        signed_username = base64.b64encode(username.encode()).decode() + '.' + sign_data(username)
        response = Response(json.dumps({"sucsess": True, "message": None, "username": f'{user["name"]}'}), media_type='application/json')
        response.set_cookie(key=key_for_cookie, value=signed_username)
        return response
    return Response(json.dumps({"sucsess": False,"message": 'dont auth'}), media_type='application/json')


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
        response = RedirectResponse(url='/', status_code=303)
        response.delete_cookie(key="session")
        return response
    return RedirectResponse(url='/', status_code=303)



@app.post('/registration')
def post_registration(data: Json = Body(...)):
    username = data["username"]
    name = data["name"]
    password = data["password"]
    sex = data["sex"]
    about = data["about"]
    user = users.get(username)
    if not user:
        users[username] = {
            "name": name,
            "password": hashlib.sha256((SALT + password).encode()).hexdigest(),
            "sex": sex,
            "about": about
            }
        pprint.pprint(users)
        key_for_cookie = 'session'
        signed_username = base64.b64encode(username.encode()).decode() + '.' + sign_data(username)
        response = Response(json.dumps({"sucsess": True, "message": None, "name": f'{name}'}), media_type='application/json')
        response.set_cookie(key=key_for_cookie, value=signed_username)
        return response
    else:
        return Response(json.dumps({"sucsess": False,"message": 'The user already exists'}), media_type='application/json')
    