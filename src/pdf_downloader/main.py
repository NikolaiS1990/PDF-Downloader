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

class Main:

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__args = None
        self.logger.info("PDF Downloader initialized.")
        self.__file_handler = FileHandler()

    def read_line_arguments(self):
        parser = argparse.ArgumentParser(description="PDF Downloader Arguments")

        parser.add_argument(
                                "--output_path",
                                required=True,
                                help="Path for the file output"
                            )

        parser.add_argument(
                                "--download_path",
                                required=True,
                                help="Path for the download folder")

        parser.add_argument(
                                "--excel_gri_file_path",
                                required=True,
                                help="Path for the GRI file")

        parser.add_argument(
                                "--metadata_excel_file_path",
                                required=True,
                                help="Path for the metadata file."
                            )

        parser.add_argument(
                                "--download_link_column",
                                required=True,
                                help="Column with links for downloading."
                            )
        parser.add_argument(
                                "--download_link_column_alternative",
                                help="Column with links for downloading if the a link in the first column does not work."
                            )

        self.__args = parser.parse_args()

        self.logger.info("Arguments received: %s", self.__args)

    def start_program(self) -> None:
        self.__file_handler.set_file_path(self.__args.excel_gri_file_path)
        self.__file_handler.load_data()
