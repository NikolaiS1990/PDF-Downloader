import logging
import urllib.request

import pandas as pd


class PdfFileDownloader:
    logger = logging.getLogger(__name__)

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
                download_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
            OSError
        ) as e:
            self.logger.warning("Failed to download %s: %s", download_url, e)
            return False


    def download_reports(
        self,
        id_column: str,
        download_path: str,
        download_link_column: str,
        download_link_column_alternative: str,
        status_column: str,
        df: pd.DataFrame,
    ) -> None:
        """Iterate through the DataFrame, download PDFs.

        It uses primary/alternative URLs, and update status.
        If the program does not crash, it will attach the status column to the
        original spread sheet.

        Args:
            id_column: The ID-column, it assumes it is the first column in the data sheet.
            download_path: The directory to put the PDFs in.
            download_url: the URL for downloading.
            status_column: The status column to mark if a download was a success or not.
            df (pd.DataFrame): The DataFrame containing metadata and URLs.

        Returns:
            pd.DataFrame: The updated status column.

        Side effects:
            It writes to the log.
            It updates the private __download_success attribute.
        """

        total_rows = len(df)
        self.logger.info("Starting download process for %d rows....", total_rows)


        for idx, row in df.iterrows():
            # Sleep to avoid overloading servers.
            sleep(2)

            # Use record ID from id_column
            record_id = str(row.get(id_column, idx))
            save_file_name = f"{record_id}.pdf"
            save_file_path = os.path.join(download_path, save_file_name)

            primary_url = row.get(download_link_column)
            alternative_url = row.get(download_link_column_alternative)

        # Try primary URL
        if pd.notna(primary_url) and str(primary_url).strip():
            msg = "Attempting primary download for ID: %s", record_id
            print(msg)
            self.logger.info(msg)
            self.__download_success = self.__download_single_url(primary_url, save_file_path)

        # Fall back to alternative URL if primary fails.
        if not self.__download_success and pd.notna(alternative_url) and str(alternative_url).strip():
            msg = "Primary failed. Attempting alternative download for ID: %s", record_id
            print(msg)
            self.logger.info(msg)
            self.__download_success = self.__download_single_url(str(alternative_url), save_file_path)

        # Update status in memory only
        if self.__download_success
            df.at[idx, self.__status_column] = "Downloadet"
            msg = "Successfully downloaded report for ID: %s", record_id
            print(msg)
            self.logger.info(msg)
        else:
            df.at[idx, self.__status_column] = "Ikke downloadet"
            msg = "Failed to download report for ID: %s", record_id
            print(msg)
            self.logger.info(msg)

            # Clean up empty/failed attempt pdf-files
            if os.path.exists(save_file_path):
                try:
                    os.remove(save_file_path)
                except OSError:
                    pass

        msg = "All downloads completed. Returning updated status column."
        print(msg)
        self.logger.info(msg)
        return df[status_column]