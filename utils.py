from datetime import datetime
import pytz
import re

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

    # Parse the datetime in Korea Standard Time (KST)
    kst = pytz.timezone("Asia/Seoul")
    dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %p %I:%M:%S")
    dt_kst = kst.localize(dt_obj)  # Localize to KST

    # Format output in 'YYYY/MM/DD HH:MM:SS ZZZ' (e.g., 2025/02/08 00:00:00 KST)
    return dt_kst.strftime("%Y/%m/%d %H:%M:%S %Z")