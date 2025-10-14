import unittest
from unittest.mock import patch
from library_service import add_book_to_catalog

class TestAddBookToCatalog(unittest.TestCase):

    @patch('library_service.get_book_by_isbn')
    @patch('library_service.insert_book')
    def test_successful_addition(self, mock_insert_book, mock_get_book_by_isbn):
        mock_get_book_by_isbn.return_value = None
        mock_insert_book.return_value = True
        success, msg = add_book_to_catalog("Test Title", "Author Name", "1234567890123", 3)
        self.assertTrue(success)
        self.assertIn("successfully added", msg)

    def test_empty_title(self):
        success, msg = add_book_to_catalog("", "Author", "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "Title is required.")

    def test_title_too_long(self):
        title = "T" * 201
        success, msg = add_book_to_catalog(title, "Author", "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "Title must be less than 200 characters.")

    def test_empty_author(self):
        success, msg = add_book_to_catalog("Title", "", "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "Author is required.")

    def test_author_too_long(self):
        author = "A" * 101
        success, msg = add_book_to_catalog("Title", author, "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "Author must be less than 100 characters.")

    def test_invalid_isbn_length(self):
        success, msg = add_book_to_catalog("Title", "Author", "12345", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "ISBN must be exactly 13 digits.")

    def test_total_copies_not_positive_int(self):
        for val in [0, -1, "five", 3.5]:
            success, msg = add_book_to_catalog("Title", "Author", "1234567890123", val)
            self.assertFalse(success)
            self.assertEqual(msg, "Total copies must be a positive integer.")

    @patch('library_service.get_book_by_isbn')
    def test_duplicate_isbn(self, mock_get_book_by_isbn):
        mock_get_book_by_isbn.return_value = {"id":1}
        success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "A book with this ISBN already exists.")

    @patch('library_service.get_book_by_isbn')
    @patch('library_service.insert_book')
    def test_database_error_on_insert(self, mock_insert_book, mock_get_book_by_isbn):
        mock_get_book_by_isbn.return_value = None
        mock_insert_book.return_value = False
        success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 2)
        self.assertFalse(success)
        self.assertEqual(msg, "Database error occurred while adding the book.")

if __name__ == '__main__':
    unittest.main()