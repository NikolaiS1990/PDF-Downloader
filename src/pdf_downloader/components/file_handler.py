"""File Management for PDF Downloader.

This module provides the FileHandler class to manage file path
configuration, safe data loading via pandas with strict column filtering,
exception handling, and structured logging.

Classes:
    FileHandler: Manages loading, validation, and retrieval of data files.

Author:
    Nikolai Sandbeck
"""

from typing import Optional
import logging
import pandas as pd
from openpyxl.utils import column_index_from_string

class FileHandler():
    """Manages loading and parsing of data files for the PDF downloader.

        This class handles file path configuration, safe reading via pandas, 
        and exception and error logging for missing files, permission issues, 
        and schema configurations.

        Attributes:
            __excel_gri_file_path: Internal string storing the target file path.
            __work_dataframe: Internal pandas DataFrame storing the the needed loaded data.
            logger: Logger instance for recording errors, warnings, and success info.

        Usage Example:
            handler = FileHandler()
            handler.set_file_path("data/gri_report.xlsx")
            handler.load_data()
            df = handler.get_file_content()
        """

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__work_dataframe: Optional[pd.DataFrame] = None
        self.__excel_gri_file_path: str = ""
        self.__download_column: str
        self.__download_link_column_alternative: str



    # def set_file_paths(
    #         self,
    #         excel_gri_file_path: str,
    #         metadata_excel_file_path: str
    #     ):

    def set_download_info(
            self,
            excel_gri_file_path: str,
            download_column: str,
            download_link_column_alternative: str

        ) -> None:
        """Temporary setter method."""

        if not isinstance(excel_gri_file_path, str):
            raise ValueError("Error: excel_gri_file_path has to be an string.")

        if not isinstance(download_column, str):
            raise ValueError("Error: excel_gri_file_path has to be an string.")

        if not isinstance(download_link_column_alternative, str):
            raise ValueError("Error: excel_gri_file_path has to be an string.")

        self.__excel_gri_file_path = excel_gri_file_path
        self.__download_column = download_column
        self.__download_link_column_alternative = download_link_column_alternative


    def load_data(
            self,
        ) -> None:
        """Load specific Excel file columns into memory as a pandas DataFrame.

            Reads the Excel spreadsheet configured at ``self.__excel_gri_file_path``
            using openpyxl and extracts target columns corresponding to:
                - Column A: BRnum
                - Column AL: Pdf_URL
                - Column AM: Report Html Address

            If successful, updates ``self.__work_dataframe`` with a data frame which only
            contains the ID column and the column with links + a new column with for download status.
            Handles missing files, permission issues, invalid column configurations,
            missing dependencies, and unexpected runtime exceptions internally by 
            logging errors without re-raising exceptions.

            Raises:
                None: All exceptions (FileNotFoundError, PermissionError, ValueError,
                    ImportError, Exception) are caught internally and logged.
            """

        try:
            # Optional: log that the loading process has started
            self.logger.info("Attempting to load Excel file: %s", self.__excel_gri_file_path)

            df = pd.read_excel(
                self.__excel_gri_file_path,
                engine="openpyxl",
                usecols=(
                    "A,"
                    f"{self.__download_column },"
                    f"{self.__download_link_column_alternative}"
                )
            )

            if df.empty:
                msg = (
                    "File loaded successfully, but "
                    f"contains no data: {self.__excel_gri_file_path}"
                )
                self.logger.warning(msg)
                raise ValueError(msg)


            colum_names = df.columns

            # Check if the ID column and columns with download links
            # has any actual content.
            for column in colum_names[:-1]:
                if df[column].isnull().all():
                    msg = f"Warning: Make sure {column} is not empty"
                    self.logger.warning({msg})
                    raise ValueError(msg)

            df['Download Status'] = None
            self.__work_dataframe = df

            success_msg = (
                f"Successfully loaded {len(self.__work_dataframe)} rows"
                "\t-\t"
                f"The needed columns {colum_names}"
                "\t-\t"
                f"And added the column {df.columns[-1]} "
            )
            self.logger.info(success_msg)
            print(success_msg)

        except FileNotFoundError:
            err_msg = (
                f"Error: The file '{self.__excel_gri_file_path}' "
                "could not be found. Please check the file path."
            )
            self.logger.error(err_msg)
            print(err_msg)

        except PermissionError:
            err_msg = (
                "Error: Permission denied. "
                f"Can't open '{self.__excel_gri_file_path}' right now."
            )
            self.logger.error(err_msg)
            print(err_msg)

        except ValueError as e:
            err_msg = f"Error with sheet or column configuration: {e}"
            self.logger.error(err_msg)
            print(err_msg)

        except ImportError as e:
            err_msg = f"Error: Could not open the sheet: {e}"
            self.logger.error(err_msg)
            print(err_msg)

        except Exception as e:
            err_msg = f"An unexpected error occurred: {e}"
            self.logger.exception(err_msg)
            print(err_msg)


    def get_file_content(self) -> Optional[pd.DataFrame]:
        """Retrieve the loaded Excel file content as a DataFrame.

        Returns:
            Optional[pd.DataFrame]: The loaded pandas DataFrame containing target
            columns if ``load_data()`` was successfully executed; otherwise ``None``.
        """

        if self.__work_dataframe is None:
            print("No data frame found, did you load it?")
            return None

        return self.__work_dataframe
