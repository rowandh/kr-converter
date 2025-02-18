"""
Ties together the hand history reading with the pokerstars converter
"""
from datetime import datetime

from html_parser import extract_hand_histories_from_html
from models import PokerHand
from pokerstars_converter import PokerStarsConverter

def parse(html_content: str, correct_datetime: datetime = None, currency_symbol = None):
    # Read the hand from HTML
    hand_history_raw: PokerHand = extract_hand_histories_from_html(html_content)

    converter = PokerStarsConverter(currency_symbol)
    # Convert to Pokerstars format
    pokerstars_format = converter.convert_to_pokerstars_format(hand_history_raw, correct_datetime)

    return pokerstars_format