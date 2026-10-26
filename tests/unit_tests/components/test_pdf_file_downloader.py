"""Unit tests for the PdfFileDownloader component."""

import logging
import unittest

import pandas as pd
import pytest

from pdf_downloader.components.pdf_file_downloader import PdfFileDownloader


class TestPdfFileDownloader(unittest.TestCase):
    """Test suite for validating PdfFileDownloader operations and exception handling."""

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        """Automatically inject pytest's caplog into unittest class instances."""
        self.__caplog = caplog

    def setUp(self):
        self.pdf_file_downloader = PdfFileDownloader()
        self.__test_download_path = "mock_download_path"

    def test_if_df_is_none_or_empty(self):
        """Test if it throws ValueError if df is none or empty, and if it calls the logger."""

        empty_df = pd.DataFrame()

        with (
            self.assertRaises(ValueError) as context_none,
            self.__caplog.at_level(logging.WARNING),
        ):
            self.pdf_file_downloader.download_reports(
                self.__test_download_path, df=None
            )

        self.assertIn("DataFrame is empty or None", str(context_none.exception))
        self.assertIn("DataFrame is empty or None", self.__caplog.text)

        with (
            self.assertRaises(ValueError) as context_empty,
            self.__caplog.at_level(logging.WARNING),
        ):
            self.pdf_file_downloader.download_reports(
                self.__test_download_path, empty_df
            )

        self.assertIn("DataFrame is empty or None", str(context_empty.exception))
        self.assertIn("DataFrame is empty or None", self.__caplog.text)

    def test_if_download_path_does_not_exist(self):
        """Test if it throws ValueError if download_path does not exist, and if it calls the logger."""

        df = pd.DataFrame({"ID": [1], "Primary Link": ["http://example.com/file.pdf"]})

        with (
            self.assertRaises(ValueError) as context,
            self.__caplog.at_level(logging.WARNING),
        ):
            self.pdf_file_downloader.download_reports("non_existent_path", df)

        self.assertIn(
            "Download path 'non_existent_path' does not exist", str(context.exception)
        )
        self.assertIn(
            "Download path 'non_existent_path' does not exist", self.__caplog.text
        )
