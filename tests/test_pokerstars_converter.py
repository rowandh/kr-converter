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

    def test_betslider_raise(self):
        expected = self.read_expected_file("generic_bet.txt")
        content = self.read_test_file("generic_bet.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_multiple_raises(self):
        expected = self.read_expected_file("multiple_raises.txt")
        content = self.read_test_file("multiple_raises.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_flop_multiple_raise_allin(self):
        expected = self.read_expected_file("flop_multiple_raise_allin.txt")
        content = self.read_test_file("flop_multiple_raise_allin.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # HM3
    # Invalid pot size (0.00 vs pot: 53688.00 rake: 2927.00 jpt: 0.00) for hand #15291928620
    # Looks like a weird/unlikely scenario
    def test_pot_size_error_1(self):
        expected = self.read_expected_file("pot_size_error_1.txt")
        content = self.read_test_file("pot_size_error_1.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # HM3
    # Invalid pot size (113640.00 vs pot: 110000.00 rake: 6360.00 jpt: 0.00) for hand #15329534465
    # Looks like a weird/unlikely scenario with a missing player
    def test_pot_size_error_2(self):
        expected = self.read_expected_file("pot_size_error_2.txt")
        content = self.read_test_file("pot_size_error_2.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # HM3
    # Invalid pot size (243470.00 vs pot: 451160.00 rake: 23911.00 jpt: 0.00) for hand #15329522298
    # Looks like a side pot scenario
    def test_pot_size_error_3(self):
        expected = self.read_expected_file("pot_size_error_3.txt")
        content = self.read_test_file("pot_size_error_3.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # HM3
    # Invalid pot size (964151.00 vs pot: 405000.00 rake: 53959.00 jpt: 0.00) for hand #15329520969
    # Turn and river are missing due to using player[0] for community cards. Wrong assumption.
    def test_pot_size_error_4(self):
        expected = self.read_expected_file("pot_size_error_4.txt")
        content = self.read_test_file("pot_size_error_4.html")
        converted = self.parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)