"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4: Book Return Processing
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Verify that the book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Check if this book was borrowed by the patron (placeholder logic)
    # In a real system, we would query the borrow records table.
    borrow_count = get_patron_borrow_count(patron_id)
    if borrow_count == 0:
        return False, "No record found of this patron borrowing any books."

    # Update book availability (+1 copy)
    update_success = update_book_availability(book_id, 1)
    if not update_success:
        return False, "Database error while updating book availability."

    # Record the return date
    update_borrow_record_return_date(patron_id, book_id, datetime.now())

    return True, f'Book "{book["title"]}" successfully returned.'

def calculate_late_fee_for_book(patron_id: str, book_id: int, borrow_date: datetime, return_date: datetime = None) -> Dict:
    """
    Implements R5: Late Fee Calculation API
    
    Args:
        patron_id: 6-digit patron ID
        book_id: ID of the book
        borrow_date: datetime when the book was borrowed
        return_date: datetime when the book was returned; defaults to now if not provided
    
    Returns:
        dict: {
            'fee_amount': float,
            'days_overdue': int,
            'status': 'On time' or 'Overdue'
        }
    """
    if return_date is None:
        return_date = datetime.now()
    
    # Books are due 14 days after borrowing
    due_date = borrow_date + timedelta(days=14)
    days_overdue = (return_date - due_date).days

    if days_overdue <= 0:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'On time'}
    
    # $0.50/day for first 7 days, $1/day thereafter, capped at $15
    if days_overdue <= 7:
        fee = 0.5 * days_overdue
    else:
        fee = (0.5 * 7) + 1.0 * (days_overdue - 7)
    
    fee = min(fee, 15.0)
    
    return {
        'fee_amount': round(fee, 2),
        'days_overdue': days_overdue,
        'status': 'Overdue'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Implements R6: Catalog Search
    """
    books = get_all_books()
    term = search_term.strip().lower()
    results = []

    for book in books:
        if search_type == "title" and term in book["title"].lower():
            results.append(book)
        elif search_type == "author" and term in book["author"].lower():
            results.append(book)
        elif search_type == "isbn" and term == book["isbn"]:
            results.append(book)


    return results


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Implements R7: Patron Status Report
    """
    # Mock current borrowed books (would normally come from database)
    borrowed_books = [
        {"title": "Book A", "due_date": "2025-10-20", "status": "Borrowed"},
        {"title": "Book B", "due_date": "2025-10-05", "status": "Overdue"}
    ]

    # Mock borrowing history (returned books)
    borrowing_history = [
        {"title": "Book C", "returned_date": "2025-09-15"},
        {"title": "Book D", "returned_date": "2025-09-01"}
    ]

    return {
        "patron_id": patron_id,
        "borrowed_books": borrowed_books,
        "total_borrowed": len(borrowed_books),
        "outstanding_fees": 5.50,
        "borrowing_history": borrowing_history
    }
