import unittest
from datetime import datetime
from pprint import pprint
from pathlib import Path

from hand_parser import parse

class TestPokerstarsConverter(unittest.TestCase):

    def read_test_file(self, name):
        return self.read_file("data", name)

    def read_expected_file(self, name):
        return self.read_file("expected", name)

    def read_file(self, dir_name, name):
        script_dir = Path(__file__).parent
        with open(script_dir / dir_name / name, "r", encoding="utf-8") as file:
            html_content = file.read()
            return html_content

    def parse(self, content, correct_datetime = None):
        return parse(content, correct_datetime, currency_symbol="$")

    def test_smallhand(self):
        expected = self.read_expected_file("smallhand.txt")
        content = self.read_test_file("smallhand.html")
        converted = self.parse(content)

        pprint(converted)
        self.assertEqual(converted, expected)

    def test_river_9way_bet_call_with_corrected_date(self):
        expected = self.read_expected_file("river-9way-bet-call.txt")

        content = self.read_test_file("river-9way-bet-call.html")

        correct_datetime = datetime(2024, 11,30, 13, 34, 46)
        converted = self.parse(content, correct_datetime)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_all_in_pre(self):
        expected = self.read_expected_file("all_in_pre.txt")

        content = self.read_test_file("all_in_pre.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_parse_error1(self):
        expected = self.read_expected_file("parse_error_1.txt")

        content = self.read_test_file("parse_error_1.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # Scenario where HU and a player leaves before betting
    def test_parse_error2(self):
        expected = self.read_expected_file("parseerror2_2025-02-08T20-57-51.txt")

        content = self.read_test_file("parseerror2_2025-02-08T20-57-51.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_all_in(self):
        expected = self.read_expected_file("all_in.txt")
        content = self.read_test_file("all_in.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_bighand(self):
        expected = self.read_expected_file("bighand.txt")
        content = self.read_test_file("bighand.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_multiple_entryfees(self):
        expected = self.read_expected_file("multiple_entryfees.txt")
        content = self.read_test_file("multiple_entryfees.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)