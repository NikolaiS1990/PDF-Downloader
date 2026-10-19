from unittest.mock import patch
import pandas as pd
from pdf_downloader.components.file_handler import FileHandler


@patch.object(FileHandler, "logger")
@patch("pandas.read_excel")
def test_load_data(mock_read_excel, mock_logger_instance):
    """Test successful loading without caring about the underlying file path string."""
    
    # 1. Arrange: Provide a valid mock DataFrame
    mock_df = pd.DataFrame({
        "A": ["BR50041", "BR50042"],
        "AL": ["url1", "url2"],
        "AM": ["url1", "url2"],
        "AP": ["", ""]
    })
    mock_read_excel.return_value = mock_df

    file_handler = FileHandler()
    
    # Pass a clean test path right into the setter
    test_path = "data/test_gri_file.xlsx"
    file_handler.set_file_path(test_path)

    file_handler.load_data()

    # 3. Assert: Verify the getter retrieves the loaded mock data properly
    loaded_df = file_handler.get_file_content()
    assert loaded_df is not None
    assert len(loaded_df) == 2

    # 4. Assert: ANY means "we don't care what path string was passed, 
    # as long as openpyxl and the correct columns were used!"
    mock_read_excel.assert_called_once_with(
        test_path, 
        engine="openpyxl", 
        usecols="A, AL, AM, AP"
    )
    
    # 5. Assert: Verify logging happened
    assert mock_logger_instance.info.called