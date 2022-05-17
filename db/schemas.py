from typing import Optional
from pydantic import BaseModel

class Author(BaseModel):
    id: Optional[int] = None
    full_name: str
    fast_facts: Optional[str] = None
    
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    authors: list[Author]


class BookAdd(BookBase):
    description: str


class BookOut(BaseModel):
    id: int
    title: str
    authors: list[Author]
    description: Optional[str] = None

    class Config:
        orm_mode = True


class BookChange(BookBase):
    description: Optional[None] = str


class BookAuthorSearch(BaseModel):
    search_request: str
   

class BooksList(BaseModel):
    books: list[BookOut]

    class Config:
        orm_mode = True

class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    name: str
    succsess: bool
    message: Optional[str] = None