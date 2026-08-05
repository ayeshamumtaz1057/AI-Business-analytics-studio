"""
Data loading module supporting CSV and Excel files with encoding detection.
"""
import pandas as pd
import io
from typing import Tuple, Optional


def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Reads CSV, XLS, or XLSX uploaded files into a Pandas DataFrame.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        
    Returns:
        Tuple of (DataFrame or None, Error Message or None)
    """
    if uploaded_file is None:
        return None, "No file uploaded."

    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith(".csv"):
            # Attempt default UTF-8 first
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin1")
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="cp1252")
                
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file format. Please upload CSV or Excel files."

        if df.empty:
            return None, "The uploaded file contains no data."

        # Standardize column headers by stripping leading/trailing whitespace
        df.columns = [str(col).strip() for col in df.columns]
        
        return df, None

    except Exception as e:
        return None, f"Error parsing file: {str(e)}"
