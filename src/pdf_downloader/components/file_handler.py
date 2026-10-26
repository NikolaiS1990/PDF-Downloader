"""File Management for PDF Downloader.

This module provides the FileHandler class to manage file path
configuration, safe data loading via pandas with strict column filtering,
exception handling, and structured logging.

Classes:
    FileHandler: Manages loading, validation, and retrieval of data files.

Author:
    Nikolai Sandbeck
"""

import logging
import pathlib

import pandas as pd


class FileHandler:
    """Manages loading and parsing of data files for the PDF downloader.

    This class handles file path configuration, safe reading via pandas,
    and exception and error logging for missing files, permission issues,
    and schema configurations.

    Attributes:
        __excel_gri_file_path: Internal string storing the target file path.
        __work_dataframe: Internal pandas DataFrame storing the the needed loaded data.
        __logger: Logger instance for recording errors, warnings, and success info.

    Usage Example:
        handler = FileHandler()
        handler.set_file_path("data/gri_report.xlsx")
        handler.load_data()
        df = handler.get_file_content()
    """

    __logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.__work_dataframe: pd.DataFrame | None = None
        self.__excel_gri_file_path: str = ""
        self.__download_link_column: str
        self.__download_link_column_alternative: str

    def set_download_info(
        self,
        excel_gri_file_path: str,
        download_link_column: str,
        download_link_column_alternative: str,
    ) -> None:
        """Configures target file path and Excel download column parameters.

        Validates the input parameters for correct types, non-empty values,
        file existence on disk, and valid Excel file extension (.xlsx or .xls).
        If validation succeeds, updates internal attributes for path and column
        names used during data extraction.

        Args:
            excel_gri_file_path (str): The file path to the target Excel spreadsheet.
            download_link_column (str): Primary column name/letter containing download URLs.
            download_link_column_alternative (str): Alternative column name/letter
                containing backup download URLs.

        Raises:
            TypeError: If any of the provided arguments are not strings.
            ValueError: If ``excel_gri_file_path`` is empty/whitespace or does not end
                with a valid Excel extension (``.xlsx`` or ``.xls``).
            FileNotFoundError: If ``excel_gri_file_path`` does not exist on disk.

        Side Effects:
            - Updates internal instance attributes (`__excel_gri_file_path`,
              `__download_link_column`, and `__download_link_column_alternative`).
            - Emits structured log messages via the class logger (errors on
              validation failure, info on success).
            - Prints success confirmation messages to standard output (`stdout`).
        """

        file_extensions = (".xlsx", ".xls")

        if not isinstance(download_link_column, str):
            error_message = f"Expected a string for download_link_column, got {type(download_link_column)}"
            self.__logger.error(error_message)
            raise TypeError(error_message)

        if not isinstance(download_link_column_alternative, str):
            error_message = f"Expected a string for download_link_column_alternative, got {type(download_link_column_alternative)}"
            self.__logger.error(error_message)
            raise TypeError(error_message)

        if not isinstance(excel_gri_file_path, str):
            error_message = f"Expected a string for a path for an file, got {type(excel_gri_file_path)}"
            self.__logger.error(error_message)
            raise TypeError(error_message)

        if not excel_gri_file_path.strip():
            error_message = (
                f"A path for an excel file must be provided, got {excel_gri_file_path}"
            )
            self.__logger.error(error_message)
            raise ValueError(error_message)

        if not pathlib.Path(excel_gri_file_path).exists():
            error_message = f"Path does not exist: {excel_gri_file_path}."
            self.__logger.error(error_message)
            raise FileNotFoundError(error_message)

        if not excel_gri_file_path.endswith(file_extensions):
            error_message = f"Expected an Excel file, got {excel_gri_file_path}"
            self.__logger.error(error_message)
            raise ValueError(error_message)

        msg = (
            f"Setting file path to: {excel_gri_file_path}, "
            f"Setting primary download column: {download_link_column}, "
            f"Setting alternative download column: {download_link_column_alternative}"
            "was successful."
        )

        print(msg)
        self.__logger.info(msg)

        self.__excel_gri_file_path = excel_gri_file_path
        self.__download_link_column = download_link_column
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
        contains the ID column and the column with links + a new column with for
        download status. Handles missing files, permission issues,
        invalid column configurations, missing dependencies,
        and unexpected runtime exceptions internally by
        logging errors without re-raising exceptions.

        Raises:
            None: All exceptions (FileNotFoundError, PermissionError, ValueError,
                ImportError, Exception) are caught internally and logged.
        """

        try:
            # Optional: log that the loading process has started
            self.__logger.info(
                "Attempting to load Excel file: %s", self.__excel_gri_file_path
            )

            df = pd.read_excel(
                self.__excel_gri_file_path,
                engine="openpyxl",
                usecols=(
                    "A,"
                    f"{self.__download_link_column},"
                    f"{self.__download_link_column_alternative}"
                ),
            )

            if df.empty:
                msg = (
                    "File loaded successfully, but "
                    f"contains no data: {self.__excel_gri_file_path}"
                )
                self.__logger.warning(msg)
                raise ValueError(msg)

            colum_names = df.columns

            # Check if the ID column and columns with download links
            # has any actual content.
            for column in colum_names[:-1]:
                if df[column].isnull().all():
                    msg = f"Warning: Make sure {column} is not empty"
                    self.__logger.warning({msg})
                    raise ValueError(msg)

            df["Download Status"] = None
            self.__work_dataframe = df

            success_msg = (
                f"Successfully loaded {len(self.__work_dataframe)} rows"
                "\t-\t"
                f"The needed columns {colum_names}"
                "\t-\t"
                f"And added the column {df.columns[-1]} "
            )
            self.__logger.info(success_msg)
            print(success_msg)

        except FileNotFoundError:
            err_msg = (
                f"Error: The file '{self.__excel_gri_file_path}' "
                "could not be found. Please check the file path."
            )
            self.__logger.error(err_msg)
            print(err_msg)

        except PermissionError:
            err_msg = (
                "Error: Permission denied. "
                f"Can't open '{self.__excel_gri_file_path}' right now."
            )
            self.__logger.error(err_msg)
            print(err_msg)

        except ValueError as e:
            err_msg = f"Error with sheet or column configuration: {e}"
            self.__logger.error(err_msg)
            print(err_msg)

        except ImportError as e:
            err_msg = f"Error: Could not open the sheet: {e}"
            self.__logger.error(err_msg)
            print(err_msg)

        except Exception as e:
            err_msg = f"An unexpected error occurred: {e}"
            self.__logger.exception(err_msg)
            print(err_msg)

    # def save_updated_spreadsheet(
    #     self,
    #     df: pd.DataFrame,
    #     output_excel_path: str
    #     ) -> None:
    #     """Save the updated DataFrame with statuses to a NEW Excel copy.

    #     Args:
    #         df (pd.DataFrame): The DataFrame with updated status column.
    #         output_excel_path (str): Filepath to save the new Excel spreadsheet copy.
    #     """
    #     try:
    #         df.to_excel(output_excel_path, index=False, engine="openpyxl")
    #         self.__logger.info("Successfully saved updated spreadsheet to: %s", output_excel_path)
    #         print(f"Updated copy saved to: {output_excel_path}")
    #     except Exception as e:
    #         self.__logger.error("Failed to save updated Excel sheet: %s", e)
    #         raise

    def get_file_content(self) -> pd.DataFrame | None:
        """Retrieve the loaded Excel file content as a DataFrame.

        Returns:
            Optional[pd.DataFrame]: The loaded pandas DataFrame containing target
            columns if ``load_data()`` was successfully executed; otherwise ``None``.
        """

        if self.__work_dataframe is None:
            print("No data frame found, did you load it?")
            return None

        return self.__work_dataframe
