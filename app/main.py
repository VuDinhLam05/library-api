from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException
from app.database import engine, Base, SessionLocal
from app.models import BookModel
from app.routers import books

Base.metadata.create_all(bind=engine)

def init_sample_data():
    db = SessionLocal()
    try:
        if db.query(BookModel).count() == 0:
            sample_books = [
                BookModel(title="Nhập môn Mạng máy tính", author="Nguyễn Văn A", year=2021, isbn="978-604-0-00001-1", category="Mạng máy tính", quantity=5),
                BookModel(title="Lập trình Python nâng cao", author="Trần Thị B", year=2022, isbn="978-604-0-00002-8", category="Lập trình", quantity=0) # Sách này quantity = 0 để test TC hết sách
            ]
            db.add_all(sample_books)
            db.commit()
    finally:
        db.close()

init_sample_data()

app = FastAPI(
    title="Library API - Extension Borrow/Return",
    version="2.1.0"
)

# Exception Handler thống nhất định dạng lỗi
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Exception", "message": str(exc.detail)}
    )

app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Library API Extension is running!"}
