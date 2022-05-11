from typing import Optional
from pydantic import BaseModel

class Author(BaseModel):
    full_name: str
    fast_facts: Optional[str] = None
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    authors: str


class BookAdd(BookBase):
    description: str


class BookOut(BaseModel):
    title: str
    authors: list[Author]

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