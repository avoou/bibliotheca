#created by roman
import json
import json5
import hmac
import hashlib
import base64
from lib2to3.pgen2.token import OP
import typing
from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response
from typing import Dict, Optional
from pydantic import BaseModel

from pydantic import Json

app = FastAPI()


users = {
    "roman@mail.com": {
        "password": "c1e76f31c18b1ee50711f0229a8199e328c39f94def2c24f899b9e2e8a87211b", #12345678
        "name": "roman",
        "sex": "male",
        "session_id": ''
    },

    "alexey@mail.com": {
        "password": "2d1db5cd231fbb80f955bf641fdb6b3de6ce54e571633715c122548fb111b237", #01234567
        "name": "alexey",
        "sex": "male",
        "session": ''
    }
}


SECRET_KEY = '6dfd98adf2601c1f54c794fb8376794805972d71d906a3021525b90e54911a4f'
SALT = 'b8c4703bffd39be0729fe85bf4d798bd4d5809f8121a81f8cfb20a286fec6104'

def sign_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def check_password(username: str, password: str):
    users_hash_password = users[username]['password']
    verifiable_hash_password = hashlib.sha256((SALT + password).encode()).hexdigest()
    print('username', username)
    return users_hash_password == verifiable_hash_password
    

#return correct email of username or None if sign is not True
def get_permission(username_sign):
    username_b64, sign = username_sign.split(".")
    username = base64.b64decode(username_b64).decode()
    if hmac.compare_digest(
        sign_data(username),
        sign):
        return username

@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('./templates/login.html', 'r') as html_file:
        login_page = html_file.read()
    print(username)
    if not username:
        return Response(login_page, media_type='text/html')
    valid_username = get_permission(username)
    if not valid_username:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key="username")
        return response
        
    return Response('Hello, you are logined user', media_type='text/html')
    #return Response(login_page, media_type='text/html')


@app.post('/login')
def process_login_page(data: Json = Body(...)):
    #username: str = Form(...), password : str = Form(...)
    #data = json5.loads(data)
    username = data["username"]
    password = data["password"]
    user = users.get(username)
    if not user:
        #check_password(username, password)
        #return Response('dont auth', media_type='text/html')
        return Response(json.dumps({"sucsess": False,"message": 'dont auth'}), media_type='application/json')
    elif check_password(username, password):
        user: dict = users[username]
        key_for_session = 'username'
        signed_username = base64.b64encode(username.encode()).decode() + '.' + sign_data(username)
        response = Response(json.dumps({"sucsess": True,"message":f'Username: {user["name"]},</br>sex: {user["sex"]}'}), media_type='application/json')
        response.set_cookie(key=key_for_session, value=signed_username)
        return response
    return Response(json.dumps({"sucsess": False,"message": 'dont auth'}), media_type='application/json')
