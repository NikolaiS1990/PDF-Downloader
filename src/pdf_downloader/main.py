"""Main module for the PDF Downloader application.

This module handles the initialization of the application..

Class:
    Main: The main controller class for the PDF Downloader.

Author:
    Nikolai Sandbeck
"""

import argparse
import logging

class Main:

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__args = None
        self.logger.info("PDF Downloader initialized.")

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

        self.__args = parser.parse_args()

        self.logger.info("Arguments received: %s", self.__args)
