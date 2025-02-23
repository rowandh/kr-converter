import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import islice

import constants
from hand_parser import parse
from utils import find_files, extract_datetime_from_filename

def process_file(file, data_folder, output_folder):
    try:
        html_content = file.read_text(encoding="utf-8")
        corrected_timestamp = extract_datetime_from_filename(file)
        converted_content = parse(html_content, corrected_timestamp, "$")

        # Create subdirectories relative to data_folder
        relative_path = file.relative_to(data_folder)
        output_filepath = output_folder / relative_path
        output_filepath = output_filepath.with_suffix(".txt")

        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        output_filepath.write_text(converted_content, encoding="utf-8")

        return 1
    except Exception as e:
        print(f"Error parsing file '{file}': {e}")
        return 0

def chunked_iterable(iterable, size):
    """Yield successive chunks of a given size from an iterable."""
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <data_folder>")
        sys.exit(1)

    data_folder = Path(sys.argv[1])
    output_folder = data_folder.parent / f"{data_folder.name}_converted"

    max_workers = min(4, os.cpu_count() or 1)
    processed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        try:
            for chunk in chunked_iterable(find_files(data_folder, "*.html"), max_workers):
                futures = [executor.submit(process_file, file, data_folder, output_folder) for file in chunk]
                for future in as_completed(futures):
                    processed += future.result()

        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
            executor.shutdown(wait=False, cancel_futures=True)

    print(f"Processed {processed}")

if __name__ == "__main__":
    main()
