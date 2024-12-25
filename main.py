from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from Models.books import Book, BookRespond, BookCreate, UpdateBook
from Models.database import SessionLocal

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a new book
@app.post("/books", response_model=BookRespond)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        new_book = Book(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            pb_date=book.pb_date,
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return new_book
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="ISBN must be unique")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# Retrieve all books
@app.get("/books", response_model=list[BookRespond])
def get_books(db: Session = Depends(get_db)):
    try:
        books = db.execute(select(Book)).scalars().all()
        return books
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

#Retrieve a particular book by it's id
@app.get("/books/{book_id}", response_model=BookRespond)
async def get_particular_details(book_id: int, db: Session = Depends(get_db)):
    try:
        book = db.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

#Delete a book by using it's id
@app.delete("/books/{book_id}", response_model=BookRespond)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        book = db.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        db.delete(book)
        db.commit()
        return book
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

#Update a particular book's content by refrencing it's id
@app.put("/books/{book_id}", response_model=BookRespond)
def update_book(book_id: int, book_update: UpdateBook, db: Session = Depends(get_db)):
    # Find the book by ID
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book_update.title is not None:
        book.title = book_update.title
    if book_update.author is not None:
        book.author = book_update.author
    if book_update.pb_date is not None:
        book.pb_date = book_update.pb_date

    db.commit()
    db.refresh(book)  

    return book