"""Unit tests for the FileHandler component."""

import logging
import unittest
from unittest.mock import patch

import pandas as pd
import pytest

from pdf_downloader.components.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    """Test suite for validating FileHandler operations and exception handling."""

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        """Automatically inject pytest's caplog into unittest class instances."""
        self.__caplog = caplog

    def setUp(self):
        self.file_handler = FileHandler()
        self.__test_path = "data/mock_file.xlsx"
        self.__test_download_link_column = "AL"
        self.__test_download_link_column_alternative = "AM"

    def __mock_file_path(self):

        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )

        self.file_handler.load_data()

        assert self.file_handler.get_file_content() is None

    @patch("pandas.read_excel")
    def test_load_data(self, mock_read_sheet):
        """Test successful loading of an Excel file in-memory."""

        # Arrange: Provide a valid mock DataFrame
        mock_df = pd.DataFrame(
            {
                "A": ["BR50041", "BR50042"],
                self.__test_download_link_column: ["url1", "url2"],
                self.__test_download_link_column_alternative: ["url1", "url2"],
            }
        )
        mock_read_sheet.return_value = mock_df

        # Pass a clean test path right into the setter using self.file_handler
        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )

        # Run load_data inside the caplog context level
        with self.__caplog.at_level(logging.INFO):
            self.file_handler.load_data()

        # Assert: Verify the getter retrieves the loaded mock data properly
        loaded_df = self.file_handler.get_file_content()
        self.assertIsNotNone(loaded_df)
        self.assertEqual(len(loaded_df), 2)

        # Assert: Verify the getter retrieves a pandas dataframe
        self.assertIsInstance(self.file_handler.get_file_content(), pd.DataFrame)

        # Assert: Verify read_sheet was called with the exact parameters
        mock_read_sheet.assert_called_once_with(
            self.__test_path,
            engine="openpyxl",
            usecols=(
                "A,"
                f"{self.__test_download_link_column},"
                f"{self.__test_download_link_column_alternative}"
            ),
        )

        # Assert: Verify logging happened
        self.assertIn("Successfully loaded 2 rows", self.__caplog.text)

    @patch("pandas.read_excel")
    def test_load_data_file_not_found(self, mock_read_sheet):
        """Test load_data handles FileNotFoundError gracefully when pandas cannot find the file."""

        mock_read_sheet.side_effect = FileNotFoundError("No such file or directory")

        self.__mock_file_path()

        # 4. Assert: Check that error logging was called with the expected message
        expected_error_msg = f"Error: The file '{self.__test_path}' could not be found. Please check the file path."
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_permission_error(self, mock_read_excel):
        """Test load_data handles PermissionError gracefully when pandas cannot find the file."""

        mock_read_excel.side_effect = PermissionError("Permission denied")

        self.__mock_file_path()

        expected_error_msg = (
            f"Error: Permission denied. Can't open '{self.__test_path}' right now."
        )

        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_value_error(self, mock_read_excel):
        """Test load_data handles ValueError when sheet or column configuration fails."""

        error_details = "Usecols do not match columns, columns expected but not found"
        mock_read_excel.side_effect = ValueError(error_details)

        self.__mock_file_path()

        expected_error_msg = (
            f"Error with sheet or column configuration: {error_details}"
        )
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_import_error(self, mock_read_excel):
        """Test load_data handles ImportError gracefully when dependencies are missing."""

        error_details = "Missing optional dependency 'openpyxl'"
        mock_read_excel.side_effect = ImportError(error_details)

        self.__mock_file_path()

        expected_error_msg = f"Error: Could not open the sheet: {error_details}"
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_unexpected_exception(self, mock_read_excel):
        """Test load_data handles unexpected exceptions gracefully."""

        # Arrange: Raise a generic, unexpected exception (like RuntimeError)
        error_details = "Something completely unexpected happened"
        mock_read_excel.side_effect = RuntimeError(error_details)

        self.__mock_file_path()

        expected_error_msg = f"An unexpected error occurred: {error_details}"
        self.assertIn(expected_error_msg, self.__caplog.text)

    def test_get_file_content_when_none(self):
        """Test when there is no file content."""

        self.assertEqual(self.file_handler.get_file_content(), None)
