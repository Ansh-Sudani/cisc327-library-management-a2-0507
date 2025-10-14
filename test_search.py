import pytest
from unittest.mock import patch
from library_service import search_books_in_catalog

# Sample book data
BOOKS = [
    {"title": "Harry Potter", "author": "J.K. Rowling", "isbn": "1234567890123"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "3216549870123"},
    {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "1112223334445"}
]

# ----------------------------
# Test: Search by title (partial, case-insensitive)
# ----------------------------
@patch("library_service.get_all_books")
def test_search_by_title(mock_get_books):
    mock_get_books.return_value = BOOKS
    results = search_books_in_catalog("harry", "title")
    assert len(results) == 1
    assert results[0]["title"] == "Harry Potter"

    # Case-insensitive check
    results = search_books_in_catalog("HARRY", "title")
    assert len(results) == 1

# ----------------------------
# Test: Search by author (partial, case-insensitive)
# ----------------------------
@patch("library_service.get_all_books")
def test_search_by_author(mock_get_books):
    mock_get_books.return_value = BOOKS
    results = search_books_in_catalog("martin", "author")
    assert len(results) == 1
    assert results[0]["author"] == "Robert C. Martin"

    # Case-insensitive check
    results = search_books_in_catalog("MARTIN", "author")
    assert len(results) == 1

# ----------------------------
# Test: Search by ISBN (exact match only)
# ----------------------------
@patch("library_service.get_all_books")
def test_search_by_isbn(mock_get_books):
    mock_get_books.return_value = BOOKS
    results = search_books_in_catalog("1234567890123", "isbn")
    assert len(results) == 1
    assert results[0]["title"] == "Harry Potter"

    # Partial ISBN should return nothing
    results = search_books_in_catalog("123456", "isbn")
    assert len(results) == 0

# ----------------------------
# Test: No results returned
# ----------------------------
@patch("library_service.get_all_books")
def test_search_no_results(mock_get_books):
    mock_get_books.return_value = BOOKS
    results = search_books_in_catalog("Nonexistent Book", "title")
    assert results == []

    results = search_books_in_catalog("Unknown Author", "author")
    assert results == []

    results = search_books_in_catalog("0000000000000", "isbn")
    assert results == []
