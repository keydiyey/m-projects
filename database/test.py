import sqlite3
import pandas as pd
from openpyxl import Workbook, load_workbook

def open_file(excel_file):
    # Load the workbook and select the active worksheet
    wb = load_workbook(excel_file)
    ws = wb.active
    
    # Read the data into a pandas DataFrame
    data = ws.values
    columns = next(data)[0:]  # Get the first row as column names
    df = pd.DataFrame(data, columns=columns)
    
    return df

def clean(excel_file:Workbook,worksheet:str="Sheet1", profiler:str="kic"):
    # Remove rows with missing values
    df_cleaned = excel_file[worksheet]
    
    # Save the cleaned DataFrame back to an Excel file
    cleaned_file = "cleaned_" + excel_file
    df_cleaned.to_excel(cleaned_file, index=False)
    
    return cleaned_file
