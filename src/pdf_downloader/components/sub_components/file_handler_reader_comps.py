import logging
import pandas as pd

class ExcelFileReader:
    """Concrete implementation for Excel files."""
    
    logger = logging.getLogger(__name__)

    def read(self, file_path: str) -> list[dict]:
        self.logger.info(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        return df.to_dict(orient="records")

class CsvFileReader:
    """Concrete implementation for CSV files."""
    
    logger = logging.getLogger(__name__)

    def read(self, file_path: str) -> list[dict]:
        self.logger.info(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")

class FileReaderFactory:
    @staticmethod
    def get_file_reader(file_path: str):
        """Factory method to get the appropriate file reader."""
        if file_path.endswith((".xlsx", ".xls")):
            return ExcelFileReader()
        elif file_path.endswith(".csv"):
            return CsvFileReader()
        else:
            error_message = f"Unsupported file extension for file: {file_path}"
            logging.error(error_message)
            raise ValueError(error_message)