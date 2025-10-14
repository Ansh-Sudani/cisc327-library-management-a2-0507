import unittest
from unittest.mock import patch
from library_service import search_books_in_catalog

class TestSearchBooksInCatalog(unittest.TestCase):

    sample_books = [
        {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '1234567890123'},
        {'id': 2, 'title': 'Advanced Flask', 'author': 'Jane Smith', 'isbn': '9876543210987'},
        {'id': 3, 'title': 'Python Tips', 'author': 'John Doe', 'isbn': '1231231231231'},
    ]

    @patch('library_service.get_all_books')
    def test_search_title_partial_case_insensitive(self, mock_get_all_books):
        mock_get_all_books.return_value = self.sample_books
        results = search_books_in_catalog("python", "title")
        self.assertEqual(len(results), 2)
        self.assertTrue(all('python' in b['title'].lower() for b in results))

    @patch('library_service.get_all_books')
    def test_search_author_partial_case_insensitive(self, mock_get_all_books):
        mock_get_all_books.return_value = self.sample_books
        results = search_books_in_catalog("john", "author")
        self.assertEqual(len(results), 2)
        self.assertTrue(all('john' in b['author'].lower() for b in results))

    @patch('library_service.get_all_books')
    def test_search_isbn_exact_match(self, mock_get_all_books):
        mock_get_all_books.return_value = self.sample_books
        results = search_books_in_catalog("9876543210987", "isbn")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['isbn'], "9876543210987")

    @patch('library_service.get_all_books')
    def test_search_no_match(self, mock_get_all_books):
        mock_get_all_books.return_value = self.sample_books
        results = search_books_in_catalog("nonexistent", "title")
        self.assertEqual(len(results), 0)

    @patch('library_service.get_all_books')
    def test_search_invalid_type(self, mock_get_all_books):
        mock_get_all_books.return_value = self.sample_books
        results = search_books_in_catalog("something", "unknown")
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()