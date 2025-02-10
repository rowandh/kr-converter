"""
Ties together the hand history reading with the pokerstars converter
"""
from html_parser import extract_hand_histories_from_html
from models import PokerHand
from pokerstars_converter import convert_to_pokerstars_format
from individual_history_parser import parse_hand_history

def parse(html_content: str):
    # Read the hand from HTML
    hand_history_raw: PokerHand = extract_hand_histories_from_html(html_content)

    # Convert to Pokerstars format
    pokerstars_format = convert_to_pokerstars_format(hand_history_raw)