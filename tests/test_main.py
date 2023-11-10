import pytest

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app, get_db
from app.models import Book

client = TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def book_details():
    return Book(title="TEST_TITLE", author="TEST_AUTHOR",
                renter="TEST_RENTER")


@pytest.fixture
def add_book(db, book_details):
    db.add(book_details)
    db.commit()


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "BorrowedBooksHub" in response.text


def test_new():
    response = client.get("/new")
    assert response.status_code == 200
    assert response.text.count("<input") == 3


def test_add_put_is_only_allowed():
    # get is not allowed
    response = client.get("/add")
    assert response.status_code == 405
    # post is not allowed
    response = client.post("/add")
    assert response.status_code == 405


def test_add_check_data(db, book_details):
    response = client.put("/add",
                          data={"title": book_details.title, "author": book_details.author, "renter": book_details.renter})
    # filtering by the attributes of the book_details
    book_model = db.query(Book).filter(Book.author == book_details.author).filter(
        Book.title == book_details.title).filter(Book.renter == book_details.renter).first()

    assert response.status_code == 200
    assert response.headers["hx-trigger"] == 'addedRecord'
    assert book_model is not None
    assert book_model.title == book_details.title
    assert book_model.author == book_details.author
    assert book_model.renter == book_details.renter

    # cleanup
    db.delete(book_model)
    db.commit()


def test_update_book_is_changed(add_book, db, book_details):

    response = client.put(f"/update/{book_details.id}",
                          data={"title": "CHANGED_TITLE", "author": "CHANGED_AUTHOR", "renter": "CHANGED_RENTER"})
    book_model = db.get(Book, book_details.id)
    # needed to get the current state of the updated book
    db.refresh(book_model)

    assert response.status_code == 200
    assert book_model is not None
    assert book_model.title == "CHANGED_TITLE"
    assert book_model.author == "CHANGED_AUTHOR"
    assert book_model.renter == "CHANGED_RENTER"

    db.delete(book_model)
    db.commit()


def test_delete_book(add_book, db, book_details):

    response = client.delete(f"/delete/{book_details.id}")

    book_model = db.query(Book).filter_by(id=book_details.id).scalar()

    assert response.status_code == 200
    assert book_model is None


def test_get_count(db):
    response = client.get("/get_count")
    given_count = int(''.join(
        letter for letter in response.text if letter.isdigit()))
    assert response.status_code == 200
    assert given_count == db.query(Book).count()
