from datetime import datetime
from pathlib import Path

import pytz
import re
import os
import fnmatch

def convert_korean_datetime_with_timezone(datetime_str):
    """
    Converts a Korean-formatted datetime string (Asia/Seoul) to UTC-based output with timezone.

    Parameters:
        datetime_str (str): The datetime string in the format 'YYYY-MM-DD 오전/오후 HH:MM:SS'.

    Returns:
        str: The formatted datetime string in 'YYYY/MM/DD HH:MM:SS ZZZ' with timezone.
    """
    # Replace Korean AM/PM indicators
    datetime_str = re.sub(r"오전", "AM", datetime_str)
    datetime_str = re.sub(r"오후", "PM", datetime_str)
    dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %p %I:%M:%S")

    return format_korean_date(dt_obj)

def format_korean_date(dt_obj: datetime):
    # Parse the datetime in Korea Standard Time (KST)
    kst = pytz.timezone("Asia/Seoul")
    dt_kst = kst.localize(dt_obj)  # Localize to KST

    # Format output in 'YYYY/MM/DD HH:MM:SS ZZZ' (e.g., 2025/02/08 00:00:00 KST)
    return dt_kst.strftime("%Y/%m/%d %H:%M:%S %Z")

def find_files(directory, pattern="*.html"):
    directory = Path(directory)
    for root, _, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            yield Path(root) / filename


def extract_datetime_from_filename(filename: Path):
    """
    Extracts the ISO-formatted datetime from a filename.
    Supports both string and Path objects.

    Parameters:
        filename (str or Path): The filename containing the datetime stamp.

    Returns:
        datetime: A datetime object representing the extracted timestamp.
    """
    filename = filename.stem  # Ensure it's a Path object and remove the extension

    try:
        # Extract the last part after '_', which contains the ISO datetime
        datetime_part = filename.split("_")[-1]

        # Directly parse the datetime
        return datetime.strptime(datetime_part, "%Y-%m-%dT%H-%M-%S")

    except ValueError:
        return None  # Return None if parsing fails
