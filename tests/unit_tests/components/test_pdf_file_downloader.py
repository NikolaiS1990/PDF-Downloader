"""Unit tests for the PdfFileDownloader component."""

import logging
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

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

    @patch("pdf_downloader.components.pdf_file_downloader.urllib.request.urlopen")
    @patch("os.path.exists")
    def test_successful_primary_download(self, mock_path_exists, mock_urlopen):
        """Test successful download on the primary URL."""
        mock_path_exists.return_value = (
            True  # Pretend download_path and saved file exist when checking
        )

        mock_response = MagicMock()
        mock_response.read.return_value = b"%PDF-1.4 mock content"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        df = pd.DataFrame(
            {
                "ID": ["001"],
                "Primary": ["http://example.com/primary.pdf"],
                "Alternative": ["http://example.com/alt.pdf"],
                "Status": ["Pending"],
            }
        )

        with patch("builtins.open", create=True):
            status_series = self.pdf_file_downloader.download_reports(
                "mock_download_path", df
            )

        self.assertEqual(status_series.iloc[0], "Downloadet")

    @patch("pdf_downloader.components.pdf_file_downloader.urllib.request.urlopen")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_fallback_to_alternative_url_and_cleanup(
        self, _mock_remove, mock_path_exists, mock_urlopen
    ):
        """Test that primary failure triggers alternative URL download, and total failure triggers file cleanup."""
        mock_path_exists.side_effect = lambda path: True

        mock_urlopen.side_effect = [
            urllib.error.URLError("Primary connection timeout"),
            MagicMock(read=lambda: b"%PDF-1.4 mock content"),
        ]

        df = pd.DataFrame(
            {
                "ID": ["002"],
                "Primary": ["http://example.com/broken.pdf"],
                "Alternative": ["http://example.com/working.pdf"],
                "Status": ["Pending"],
            }
        )

        with patch("builtins.open", create=True):
            status_series = self.pdf_file_downloader.download_reports(
                "mock_download_path", df
            )

        self.assertEqual(status_series.iloc[0], "Downloadet")

    @patch("pdf_downloader.components.pdf_file_downloader.urllib.request.urlopen")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_total_download_failure_and_cleanup(
        self, mock_remove, mock_path_exists, mock_urlopen
    ):
        """Test that if both primary and alternative fail, status is 'Ikke downloadet' and file is cleaned up."""
        mock_path_exists.side_effect = lambda _path: True
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        df = pd.DataFrame(
            {
                "ID": ["003"],
                "Primary": ["http://example.com/broken1.pdf"],
                "Alternative": ["http://example.com/broken2.pdf"],
                "Status": ["Pending"],
            }
        )

        with patch("builtins.open", create=True):
            status_series = self.pdf_file_downloader.download_reports(
                "mock_download_path", df
            )

        self.assertEqual(status_series.iloc[0], "Ikke downloadet")
        mock_remove.assert_called()
