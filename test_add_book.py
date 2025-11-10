import pytest
from services.library_service import add_book_to_catalog
from unittest.mock import patch

@patch("library_service.insert_book")
@patch("library_service.get_book_by_isbn")
def test_add_book_success(mock_get, mock_insert):
    mock_get.return_value = None
    mock_insert.return_value = True
    success, msg = add_book_to_catalog("Test Book", "Author", "1234567890123", 3)
    assert success
    assert "successfully added" in msg.lower()

def test_add_book_missing_title():
    success, msg = add_book_to_catalog("", "Author", "1234567890123", 3)
    assert not success
    assert "title is required" in msg.lower()

def test_add_book_invalid_isbn():
    success, msg = add_book_to_catalog("Book", "Author", "123", 3)
    assert not success
    assert "13 digits" in msg.lower()

def test_add_book_negative_copies():
    success, msg = add_book_to_catalog("Book", "Author", "1234567890123", -1)
    assert not success
    assert "positive integer" in msg.lower()
