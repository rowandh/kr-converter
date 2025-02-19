import unittest
from pprint import pprint
from pathlib import Path


from hand_parser import parse
from utils import find_files


class TestActionsParsing(unittest.TestCase):

    def test_parse_error_1(self):
        script_dir = Path(__file__).parent

        file = script_dir / "data" / "parse_error_1.html"

        with open(file, "r", encoding="utf-8") as file:
            html_content = file.read()
            str = parse(html_content)
            pprint(str)

    def test_parse_error_2(self):
        script_dir = Path(__file__).parent

        file = script_dir / "data" / "parseerror2_2025-02-08T20-57-51.html"

        with open(file, "r", encoding="utf-8") as file:
            html_content = file.read()
            str = parse(html_content)
            pprint(str)

    def test_river_reraise(self):
        script_dir = Path(__file__).parent

        file = script_dir / "data" / "bighand.html"

        with open(file, "r", encoding="utf-8") as file:
            html_content = file.read()
            str = parse(html_content)
            pprint(str)

        save = script_dir / "converted" / "bighand_converted.txt"
        with open (save, "w", encoding="utf-8") as file:
            file.write(str)

    def test_convert(self):
        script_dir = Path(__file__).parent

        # Define the path to the "data" subdirectory
        data_folder = Path(r"C:\Users\Work\Downloads\zips_handhistories-agent-blue-all-dates")

        # with open(script_dir / "data" / "flop_hand_ends.html", "r", encoding="utf-8") as file:
        #     html_content = file.read()
        #     str = parse(html_content)
        #     pprint(str)

        processed = 0
        for file in find_files(data_folder, "*.html"):
            with open(file, "r", encoding="utf-8") as file:
                html_content = file.read()
                str = parse(html_content)

                print(f"Processed {processed}")
                processed = processed + 1
                #pprint(str)

if __name__ == '__main__':
    unittest.main()