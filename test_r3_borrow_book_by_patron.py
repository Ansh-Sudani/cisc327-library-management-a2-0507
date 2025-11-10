import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from services.library_service import borrow_book_by_patron

class TestBorrowBookByPatron(unittest.TestCase):

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    @patch('library_service.insert_borrow_record')
    @patch('library_service.update_book_availability')
    def test_successful_borrow(self, mock_update_avail, mock_insert_borrow, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {
            'id': 1,
            'title': 'Test Book',
            'available_copies': 3
        }
        mock_borrow_count.return_value = 2
        mock_insert_borrow.return_value = True
        mock_update_avail.return_value = True

        success, msg = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn('Successfully borrowed', msg)
        self.assertIn('Due date:', msg)

    def test_invalid_patron_id(self):
        for invalid_id in ["", "12345", "abcdef", "1234567"]:
            success, msg = borrow_book_by_patron(invalid_id, 1)
            self.assertFalse(success)
            self.assertEqual(msg, "Invalid patron ID. Must be exactly 6 digits.")

    @patch('library_service.get_book_by_id')
    def test_book_not_found(self, mock_get_book):
        mock_get_book.return_value = None
        success, msg = borrow_book_by_patron("123456", 99)
        self.assertFalse(success)
        self.assertEqual(msg, "Book not found.")

    @patch('library_service.get_book_by_id')
    def test_no_available_copies(self, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 0}
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "This book is currently not available.")

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    def test_maximum_borrow_limit_reached(self, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 1}
        mock_borrow_count.return_value = 5

        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "You have reached the maximum borrowing limit of 5 books.")

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    @patch('library_service.insert_borrow_record')
    def test_error_on_insert_borrow_record(self, mock_insert_borrow, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 1}
        mock_borrow_count.return_value = 0
        mock_insert_borrow.return_value = False

        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Database error occurred while creating borrow record.")

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    @patch('library_service.insert_borrow_record')
    @patch('library_service.update_book_availability')
    def test_error_on_update_book_availability(self, mock_update_avail, mock_insert_borrow, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 1}
        mock_borrow_count.return_value = 0
        mock_insert_borrow.return_value = True
        mock_update_avail.return_value = False

        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Database error occurred while updating book availability.")

if __name__ == '__main__':
    unittest.main()