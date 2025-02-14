import os
from pathlib import Path
from hand_parser import parse
from utils import find_files


def main():
    data_folder = Path(r"C:\Users\Work\Downloads\zips_handhistories-agent-blue-all-dates\2025-02-08")

    output_folder = data_folder.parent / f"{data_folder.name}_converted"
    output_folder.mkdir(exist_ok=True)

    try:
        processed = 0
        for file in find_files(data_folder, "*.html"):
            html_content = file.read_text(encoding="utf-8")
            converted_content = parse(html_content)

            output_filename = f"{file.stem}_converted.txt"
            output_filepath = output_folder / output_filename

            output_filepath.write_text(converted_content, encoding="utf-8")

            print(f"Processed {processed}")
            processed = processed + 1
    except Exception as e:
        print(f"Error parsing file '{file}': {e}")

if __name__ == "__main__":
    main()