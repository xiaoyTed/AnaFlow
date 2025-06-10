# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import pandas as pd
import os
from typing import Annotated
from langchain_core.tools import tool
from .decorators import log_io

@tool
@log_io
def csv_loader_tool(
    file_path: Annotated[str, "The path to the local CSV file or directory to load. If directory, will load the first CSV file found."] = "./local_data"
):
    """Load a local CSV file and return the first 5 rows as a markdown table plus basic statistics. Useful for data analysis and previewing tabular data."""
    try:
        # If file_path is a directory, find CSV files in it
        if os.path.isdir(file_path):
            csv_files = [f for f in os.listdir(file_path) if f.endswith('.csv')]
            if len(csv_files) == 0:
                return "No CSV files found in the specified directory."
            # Use the first CSV file found
            actual_file_path = os.path.join(file_path, csv_files[0])
            file_info = f"Found {len(csv_files)} CSV file(s). Loading: {csv_files[0]}\n\n"
        else:
            actual_file_path = file_path
            file_info = f"Loading file: {os.path.basename(file_path)}\n\n"
        
        # Load the CSV file
        df = pd.read_csv(actual_file_path, encoding="gbk")
        
        # Generate summary information
        summary = f"{file_info}"
        summary += f"**Dataset Overview:**\n"
        summary += f"- Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        summary += f"- Columns: {', '.join(df.columns.tolist())}\n\n"
        
        # Add data types info
        summary += f"**Data Types:**\n"
        for col, dtype in df.dtypes.items():
            summary += f"- {col}: {dtype}\n"
        summary += "\n"
        
        # Add first 5 rows as markdown table
        summary += f"**First 5 Rows:**\n"
        summary += df.head().to_markdown(index=False)
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += f"\n\n**Basic Statistics (Numeric Columns):**\n"
            summary += df[numeric_cols].describe().to_markdown()
        
        return summary
        
    except Exception as e:
        return f"Error loading CSV file: {e}"

def list_subfolder_files(folder_path: Annotated[str, "The path to the local folder to list files."] = "./local_data"):
    """List all CSV files in a local folder."""
    try:
        if not os.path.exists(folder_path):
            return f"Directory {folder_path} does not exist."
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and os.path.isfile(os.path.join(folder_path, f))]
        return csv_files
    except Exception as e:
        return f"Error listing files: {e}"
