"""Unit tests for the Main controller component."""

import unittest
from unittest.mock import patch
from pdf_downloader.main import Main


class TestMain(unittest.TestCase):
    """Test suite for validating Main controller initialization, argument parsing, and workflow."""

    def setUp(self):
        # Start patching FileHandler before Main() is initialized in setUp
        self.file_handler_patcher = patch("pdf_downloader.main.FileHandler")
        self.mock_file_handler_cls = self.file_handler_patcher.start()
        
        # Now setUp can safely create Main() with the mock active
        self.main_app = Main()

    def tearDown(self):
        # Clean up the patcher after every test
        self.file_handler_patcher.stop()

    def test_init(self):
        """Test initialization instantiates the FileHandler component."""
        self.assertIsNotNone(self.main_app)
        self.mock_file_handler_cls.assert_called_once()

    @patch("sys.argv", [
        "pdf_downloader",
        "--output_path", "/test/output",
        "--download_path", "/test/download",
        "--excel_gri_file_path", "/test/file.xlsx",
        "--download_link_column", "ColumnA",
        "--download_link_column_alternative", "ColumnB"
    ])
    def test_read_line_arguments_success(self):
        """Test command-line argument parsing successfully populates required arguments."""
        self.main_app.read_line_arguments()

        args = self.main_app._Main__args
        self.assertIsNotNone(args)
        self.assertEqual(args.output_path, "/test/output")
        self.assertEqual(args.download_path, "/test/download")
        self.assertEqual(args.excel_gri_file_path, "/test/file.xlsx")

    @patch("sys.argv", [
        "pdf_downloader",
        "--output_path", "/test/output"
    ])
    def test_read_line_arguments_missing_required(self):
        """Test argument parsing raises SystemExit when required arguments are missing."""
        with self.assertRaises(SystemExit):
            self.main_app.read_line_arguments()

    @patch("sys.argv", [
        "pdf_downloader",
        "--output_path", "/test/output",
        "--download_path", "/test/download",
        "--excel_gri_file_path", "/test/file.xlsx",
        "--download_link_column", "ColumnA"
    ])
    def test_start_program(self):
        """Test start_program correctly passes the file path and triggers data loading."""
        mock_handler_instance = self.mock_file_handler_cls.return_value

        self.main_app.read_line_arguments()
        self.main_app.start_program()

        mock_handler_instance.set_file_path.assert_called_once_with("/test/file.xlsx")
        mock_handler_instance.load_data.assert_called_once()