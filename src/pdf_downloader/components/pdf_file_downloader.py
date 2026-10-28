"""PDF Downloader Module.

This module provides functionality for downloading PDF reports from a
fixed-structure DataFrame using primary URLs with automatic fallback to
alternative URLs, in-memory status tracking, and file validation
(MIME type inspection, size constraints, and EOF trailer verification) with
automatic cleanup of invalid or failed downloads.

Classes:
    PdfFileDownloader: Manages iterating through DataFrame rows, downloading PDFs,
        handling URL fallbacks, validating file integrity, updating status,
        and cleaning up failed or corrupted files.

Author:
    Nikolai Sandbeck
"""

import logging
import os
import urllib.error
import urllib.request
from pathlib import Path

import magic
import pandas as pd


class PdfFileDownloader:
    """Handles downloading PDF files from a fixed-structure DataFrame with fallback support and validation.

    This class iterates through a standardized DataFrame using fixed positional indexing,
    attempts to download PDF reports using primary URLs with automatic fallback to alternative
    URLs, validates downloaded files (checking file extensions, size limits,
    MIME types via python-magic, and trailer %%EOF markers), tracks download success/failure
    status in memory, and handles automatic cleanup of partial, invalid, or failed downloads.

    Attributes:
        __logger (logging.Logger): Logger instance for recording download progress, warnings, and errors.
        __timeout (int): Request timeout limit in seconds for URL downloads (default is 20).
        __download_success (bool): Internal flag tracking whether the latest individual download attempt succeeded.

    Public Method:
        download_reports: Iterates through the DataFrame, executes downloads with fallback, and returns the status series.

    Private Methods:
        __download_single_url: Attempts to download a single file from a given URL with timeout and error handling.
        __PDF_file_vaildator: Validates file integrity, extension, size, MIME type, and EOF markers, unlinking bad files.

    Usage Example:
        downloader = PdfFileDownloader()
        status_series = downloader.download_reports("data/downloaded_pdfs", work_dataframe)
    """

    __logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.__timeout: int = 20
        self.__download_success: bool = False

    def __PDF_file_vaildator(self, file_path: str) -> bool:
        """Validate that a downloaded file at the given path is a genuine, complete PDF.

        Performs the following validation checks:
            1. Verifies the file has a .pdf extension.
            2. Verifies the file is not empty (size > 0 bytes).
            3. Verifies the file does not exceed the maximum allowed size (100 MB).
            4. Inspects the first 2,048 bytes using python-magic to verify
               that the true MIME type is strictly 'application/pdf'.
            5. Inspects the tail of the file to ensure it contains the
               '%%EOF' trailer marker (guarding against truncated downloads).

        Side Effects:
            - **File Deletion (Unlink):** If the file fails any validation check
              (empty, oversized, wrong MIME type, or missing EOF marker), it is
              immediately and permanently deleted from disk using `path.unlink()`.
            - **Logging & Output:** Prints warning notifications to stdout and
              emits warning-level log records via `self.__logger`.

        Args:
            file_path (str): The path to the file on disk to validate.

        Returns:
            bool: True if the file successfully passes all validation checks.

        Raises:
            ValueError: If the file is empty, too large, has an invalid MIME type,
                        or lacks the PDF EOF trailer marker.
            Exception: If an unexpected I/O error occurs while reading the file.
        """

        path = Path(file_path)
        file_size = path.stat().st_size

        # 1. Check if file has a .pdf extension
        if path.suffix.lower() != ".pdf":
            msg = f"File at {path} does not have a .pdf extension."
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        # 2. Check if file is empty
        if file_size == 0:
            path.unlink(missing_ok=True)
            msg = f"File at {path} is empty. Size: {file_size} bytes"
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        # 3. Check if file is too large (> 100 MB)
        if file_size > 104857600:  # 100 MB
            path.unlink(missing_ok=True)
            msg = f"File at {path} is too large. Size: {file_size} bytes"
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        # 4. Read the file buffer from disk
        try:
            with open(path, "rb") as f:
                head_chunk = f.read(2048)

                tail_size = min(1024, file_size)
                f.seek(-tail_size, os.SEEK_END)
                tail_chunk = f.read(tail_size)
        except Exception as e:
            msg = f"Error reading file at {path}: {e}"
            print(msg)
            self.__logger.warning(msg)
            raise

        # 5. Check MIME type using python-magic
        mime_type = magic.from_buffer(head_chunk, mime=True)

        if mime_type != "application/pdf":
            path.unlink(missing_ok=True)
            msg = f"File at {path} is not a valid PDF. Detected MIME type: {mime_type}"
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        # 6. Check for PDF EOF marker (%%EOF) is in the end of the file
        if b"%%EOF" not in tail_chunk:
            path.unlink(missing_ok=True)
            msg = f"File at {path} does not contain a valid PDF EOF marker."
            print(msg)
            self.__logger.warning(msg)
            raise ValueError(msg)

        return True

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

            self.__PDF_file_vaildator(download_path)

            return True

        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            OSError,
            ValueError,
        ) as e:
            # Only log warnings for none-ValueError exceptions,
            # because ValueError is already logged in __PDF_file_vaildator
            if not isinstance(e, ValueError):
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
