import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

def save_json_data(data: Dict[str, Any], filename: str) -> str:
    """
    Save JSON data to a file for future reference or verification.
    
    Args:
        data: Dictionary data to save
        filename: Base name for the file (without extension)
    
    Returns:
        Path to the saved JSON file
    """
    # Create directory for JSON data if it doesn't exist
    json_dir = os.path.join("temp", "json_data")
    os.makedirs(json_dir, exist_ok=True)
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(json_dir, f"{filename}_{timestamp}.json")
    
    # Save the data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path

def load_json_data(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary with the loaded data or None if loading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON data: {str(e)}")
        return None

def calculate_total_quantity(wastes: list) -> float:
    """
    Calculate the total quantity of waste from a list of waste items.
    
    Args:
        wastes: List of waste items, each with a 'quantity' field
    
    Returns:
        Total quantity as a float
    """
    try:
        return sum(float(waste.get('quantity', 0)) for waste in wastes)
    except (ValueError, TypeError):
        return 0.0

def format_date(date_str: str, input_format: str = "%Y-%m-%d", output_format: str = "%d.%m.%Y") -> str:
    """
    Format a date string from one format to another.
    
    Args:
        date_str: Date string to format
        input_format: Format of the input date string
        output_format: Desired format for the output date string
    
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str
