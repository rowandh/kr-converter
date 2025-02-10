# Parses the Korean HH to a normalized structure
from argparse import Action
from typing import List, Dict, Any

from models import ParsedHandHistory, StartEntry, HistoryLine, PlayerEntry, AnteEntry, CommunityCardsEntry, ActionEntry


def parse_hand_history(hand_history: str) -> ParsedHandHistory:
    """
    Parses a poker hand history line by line into structured data.
    Each line is categorized into a type and stored with relevant details.

    Returns:
    - A list of dictionaries where each dictionary represents one line of the hand history.
    """
    lines = hand_history.strip().split("\n")
    parsed_lines: ParsedHandHistory = []

    for line in lines:
        parsed_line: HistoryLine | None = None

        # 시작 (Start of the hand): Contains hand metadata like StageNo, Credit, Blinds
        if "시작 :" in line:
            parsed_line = StartEntry()
            parts = line.replace("[", "").replace("]", "").split()
            for part in parts:
                if "StageNo:" in part:
                    parsed_line.stage_number = part.split("StageNo:")[1]
                elif "Credit:" in part:
                    parsed_line.credit = int(part.split("Credit:")[1].replace(",", "").replace("원", ""))
                elif "SB:" in part:
                    parsed_line.sb = int(part.split("SB:")[1].replace(",", "").replace("원", ""))
                elif "BB:" in part:
                    parsed_line.bb = int(part.split("BB:")[1].replace(",", "").replace("원", ""))
                elif "MBI:" in part:
                    parsed_line.mbi = int(part.split("MBI:")[1].replace(",", "").replace("원", ""))
                elif "CBIR:" in part:
                    parsed_line.cbir = int(part.split("CBIR:")[1].replace(",", "").replace("원", ""))

        # NICKNAME (플레이어 이름): Identifies the player
        elif "NICKNAME:[" in line:
            parsed_line = PlayerEntry()
            start = line.find("[") + 1
            end = line.find("]", start)
            parsed_line.nickname = line[start:end]

        elif "앤티:" in line:
            parsed_line = AnteEntry()

            # Remove "* 앤티:" and split by spaces, handling multiple spaces
            parts = line.replace("* 앤티:", "").strip().split("원")

            # Extract ante amount (removing '-', commas, and '원')
            ante_amount = int(parts[0].replace("원", "").replace(",", "").replace("-", ""))

            # Extract remaining stack (removing parentheses, commas, and '원')
            remaining_stack = int(parts[1].strip("()").replace(",", "").replace("원", ""))

            parsed_line.amount = ante_amount
            parsed_line.remaining_stack = remaining_stack

        # 홀 카드딜 (Hole Cards Deal): Player's starting hand
        # elif "홀 카드딜:" in line:
        #     parsed_line["type"] = "HOLE_CARDS"
        #     parts = line.split(": ")[1].split(" ")
        #     # Don't set the hole cards here
        #     # parsed_line["hole_cards"] = parts[:2]

        # 커뮤니티 카드 딜 (Community Card Deal): The board cards for each street
        elif "커뮤니티 카드 딜:" in line:
            parsed_line = CommunityCardsEntry()
            h_start = line.index("H(") + 2
            h_end = line.index(")", h_start)
            hole_cards_section = line[h_start:h_end]
            # Change 10 to T
            hole_cards_section = hole_cards_section.replace("10", "T")
            parsed_line.hole_cards = [hole_cards_section[i:i + 2] for i in range(0, len(hole_cards_section), 2)]

            # Step 2: Extract community cards after "C "
            c_start = line.index("C (") + 2  # Start after "C ("
            c_section = line[c_start:]  # Get everything after "C "
            # Change 10 to T
            c_section = c_section.replace("10", "T")

            # Step 3: Split community cards while keeping empty streets
            c_groups = c_section.split(") (")  # Split at street boundaries

            c_groups = [group.replace("(", "").replace(")", "").strip() for group in c_groups]  # Clean up
            cc = [[group[i:i + 2] for i in range(0, len(group), 2)] if group else [] for group in c_groups]
            parsed_line.community_cards = cc

        # 베팅 (Betting Action): Player actions (call, check, fold, raise)
        elif "베팅:" in line:
            parsed_line = _parse_betting_action(line)

        if parsed_line is not None:
            parsed_lines.append(parsed_line)

    return parsed_lines

def _parse_betting_action(line: str) -> ActionEntry:
    """
    Parses a poker betting action line into a structured dictionary.

    Handles:
    - Folds (다이)
    - Checks (체크)
    - Calls (콜)
    - Blinds (블라인드:BIG, 블라인드:SMALL)

    Example input:
    * 베팅: 콜 -1,000원(254,674원) - 베팅순서: [0][3] [2531ms]

    Returns:
    {
        "type": "ACTION",
        "action": "콜",
        "amount": 1000,
        "remaining_stack": 254674,
        "betting_round": 0,
        "betting_position": 3,
        "time_taken_ms": 2531
    }
    """

    bet_amount = _parse_bet_amount(line)
    parsed_line = ActionEntry()
    parsed_line.action = bet_amount["action"]
    parsed_line.amount = bet_amount["amount"]
    parsed_line.is_blind = bet_amount["is_blind"]

    # Extract remaining stack from parentheses "(xxx,xxx원)"
    remaining_stack = None
    if "(" in line and "원" in line:
        stack_start = line.find("(") + 1
        stack_end = line.find("원", stack_start)
        remaining_stack = int(line[stack_start:stack_end].replace(",", "").strip())
    parsed_line.remaining_stack = remaining_stack

    # Extract betting round and position from "베팅순서: [0][3]"
    betting_round, betting_position = None, None
    if "베팅순서:" in line:
        order_start = line.find("베팅순서: [") + len("베팅순서: [")
        order_end = line.find("]", order_start)

        order2_start = line.find("[", order_end) + 1
        order2_end = line.find("]", order2_start)
        try:
            betting_position = int(line[order2_start:order2_end])
        except ValueError:
            betting_position = None

        try:
            betting_round = int(line[order_start:order_end])
        except ValueError:
            betting_round = None

    parsed_line.betting_position = betting_position
    parsed_line.betting_round = betting_round

    # Extract time taken in milliseconds [xxxxms]
    time_taken = None
    if "[" in line and "ms]" in line:
        try:
            time_start = line.rfind("[") + 1
            time_end = line.find("ms]", time_start)
            time_taken = int(line[time_start:time_end].strip()) if time_start < time_end else None
        except ValueError:
            time_taken = None
    parsed_line.time_taken_ms = time_taken

    return parsed_line

def _parse_bet_amount(line: str) -> Dict[str, Any]:
    """
    Extracts the bet amount from a poker betting action line.

    Handles:
    - Regular bets (Call, Check, Fold, Raise)
    - Small Blind & Big Blind postings

    Returns:
    {
        "action": "콜",
        "amount": 1000,
        "is_blind": False
    }
    """
    parsed_data = {"action": None, "amount": None, "is_blind": False}

    # Remove "* 베팅:" at the start
    line = line.replace("* 베팅:", "").strip()

    # Check if it's a blind posting (Small Blind / Big Blind)
    if "블라인드:SMALL" in line or "블라인드:BIG" in line:
        parsed_data["is_blind"] = True
        parsed_data["action"] = "블라인드:SMALL" if "블라인드:SMALL" in line else "블라인드:BIG"

        # Extract blind bet amount
        if "금액:" in line:
            start = line.find("금액:") + 3
            end = line.find("원", start)
            blind_amount = line[start:end].replace(",", "").strip()
            parsed_data["amount"] = int(blind_amount) if blind_amount.isdigit() else None

        if "[Creadit:" in line:
            stack_start = line.find("[Creadit:") + len("[Creadit:")
            stack_end = line.find("원", stack_start)
            remaining_stack = int(line[stack_start:stack_end].replace(",", "").strip())
            parsed_data["remaining_stack"] = remaining_stack

    else:
        # Extract betting action (콜, 다이, 체크, 풀)
        parts = line.split()
        parsed_data["action"] = parts[0]  # First word is the action (e.g., "콜", "다이", "체크", "풀")

        # Find the first "원" outside of parentheses (bet amount)
        first_won_index = line.find("원")
        first_paren_index = line.find("(")

        # If "원" exists AND it's before "(", it's a bet amount
        if first_won_index != -1 and (first_paren_index == -1 or first_won_index < first_paren_index):
            bet_amount_str = line[:first_won_index].split()[-1].replace(",", "").replace("-", "").strip()
            parsed_data["amount"] = int(bet_amount_str) if bet_amount_str.isdigit() else None

    return parsed_data