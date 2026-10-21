"""Unit tests for the FileHandler component."""

import unittest
from unittest.mock import patch
import pandas as pd
from pdf_downloader.components.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    """Test suite for validating FileHandler operations and exception handling."""

    def setUp(self):
        self.file_handler = FileHandler()
        self.__test_path = "data/mock_file.xlsx"
        self.__test_download_column: str
        self.__test_download_link_column_alternative: str


    def __mock_file_path(self):

        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_column,
            self.__test_download_link_column_alternative
        )

        self.file_handler.load_data()

        assert self.file_handler.get_file_content() is None

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_load_data(self, mock_read_excel, mock_logger_instance):
        """Test successful loading of an Excel file in-memory."""

        # 1. Arrange: Provide a valid mock DataFrame
        mock_df = pd.DataFrame({
            "A": ["BR50041", "BR50042"],
            "AL": ["url1", "url2"],
            "AM": ["url1", "url2"],
            "AP": ["", ""]
        })
        mock_read_excel.return_value = mock_df

        # Pass a clean test path right into the setter using self.file_handler
        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_column,
            self.__test_download_link_column_alternative
        )

        # Act
        self.file_handler.load_data()

        # 3. Assert: Verify the getter retrieves the loaded mock data properly
        loaded_df = self.file_handler.get_file_content()
        self.assertIsNotNone(loaded_df)
        self.assertEqual(len(loaded_df), 2)

        # Assert: Verify the getter retrieves a pandas dataframe
        self.assertIsInstance(self.file_handler.get_file_content(), pd.DataFrame)

        # 4. Assert: Verify read_excel was called with the exact parameters
        mock_read_excel.assert_called_once_with(
            self.__test_path,
            engine="openpyxl",
            usecols="A, AL, AM, AP"
        )

        # 5. Assert: Verify logging happened
        self.assertTrue(mock_logger_instance.info.called)

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_load_data_file_not_found(self, mock_read_excel, mock_logger_instance):
        """Test load_data handles FileNotFoundError gracefully when pandas cannot find the file."""

        mock_read_excel.side_effect = FileNotFoundError("No such file or directory")

        self.__mock_file_path()

        # 4. Assert: Check that error logging was called with the expected message
        expected_error_msg = (
            f"Error: The file '{self.__test_path}' could not be found. Please check the file path."
        )
        mock_logger_instance.error.assert_called_once_with(expected_error_msg)

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_permission_error(self, mock_read_excel, mock_logger_instance):
        """Test load_data handles PermissionError gracefully when pandas cannot find the file."""

        mock_read_excel.side_effect = PermissionError("Permission denied")

        self.__mock_file_path()

        expected_error_msg = (
            f"Error: Permission denied. Can't open '{self.__test_path}' right now."
        )

        mock_logger_instance.error.assert_called_once_with(expected_error_msg)

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_value_error(self, mock_read_excel, mock_logger_instance):
        """Test load_data handles ValueError when sheet or column configuration fails."""

        error_details = "Usecols do not match columns, columns expected but not found"
        mock_read_excel.side_effect = ValueError(error_details)

        self.__mock_file_path()

        expected_error_msg = f"Error with sheet or column configuration: {error_details}"
        mock_logger_instance.error.assert_called_once_with(expected_error_msg)

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_import_error(self, mock_read_excel, mock_logger_instance):
        """Test load_data handles ImportError gracefully when dependencies are missing."""

        error_details = "Missing optional dependency 'openpyxl'"
        mock_read_excel.side_effect = ImportError(error_details)

        self.__mock_file_path()

        expected_error_msg = f"Error: Could not open the sheet: {error_details}"
        mock_logger_instance.error.assert_called_once_with(expected_error_msg)

    @patch.object(FileHandler, "logger")
    @patch("pandas.read_excel")
    def test_unexpected_exception(self, mock_read_excel, mock_logger_instance):
        """Test load_data handles unexpected exceptions gracefully."""

        # Arrange: Raise a generic, unexpected exception (like RuntimeError)
        error_details = "Something completely unexpected happened"
        mock_read_excel.side_effect = RuntimeError(error_details)

        self.__mock_file_path()

        expected_error_msg = f"An unexpected error occurred: {error_details}"
        mock_logger_instance.exception.assert_called_once_with(expected_error_msg)


    def test_get_file_content_when_none(self):
        """Test when there is no file content."""

        self.assertEqual(self.file_handler.get_file_content(), None)
