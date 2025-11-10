import unittest
from unittest.mock import patch
from services.library_service import return_book_by_patron

class TestReturnBookByPatron(unittest.TestCase):

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    @patch('library_service.update_book_availability')
    @patch('library_service.update_borrow_record_return_date')
    def test_successful_return(self, mock_update_return, mock_update_avail, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book'}
        mock_borrow_count.return_value = 2
        mock_update_avail.return_value = True
        mock_update_return.return_value = None  # void function

        success, msg = return_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn('successfully returned', msg)

    def test_invalid_patron_id(self):
        for invalid_id in ["", "12345", "abcdef", "1234567"]:
            success, msg = return_book_by_patron(invalid_id, 1)
            self.assertFalse(success)
            self.assertEqual(msg, "Invalid patron ID. Must be exactly 6 digits.")

    @patch('library_service.get_book_by_id')
    def test_book_not_found(self, mock_get_book):
        mock_get_book.return_value = None
        success, msg = return_book_by_patron("123456", 99)
        self.assertFalse(success)
        self.assertEqual(msg, "Book not found.")

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    def test_no_borrow_record_found(self, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book'}
        mock_borrow_count.return_value = 0

        success, msg = return_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "No record found of this patron borrowing any books.")

    @patch('library_service.get_book_by_id')
    @patch('library_service.get_patron_borrow_count')
    @patch('library_service.update_book_availability')
    def test_update_availability_failure(self, mock_update_avail, mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book'}
        mock_borrow_count.return_value = 1
        mock_update_avail.return_value = False

        success, msg = return_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Database error while updating book availability.")

if __name__ == '__main__':
    unittest.main()