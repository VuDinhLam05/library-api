from sqlalchemy import Column, Integer, String
from app.database import Base

class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
