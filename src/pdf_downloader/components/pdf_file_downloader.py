"""PDF Downloader Module.

This module provides functionality for downloading PDF reports from a
fixed-structure DataFrame using primary URLs with automatic fallback to
alternative URLs, in-memory status tracking, and cleanup of failed downloads.

Classes:
    PdfFileDownloader: Manages iterating through DataFrame rows, downloading PDFs,
        handling URL fallbacks, updating status, and cleaning up failed files.

Author:
    Nikolai Sandbeck
"""

import logging
import os
import urllib.error
import urllib.request

import pandas as pd


class PdfFileDownloader:
    """Handles downloading PDF files from a fixed-structure DataFrame with fallback support.

    This class iterates through a standardized DataFrame using fixed positional indexing,
    attempts to download PDF reports using primary URLs with automatic fallback to alternative
    URLs, tracks download success/failure status in memory, and handles cleanup of partial
    or failed downloads.

    Attributes:
        __logger (logging.Logger): Logger instance for recording download progress, warnings, and errors.
        __timeout (int): Request timeout limit in seconds for URL downloads (default is 20).
        __download_success (bool): Internal flag tracking whether the latest individual download attempt succeeded.

    Public Method:
        download_reports: Iterates through the DataFrame, executes downloads with fallback, and returns the status series.

    Private Method:
        __download_single_url: Attempts to download a single file from a given URL with a timeout and error handling.

    Usage Example:
        downloader = PdfFileDownloader()
        status_series = downloader.download_reports("data/downloaded_pdfs", work_dataframe)
    """

    __logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.__timeout: int = 20
        self.__download_success: bool = False

    def __download_single_url(self, download_url: str, download_path: str) -> bool:
        """Attempt to download a file from a URL with a timeout.

        Args:
            download_url (str): The URL to download from.
            download_path (str): Local destination file path.

        Returns:
            bool: True if successful, False otherwise.

        Side effects:
            It write to log if a download attempt fails
        """

        try:
            req = urllib.request.Request(
                download_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )

            with (
                urllib.request.urlopen(req, timeout=self.__timeout) as response,
                open(download_path, "wb") as pdf_file,
            ):
                pdf_file.write(response.read())

            return True

        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            OSError,
        ) as e:
            self.__logger.warning("Failed to download %s: %s", download_url, e)
            return False

    def download_reports(
        self,
        download_path: str,
        df: pd.DataFrame,
    ) -> pd.Series:
        """Iterate through the DataFrame using fixed column order, download PDFs, and update status.

        Assumes DataFrame column order:
            - Index 0: ID column
            - Index 1: Primary URL column
            - Index 2: Alternative URL column
            - Index 3: Status column

        Args:
            download_path (str): The directory to save downloaded PDFs.
            df (pd.DataFrame): The standardized DataFrame from FileHandler.

        Returns:
            pd.Series: The updated status column.

        Side effects:
            It writes to the log and console.
            It updates the private __download_success attribute.
        """
        if df is None or df.empty:
            msg = "DataFrame is empty or None. No reports to download."
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        if not os.path.exists(download_path):
            msg = f"Download path '{download_path}' does not exist. Make sure the directory is created before running the download."
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        total_rows = len(df)
        self.__logger.info("Starting download process for %d rows...", total_rows)

        for idx, row in df.iterrows():
            # Respect server limits
            # sleep(2)

            # Fixed positions guarantee where data and status live
            record_id = str(row.iloc[0])
            primary_url = row.iloc[1]
            alternative_url = row.iloc[2]
            status_column = df.columns[3]

            save_file_name = f"{record_id}.pdf"
            save_file_path = os.path.join(download_path, save_file_name)

            self.__download_success = False

            # 1. Try primary URL (Index 1)
            if pd.notna(primary_url) and str(primary_url).strip():
                msg = f"Attempting primary download for ID: {record_id}"
                print(msg)
                self.__logger.info(msg)
                self.__download_success = self.__download_single_url(
                    str(primary_url), save_file_path
                )

            # 2. Fall back to alternative URL (Index 2) if primary fails
            if (
                not self.__download_success
                and pd.notna(alternative_url)
                and str(alternative_url).strip()
            ):
                msg = f"Primary failed. Attempting alternative download for ID: {record_id}"
                print(msg)
                self.__logger.info(msg)
                self.__download_success = self.__download_single_url(
                    str(alternative_url), save_file_path
                )

            # 3. Update status in memory
            if self.__download_success:
                df.at[idx, status_column] = "Downloadet"
                msg = f"Successfully downloaded report for ID: {record_id}"
                print(msg)
                self.__logger.info(msg)
            else:
                df.at[idx, status_column] = "Ikke downloadet"
                msg = f"Failed to download report for ID: {record_id}"
                print(msg)
                self.__logger.info(msg)

                # Clean up empty/failed attempt pdf-files ONLY on failure
                if os.path.exists(save_file_path):
                    try:
                        os.remove(save_file_path)
                    except OSError:
                        pass

        msg = "All downloads completed. Returning updated status column."
        print(msg)
        self.__logger.info(msg)

        return df[status_column]
