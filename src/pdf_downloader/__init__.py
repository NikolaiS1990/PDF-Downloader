"""PDF Downloader Application Entry Point.

This module serves as the entry point for the PDF Downloader application.
It handles logging configuration and initializes the Main controller class.

Functions:
    setup_logging(): Configures the logging system with timestamped log files.
    main(): Entry point function that sets up logging and runs the application.

Author:
    Nikolai Sandbeck
"""

from datetime import datetime
import logging
import pathlib
from pdf_downloader.main import Main

def setup_logging():
    """Configure the application logging system.

    Creates a 'logs' directory if it does not exist and configures
    the root logger to write to a timestamped log file (e.g., app_2023-10-27_10-00-00.log).
    
    The log format includes timestamp, logger name, level, and message.
    """

    log_dir = pathlib.Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = log_dir / f"app_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=str(log_file_path),
        force=True
    )

def main() -> None:
    """Entry point for the PDF Downloader application.
    Initializes the logging system and starts the Main controller class
    to handle argument parsing and application logic.
    """

    setup_logging()
    run_app = Main()
    run_app.read_line_arguments()

if __name__ == "__main__":
    main()
