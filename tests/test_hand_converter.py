import unittest
from pprint import pprint
from pathlib import Path

from hand_parser import parse

class TestActionsParsing(unittest.TestCase):
    def test_convert(self):
        script_dir = Path(__file__).parent

        # Define the path to the "data" subdirectory
        data_folder = script_dir / "data"

        target_file = data_folder / "river-9way-bet-call.html"

        with target_file.open("r", encoding="utf-8") as file:
            html_content = file.read()
            str = parse(html_content)
            pprint(str)

if __name__ == '__main__':
    unittest.main()