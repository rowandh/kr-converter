# Full HTML Parser to Extract Poker Hand Histories

from bs4 import BeautifulSoup
from typing import List, Dict, Any

def extract_hand_histories_from_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Extracts structured poker hand history metadata from an HTML file.

    Returns:
    - A list of dictionaries where each item contains metadata about a poker hand.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Locate the main table that contains hand histories
    table_area = soup.find("div", class_="table-area")
    if table_area:
        hand_history_table = table_area.find("table")
    else:
        hand_history_table = None

    # Extract all rows from the table (excluding the header row)
    hand_history_rows = hand_history_table.find_all("tr")[1:] if hand_history_table else []

    hand_histories = []

    for row in hand_history_rows:
        columns = row.find_all("td")

        if len(columns) < 6:  # Ensure we have the correct number of columns
            continue

        hand_data = {
            "round_id": columns[0].text.strip(),  # 라운드ID
            "timestamp": columns[1].text.strip(),  # 시각
            "game_type": columns[2].text.strip(),  # 게임 종류 (e.g., 홀덤)
            "winner": columns[3].text.strip(),  # 승자(족보)
            "winning_amount": columns[4].text.strip(),  # 이긴금액
            "detailed_info": parse_detailed_info(str(columns[5]))  # Pass nested HTML for parsing
        }

        hand_histories.append(hand_data)

    return hand_histories

def parse_detailed_info(detailed_info_html: str) -> List[Dict[str, Any]]:
    """
    Parses the nested table inside the 'detailed_info' column.

    Extracts:
    - Player names
    - Hand rankings
    - Betting actions
    - Final stack sizes

    Returns:
    - A list of structured player actions for a given hand.
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

        player_data = {
            "player": columns[0].text.strip(),  # 참가자 Player name
            "betting_action": columns[1].text.strip(),  # 족보 Betting action
            "amount_won_lost": columns[2].text.strip(),  # 변동 금액 Won/lost
            "final_stack": columns[3].text.strip()  # 남은 잔액 Final stack size
        }

        parsed_players.append(player_data)

    return parsed_players
