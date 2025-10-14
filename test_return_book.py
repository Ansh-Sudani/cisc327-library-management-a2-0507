import pytest
from unittest.mock import patch
from library_service import return_book_by_patron

@patch("library_service.update_book_availability")
@patch("library_service.update_borrow_record_return_date")
@patch("library_service.get_book_by_id")
@patch("library_service.get_patron_borrow_count")
def test_return_success(mock_count, mock_get_book, mock_update_date, mock_update_avail):
    mock_get_book.return_value = {"id": 1, "title": "Book A", "available_copies": 0}
    mock_count.return_value = 1
    mock_update_date.return_value = True
    mock_update_avail.return_value = True

    success, msg = return_book_by_patron("123456", 1)
    assert success
    assert "successfully returned" in msg.lower()

def test_return_invalid_patron():
    success, msg = return_book_by_patron("12", 1)
    assert not success
    assert "invalid patron" in msg.lower()
