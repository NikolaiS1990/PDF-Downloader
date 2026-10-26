import logging
import pandas as pd
import pathlib
from pdf_downloader.components.sub_components.file_handler_reader_comps import FileReaderFactory

class FileHandler():

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__gri_file_content: list[dict] = []
        self.__metadata_file_content: list[dict] = []
        self.__output_path: str = ""
        self.__gri_file_path: str = ""
        self.__metadata_file_path: str = ""
        self.logger.info("FileHandler initialized.")

    def set_file_paths(
            self,
            output_path: str,
            gri_file_path: str,
            metadata_file_path: str
        ):

        file_extensions = (".xlsx", ".xls", ".csv")

        file_paths = [
                        gri_file_path,
                        metadata_file_path]

        dir_paths = [output_path]

        paths = file_paths + dir_paths

        for path in paths:
            if not isinstance(path, str):
                error_message = f"Expected a string for path, got {type(path)}"
                self.logger.error(error_message)
                raise TypeError(error_message)

            if not path.strip():
                error_message = f"A path must be provided, got {path}"
                self.logger.error(error_message)
                raise ValueError(error_message)

            if not pathlib.Path(path).exists():
                error_message = f"Path does not exist: {path}. If it is a file, please ensure it exists. If it is a directory, please create it."
                self.logger.error(error_message)
                raise FileNotFoundError(error_message)

        for file_path in file_paths:
            if not file_path.endswith(file_extensions):
                error_message = f"Expected an Excel or CSV file, got {file_path}"
                self.logger.error(error_message)
                raise ValueError(error_message)

        self.__output_path = output_path
        self.__gri_file_path = gri_file_path
        self.__metadata_file_path = metadata_file_path
        self.logger.info("File paths set successfully.")


    def read_excel_files(self) -> None:
            """Read both the GRI and metadata files using FileReaderFactory."""

            try:
                # 1. Get the correct reader for the GRI file and read it
                gri_reader = FileReaderFactory.get_file_reader(self.__gri_file_path)
                self.__gri_file_content = gri_reader.read(self.__gri_file_path)

                # 2. Get the correct reader for the metadata file and read it
                metadata_reader = FileReaderFactory.get_file_reader(self.__metadata_file_path)
                self.__metadata_file_content = metadata_reader.read(self.__metadata_file_path)

                self.logger.info("Both files read successfully.")
            except Exception as e:
                self.logger.error(f"Error reading files: {e}")
                raise

    def get_gri_file_content(self) -> list[dict]:
        """Return the content of the GRI file."""
        return self.__gri_file_content

    def get_metadata_file_content(self) -> list[dict]:
        """Return the content of the metadata file."""
        return self.__metadata_file_content

    def get_set_paths(self) -> tuple[str, str, str]:
        """Return the set paths for output, GRI file, and metadata file."""
        return self.__output_path, self.__gri_file_path, self.__metadata_file_path
