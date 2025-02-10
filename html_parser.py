from bs4 import BeautifulSoup
from typing import List, Any

import individual_history_parser
from individual_history_parser import parse_hand_history

from models import PlayerAction, PokerHand


def extract_hand_histories_from_html(html_content: str) -> PokerHand | None:
    """
    Extracts structured poker hand history metadata from an HTML file.

    Returns:
    - A list of RawPokerHand objects.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Locate the main table that contains hand histories
    table_area = soup.find("div", class_="table-area")
    if table_area:
        hand_history_table = table_area.find("table")
    else:
        hand_history_table = None

    # Extract all rows from the table (excluding the header row)
    hand_history_rows = hand_history_table.find_all("tr") if hand_history_table else []
    row = hand_history_rows[1] if len(hand_history_rows) > 1 else None

    if (row is None):
        return None
    columns = row.find_all("td")
    if row is None or len(columns) < 6:  # Ensure we have the correct number of columns
        return None

    hand_data = PokerHand(
        round_id=columns[0].text.strip(), # 라운드ID
        timestamp=columns[1].text.strip(), # 시각
        game_type=columns[2].text.strip(), # 게임 종류 (e.g., 홀덤)
        winner=columns[3].text.strip(), # 승자(족보)
        winning_amount=columns[4].text.strip().replace(",", ""), # 이긴금액
        players=parse_detailed_info(str(columns[5]))  # Pass nested HTML for parsing
    )

    return hand_data

def parse_detailed_info(detailed_info_html: str) -> List[PlayerAction]:
    """
    Parses the nested table inside the 'detailed_info' column.

    Returns:
    - A list of RawPlayerAction objects for each player in the hand.
    """
    soup = BeautifulSoup(detailed_info_html, "html.parser")

    # Find the nested table inside detailed_info
    nested_table = soup.find("table")
    if not nested_table:
        return []

    parsed_players = []

    # Extract rows from the nested table
    rows = nested_table.find_all("tr")

    for row in rows[1:]:  # Skip the header row
        columns = row.find_all("td")
        if len(columns) < 4:  # Ensure correct number of columns
            continue

        betting_action = columns[1].text.strip()

        # This might not belong here but it's easier if it can stay here
        parsed_betting_action = individual_history_parser.parse_hand_history(betting_action)

        player_data = PlayerAction(
            player=columns[0].text.strip(), # 참가자 Player name
            raw_betting_action=betting_action, # 족보 Betting action
            amount_won_lost=columns[2].text.strip().replace(",", ""), # 변동 금액 Won/lost
            final_stack=columns[3].text.strip().replace(",", ""), # 남은 잔액 Final stack size
            betting_actions=parsed_betting_action
        )

        parsed_players.append(player_data)

    return parsed_players
