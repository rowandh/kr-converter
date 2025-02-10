import unittest
from pprint import pprint
from pathlib import Path

from hand_parser import parse

class TestActionsParsing(unittest.TestCase):
    def test_convert(self):
        script_dir = Path(__file__).parent

        # Define the path to the "data" subdirectory
        data_folder = script_dir / "data"

        files = [f for f in data_folder.iterdir() if f.is_file()]

        for file in files:
            with open(file, "r", encoding="utf-8") as file:
                html_content = file.read()
                str = parse(html_content)
                pprint(str)

if __name__ == '__main__':
    unittest.main()