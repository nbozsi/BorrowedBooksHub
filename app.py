from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.staticfiles import StaticFiles

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

import models
from database import SessionLocal, engine
import json


with open("./lang/hu.json", "r", encoding="utf-8") as f:
    lang = json.load(f)


models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).order_by(models.Book.id.desc()).all()
    return templates.TemplateResponse("base.html", {"request": request, "lang": lang, "book_list": books})


@app.get("/new")
def new(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("new.html", {"request": request, "lang": lang})


@app.post("/add")
def add(request: Request, title: str = Form(None), author: str = Form("Ismeretlen szerző"), db: Session = Depends(get_db)):
    if not title:
        url = app.url_path_for("new")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    new_book = models.Book(title=title, author=author)
    db.add(new_book)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/change/{book_id}")
def change(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    return templates.TemplateResponse("change.html", {"request": request, "lang": lang, "book": book})


@app.post("/update/{book_id}")
def update(request: Request, book_id: int, author: str = Form(...), title: str = Form(...), db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    book.title = title
    book.author = author
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{book_id}")
def delete(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    db.delete(book)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.post('/startsearch')
def startsearch(request: Request, title: str = Form(""), author: str = Form(""), db: Session = Depends(get_db)):

    url = app.url_path_for("search")+f"?title={title}&author={author}"
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/search")
def search(request: Request, title: str, author: str, db: Session = Depends(get_db)):
    books = db.query(models.Book).filter(
        and_(func.lower(models.Book.title).contains(title.lower()), func.lower(models.Book.author).contains(author.lower()))).all()
    return templates.TemplateResponse("base.html", {"request": request, "lang": lang, "book_list": books})
