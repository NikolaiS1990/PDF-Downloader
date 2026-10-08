import argparse


class Main:

    def __init__(self):
        self.__args = None

    def read_line_arguments(self):
        parser = argparse.ArgumentParser(description="PDF Downloader Arguments")

        parser.add_argument("--output_path", help="Path for the file output")
        parser.add_argument("--download_path", help="Path for the download folder")
        parser.add_argument("--excel_gri_file_path", help="Path for the GRI file")
        parser.add_argument("--metadata_excel_file_path", help="Path for the meta data file.")

        self.__args = parser.parse_args()

        example = """
        
        ""

        # Fixed: Check each unique argument individually
        if not self.__args.output_path:
            print("Warning: No output path set.")

        if not self.__args.download_path:
            print("Warning: No download folder path set.")

        if not self.__args.excel_gri_file_path:
            print("Warning: No GRI file path set.")

        if not self.__args.metadata_excel_file_path:
            print("Warning: No metadata file path set.")


if __name__ == "__main__":
    mii = Main()
    mii.read_line_arguments()