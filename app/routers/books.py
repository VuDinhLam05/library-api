from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import BookModel
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    year: int = Field(..., ge=1000, le=2030)
    isbn: str = Field(..., min_length=10)
    category: str = Field(..., min_length=1)
    quantity: int = Field(1, ge=0)

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None

class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True

@router.get("", response_model=List[BookResponse])
def get_books(
    q: Optional[str] = None,
    author: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(BookModel)
    if q:
        query = query.filter(BookModel.title.contains(q) | BookModel.category.contains(q))
    if author:
        query = query.filter(BookModel.author.contains(author))
    return query.offset(skip).limit(limit).all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"error": "Not Found", "message": "Không tìm thấy sách"}
        )
    return book

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    existing_book = db.query(BookModel).filter(BookModel.isbn == book.isbn).first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail={"error": "Conflict", "message": "ISBN đã tồn tại trong hệ thống"}
        )
    
    db_book = BookModel(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- NGHIỆP VỤ MƯỢN / TRẢ SÁCH (BÀI MỞ RỘNG) ---
@router.post("/{book_id}/borrow", response_model=BookResponse)
def borrow_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"error": "Not Found", "message": "Không tìm thấy sách"}
        )
    if book.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail={"error": "Conflict", "message": "Sách đã hết"}
        )
    
    book.quantity -= 1
    db.commit()
    db.refresh(book)
    return book

@router.post("/{book_id}/return", response_model=BookResponse)
def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"error": "Not Found", "message": "Không tìm thấy sách"}
        )
    
    book.quantity += 1
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"error": "Not Found", "message": "Không tìm thấy sách"}
        )
    db.delete(db_book)
    db.commit()
    return None
