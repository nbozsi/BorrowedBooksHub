from sqlalchemy import DateTime, Column, Integer, String, Boolean

from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    lend = Column(String)
