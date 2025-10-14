import pytest
from library_service import borrow_book_by_patron
from unittest.mock import patch

@patch("library_service.update_book_availability")
@patch("library_service.insert_borrow_record")
@patch("library_service.get_patron_borrow_count")
@patch("library_service.get_book_by_id")
def test_borrow_success(mock_get_book, mock_borrow_count, mock_insert_record, mock_update):
    mock_get_book.return_value = {"id": 1, "title": "Book A", "available_copies": 2}
    mock_borrow_count.return_value = 2
    mock_insert_record.return_value = True
    mock_update.return_value = True

    success, msg = borrow_book_by_patron("123456", 1)
    assert success
    assert "successfully borrowed" in msg.lower()

def test_borrow_invalid_patron_id():
    success, msg = borrow_book_by_patron("12", 1)
    assert not success
    assert "invalid patron id" in msg.lower()

@patch("library_service.get_book_by_id")
def test_borrow_book_not_found(mock_get_book):
    mock_get_book.return_value = None
    success, msg = borrow_book_by_patron("123456", 999)
    assert not success
    assert "book not found" in msg.lower()

@patch("library_service.get_book_by_id")
def test_borrow_book_unavailable(mock_get_book):
    mock_get_book.return_value = {"id": 1, "title": "Book A", "available_copies": 0}
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success
    assert "not available" in msg.lower()

@patch("library_service.get_book_by_id")
@patch("library_service.get_patron_borrow_count")
def test_borrow_exceeds_limit(mock_borrow_count, mock_get_book):
    mock_get_book.return_value = {"id": 1, "title": "Book A", "available_copies": 1}
    mock_borrow_count.return_value = 6
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success
    assert "maximum borrowing limit" in msg.lower()
