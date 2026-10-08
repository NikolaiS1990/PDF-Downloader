import pandas as pandas

class FileHandler():

    def __init__(self):
        self.__file_content: dict = {}
        self.__excel_gri_file_path: str = ""
        self.__metadata_excel_file_path: str = ""

    def set_file_paths(
            self,
            excel_gri_file_path: str,
            metadata_excel_file_path: str
        ):
       
       excel_gri_file_path

