from typing import Optional
from pydantic import BaseModel

class BookBase(BaseModel):
    title: Optional[None] = str
    authors: Optional[None] = str


class BookAdd(BookBase):
    description: str


class BookOut(BookBase):
    description: str

    class Config:
        orm_mode = True


class BookChange(BookBase):
    description: Optional[None] = str


class BookAuthorSearch(BaseModel):
    search_request: str
   

class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    name: str
    succsess: bool
    message: Optional[str] = None