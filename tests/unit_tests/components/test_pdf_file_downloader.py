"""Unit tests for the PdfFileDownloader component."""

import unittest
import pandas as pd
from pdf_downloader.components.pdf_file_downloader import PdfFileDownloader


class TestPdfFileDownloader(unittest.TestCase):
    """Test suite for validating PdfFileDownloader operations and exception handling."""


    def setUp(self):
        self.pdf_file_downloader = PdfFileDownloader()
        self.__test_download_path = "mock_ownload_path"

    @patch.object(PdfFileDownloader, "logger")
    @patch("pandas.read_sheet")
    def test_if_df_is_none_or_empty():
        """Test if it throws ValueError if df is none or empty, and if it calls the logger."""

        mock_df = pd.DataFrame({
            
        })