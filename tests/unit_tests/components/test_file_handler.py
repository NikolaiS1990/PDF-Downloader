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
        self.path_patcher = patch("pathlib.Path.exists", return_value=True)
        self.path_patcher.start()

        self.file_handler = FileHandler()
        self.__test_path = "data/mock_file.xlsx"
        self.__test_download_link_column = "AL"
        self.__test_download_link_column_alternative = "AM"

    def tearDown(self):
        # Stop the patcher after each test finishes
        self.path_patcher.stop()

    def __setup_and_attempt_load(self):
        """Helper to configure file info, trigger load_data (which fails), and ensure content is None."""

        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )

        self.file_handler.load_data()

        assert self.file_handler.get_file_content() is None

    def test_set_download_info_invalid_types(self):
        """Test that set_download_info raises ValueError for invalid types."""

        expected_error_msg = (
            "Expected a string for a path for an file, got <class 'int'>"
        )

        with self.assertRaises(TypeError) as excel_file_path_context_not_str_context:
            self.file_handler.set_download_info(
                123,
                self.__test_download_link_column,
                self.__test_download_link_column_alternative,
            )

        self.assertEqual(
            str(excel_file_path_context_not_str_context.exception), expected_error_msg
        )
        self.assertIn(expected_error_msg, self.__caplog.text)

        expected_error_msg = (
            "Expected a string for download_link_column, got <class 'int'>"
        )

        with self.assertRaises(TypeError) as download_column_context_not_str_context:
            self.file_handler.set_download_info(
                self.__test_path, 1234, self.__test_download_link_column_alternative
            )

        self.assertEqual(
            str(download_column_context_not_str_context.exception), expected_error_msg
        )
        self.assertIn(expected_error_msg, self.__caplog.text)

        expected_error_msg = (
            "Expected a string for download_link_column_alternative, got <class 'int'>"
        )

        with self.assertRaises(TypeError) as alternative_column_context_not_str_context:
            self.file_handler.set_download_info(
                self.__test_path, self.__test_download_link_column, 1234
            )
        self.assertEqual(
            str(alternative_column_context_not_str_context.exception),
            expected_error_msg,
        )
        self.assertIn(expected_error_msg, self.__caplog.text)

    def test_set_download_info_empty_file_path(self):
        """Test that set_download_info raises ValueError for empty file path."""

        expected_error_msg = "A path for an excel file must be provided, got "

        with self.assertRaises(ValueError) as no_path_context:
            self.file_handler.set_download_info(
                "",
                self.__test_download_link_column,
                self.__test_download_link_column_alternative,
            )

        self.assertEqual(str(no_path_context.exception), expected_error_msg)
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pathlib.Path.exists", return_value=False)
    def test_set_download_info_nonexistent_file_path(self, _mock_exists):
        """Test that set_download_info raises FileNotFoundError for nonexistent file path."""

        expected_error_msg = "Path does not exist: data/nonexistent_file.xlsx."

        with self.assertRaises(FileNotFoundError) as file_not_found_context:
            self.file_handler.set_download_info(
                "data/nonexistent_file.xlsx",
                self.__test_download_link_column,
                self.__test_download_link_column_alternative,
            )

        self.assertEqual(str(file_not_found_context.exception), expected_error_msg)
        self.assertIn(expected_error_msg, self.__caplog.text)

    def test_set_download_info_if_wrong_file_type(self):
        """Test that set_download_info raises ValueError for wrong file type."""

        expected_error_msg = "Expected an Excel file, got data/mock_file.txt"

        with self.assertRaises(ValueError) as context:
            self.file_handler.set_download_info(
                "data/mock_file.txt",
                self.__test_download_link_column,
                self.__test_download_link_column_alternative,
            )

        # Assert the exception message is correct
        self.assertEqual(str(context.exception), expected_error_msg)

        # Assert the error was logged
        self.assertIn(expected_error_msg, self.__caplog.text)

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

        self.__setup_and_attempt_load()

        # 4. Assert: Check that error logging was called with the expected message
        expected_error_msg = f"Error: The file '{self.__test_path}' could not be found. Please check the file path."
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_permission_error(self, mock_read_excel):
        """Test load_data handles PermissionError gracefully when pandas cannot find the file."""

        mock_read_excel.side_effect = PermissionError("Permission denied")

        self.__setup_and_attempt_load()

        expected_error_msg = (
            f"Error: Permission denied. Can't open '{self.__test_path}' right now."
        )

        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_value_error(self, mock_read_excel):
        """Test load_data handles ValueError when sheet or column configuration fails."""

        error_details = "Usecols do not match columns, columns expected but not found"
        mock_read_excel.side_effect = ValueError(error_details)

        self.__setup_and_attempt_load()

        expected_error_msg = (
            f"Error with sheet or column configuration: {error_details}"
        )
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_import_error(self, mock_read_excel):
        """Test load_data handles ImportError gracefully when dependencies are missing."""

        error_details = "Missing optional dependency 'openpyxl'"
        mock_read_excel.side_effect = ImportError(error_details)

        self.__setup_and_attempt_load()

        expected_error_msg = f"Error: Could not open the sheet: {error_details}"
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    def test_unexpected_exception(self, mock_read_excel):
        """Test load_data handles unexpected exceptions gracefully."""

        # Arrange: Raise a generic, unexpected exception (like RuntimeError)
        error_details = "Something completely unexpected happened"
        mock_read_excel.side_effect = RuntimeError(error_details)

        self.__setup_and_attempt_load()

        expected_error_msg = f"An unexpected error occurred: {error_details}"
        self.assertIn(expected_error_msg, self.__caplog.text)

    def test_get_file_content_when_none(self):
        """Test when there is no file content."""

        self.assertEqual(self.file_handler.get_file_content(), None)

    def test_save_updated_spreadsheet_without_load_data_raises_value_error(self):
        """Test that save_updated_spreadsheet raises ValueError if load_data was not called first."""

        mock_status_series = pd.Series(["Downloadet", "Ikke downloadet"])

        # Configure path info so only the __work_dataframe check fails
        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )

        expected_error_msg = (
            "You need to use load_data() before saving the updated spreadsheet."
        )

        with self.assertRaises(ValueError) as context:
            self.file_handler.save_updated_spreadsheet(mock_status_series)

        self.assertEqual(str(context.exception), expected_error_msg)
        self.assertIn(expected_error_msg, self.__caplog.text)

    def test_save_updated_spreadsheet_without_set_download_info_raises_value_error(
        self,
    ):
        """Test that save_updated_spreadsheet raises ValueError if set_download_info was not called first."""
        mock_status_series = pd.Series(["Downloadet", "Ikke downloadet"])

        expected_error_msg = "You need to use set_download_info() first."

        # Act & Assert on a fresh instance (no name mangling needed!)
        with self.assertRaises(ValueError) as context:
            self.file_handler.save_updated_spreadsheet(mock_status_series)

        self.assertEqual(str(context.exception), expected_error_msg)
        self.assertIn(expected_error_msg, self.__caplog.text)

    @patch("pandas.read_excel")
    @patch("pandas.DataFrame.to_excel")
    def test_save_updated_spreadsheet_success(self, mock_to_excel, mock_read_excel):
        """Test successful execution of save_updated_spreadsheet using public methods."""
        original_df = pd.DataFrame(
            {
                "BRnum": ["BR50041", "BR50042"],
                "Company": ["Corp A", "Corp B"],
            }
        )
        mock_read_excel.return_value = original_df

        # Set up state entirely through the public API
        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )

        # Populate work dataframe via public load method
        with patch("pandas.read_excel", return_value=original_df):
            self.file_handler.load_data()

        status_series = pd.Series(
            ["Downloadet", "Ikke downloadet"], name="Download Status"
        )

        # Act
        with self.__caplog.at_level(logging.INFO):
            self.file_handler.save_updated_spreadsheet(status_series)

        # Assert
        mock_to_excel.assert_called_once()
        self.assertIn("Successfully saved updated spreadsheet to:", self.__caplog.text)

    @patch("pandas.read_excel")
    def test_save_updated_spreadsheet_handles_exception(self, mock_read_excel):
        """Test save_updated_spreadsheet logs error and re-raises on unexpected exceptions."""
        error_details = "Disk full or write error"

        # Side effect sequence: 1st call for load_data succeeds, 2nd call for saving raises error
        mock_read_excel.side_effect = [
            pd.DataFrame(
                {
                    "A": ["BR50041", "BR50042"],
                    self.__test_download_link_column: ["url1", "url2"],
                    self.__test_download_link_column_alternative: ["url1", "url2"],
                }
            ),
            RuntimeError(error_details),
        ]

        # Prepare state entirely through the public API (no name mangling)
        self.file_handler.set_download_info(
            self.__test_path,
            self.__test_download_link_column,
            self.__test_download_link_column_alternative,
        )
        self.file_handler.load_data()

        status_series = pd.Series(["Downloadet", "Ikke downloadet"])

        # Act & Assert exception re-raising
        with self.assertRaises(RuntimeError):
            self.file_handler.save_updated_spreadsheet(status_series)

        # Assert logging happened
        expected_log = f"An unexpected error occurred: {error_details}"
        self.assertIn(expected_log, self.__caplog.text)
