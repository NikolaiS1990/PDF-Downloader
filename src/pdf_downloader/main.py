"""Main module for the PDF Downloader application.

This module handles the initialization of the application..

Class:
    Main: The main controller class for the PDF Downloader.

Author:
    Nikolai Sandbeck
"""

import argparse
import logging
from pdf_downloader.components.file_handler import FileHandler
from pdf_downloader.components.pdf_file_downloader import PdfFileDownloader


class Main:
    """Main controller class for the PDF Downloader application.

    Attributes:
        logger (logging.Logger): Logger instance for the Main class.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self):
        self.__args = None
        self.__logger.info("PDF Downloader initialized.")
        self.__file_handler = FileHandler()
        self.__pdf_file_downloader = PdfFileDownloader()

    def read_line_arguments(self) -> None:
        """Parse command-line arguments required for the PDF Downloader."""

        parser = argparse.ArgumentParser(description="PDF Downloader Arguments")

        parser.add_argument(
            "--download_path", required=True, help="Path for the download folder"
        )

        parser.add_argument(
            "--excel_gri_file_path", required=True, help="Path for the GRI file"
        )

        parser.add_argument(
            "--download_link_column",
            required=True,
            help="Column with links for downloading.",
        )

        parser.add_argument(
            "--download_link_column_alternative",
            required=True,
            help=(
                "Column with links for downloading if the a link in the first column does not work."
            ),
        )

        self.__args = parser.parse_args()

        self.__logger.info("Arguments received: %s", self.__args)

        if self.__args.download_link_column == self.__args.download_link_column_alternative:
            msg = "Primary and alternative download columns cannot be the same column."
            print(msg)
            self.__logger.error(msg)
            raise ValueError(msg)


    def get_arguments(self) -> str | None:
        """Return the parsed command-line arguments or None if uninitialized."""

        if not self.__args:
            return None

        return self.__args

    def start_program(self) -> None:
        """Configure the file handler and initiate the data loading workflow."""

        self.__file_handler.set_download_info(
            self.__args.excel_gri_file_path,
            self.__args.download_link_column,
            self.__args.download_link_column_alternative,
        )

        self.__file_handler.load_data()

        work_file_content = self.__file_handler.get_file_content()
        updated_status_column = self.__pdf_file_downloader.download_reports(
            self.__args.download_path,
            work_file_content
        )



        # print(self.__file_handler.get_file_content())
