from typing import Optional
import pandas as pd
import logging

class FileHandler():

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__file_content: Optional[pd.DataFrame] = None
        self.__excel_gri_file_path: str = ""
        self.__metadata_excel_file_path: str = ""

    # def set_file_paths(
    #         self,
    #         excel_gri_file_path: str,
    #         metadata_excel_file_path: str
    #     ):

    def set_file_path(self, excel_gri_file_path: str) -> None:
        # Temporary setter method.

        if not isinstance(excel_gri_file_path, str):
            raise ValueError("Error: excel_gri_file_path has to be an string.")

        self.__excel_gri_file_path = excel_gri_file_path


    def load_data(self) -> None:
        # Selected columns mapping:
        # A  -> BRnum
        # AL -> Pdf_URL
        # AM -> Report Html Address
        # AP -> New download report status

        try:
            # Optional: log that the loading process has started
            self.logger.info("Attempting to load Excel file: %s", self.__excel_gri_file_path)

            df = pd.read_excel(
                self.__excel_gri_file_path,
                engine="openpyxl",
                usecols="A, AL, AM, AP"
            )

            if df.empty:
                msg = f"File loaded successfully, but contains no data: {self.__excel_gri_file_path}"
                self.logger.warning(msg)
                print(f"Warning: {msg}")
                return

            self.__file_content = df
            success_msg = f"Successfully loaded {len(self.__file_content)} rows and {len(self.__file_content.columns)} columns."
            self.logger.info(success_msg)
            print(success_msg)

        except FileNotFoundError:
            err_msg = f"Error: The file '{self.__excel_gri_file_path}' could not be found. Please check the file path."
            self.logger.error(err_msg)
            print(err_msg)

        except PermissionError:
            err_msg = f"Error: Permission denied. Can't open '{self.__excel_gri_file_path}' right now."
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
            if self.__file_content is None:
                print("No data frame found, did you load it?")
                return None

            return self.__file_content





