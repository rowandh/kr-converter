import os
from pathlib import Path

import constants
from hand_parser import parse
from utils import find_files, extract_datetime_from_filename


def main():
    data_folder = Path(r"C:\Users\Work\Documents\Source\kr-converter\tests\data")

    output_folder = data_folder.parent / f"{data_folder.name}_converted"
    output_folder.mkdir(exist_ok=True)

    processed = 0
    for file in find_files(data_folder, "*.html"):
        try:
            html_content = file.read_text(encoding="utf-8")

            corrected_timestamp = extract_datetime_from_filename(file)
            converted_content = parse(html_content, corrected_timestamp, "$")

            output_filename = f"{file.stem}_converted.txt"
            output_filepath = output_folder / output_filename

            output_filepath.write_text(converted_content, encoding="utf-8")

            processed = processed + 1

        except Exception as e:
            print(f"Error parsing file '{file}': {e}")


    print(f"Processed {processed}")

if __name__ == "__main__":
    main()