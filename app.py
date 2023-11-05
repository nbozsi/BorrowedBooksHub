from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.staticfiles import StaticFiles

from starlette.responses import RedirectResponse, StreamingResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import func, text

import models
from database import SessionLocal, engine
from to_xlsx import to_xlsx
from tools import my_lower
import json

# TODO sqlite accent case sensitivity

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
    return templates.TemplateResponse("new_row.html", {"request": request, "lang": lang})


@app.put("/add")
def add(request: Request, title: str = Form(None), author: str = Form("Ismeretlen szerző"), renter: str = Form(None), db: Session = Depends(get_db)):

    new_book = models.Book(title=title, author=author, renter=renter)
    db.add(new_book)
    db.commit()

    return templates.TemplateResponse("row.html", {"request": request, "book": new_book})


@app.get("/change/{book_id}")
def change(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    return templates.TemplateResponse("update_row.html", {"request": request, "lang": lang, "book": book})


@app.put("/update/{book_id}")
def update(request: Request, book_id: int, author: str = Form("Ismeretlen szerző"), title: str = Form(...), renter: str = Form(None), db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    book.title = title
    book.author = author
    book.renter = renter
    db.commit()

    return templates.TemplateResponse("row.html", {"request": request, "lang": lang, "book": book})


@app.delete("/delete/{book_id}")
def delete_book(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    db.delete(book)
    db.commit()

    return HTMLResponse("")


@app.post('/startsearch')
def startsearch(request: Request, title: str = Form(""), author: str = Form(""), renter: str = Form(""), db: Session = Depends(get_db)):

    url = app.url_path_for("search") + \
        f"?title={title}&author={author}&renter={renter}"
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/search")
def search(request: Request, title: str, author: str, renter: str, db: Session = Depends(get_db)):
    books = db.query(models.Book)
    if author != '':
        books = books.filter(
            my_lower(models.Book.author).contains(author.lower()))
    if title != '':
        books = books.filter(
            my_lower(models.Book.title).contains(title.lower()))
    if renter != '':
        books = books.filter(
            my_lower(models.Book.renter).contains(renter.lower()))

    return templates.TemplateResponse("base.html", {"request": request, "lang": lang, "author": author, "title": title, "renter": renter, "book_list": books.order_by(models.Book.author).all()})


@app.get('/export')
def export(request: Request, db: Session = Depends(get_db)):
    with db.get_bind().connect() as conn:
        my_data = conn.execute(text("SELECT * FROM books"))

    output_file_name = "books_export.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{output_file_name}"'
    }
    file = to_xlsx(my_data)

    return StreamingResponse(file, headers=headers)
