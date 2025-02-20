# Parses the Korean HH to a normalized structure
import re
from tkinter.messagebox import showinfo

import constants
from constants import BetType, ALL_IN, CHECK, RAISE, CALL, FOLD, BIG_BLIND, SMALL_BLIND, QUARTER_POT, HALF_POT, \
    FULL_POT, \
    MoneyUnit, GENERIC
from models import ParsedHandHistory, StartEntry, HistoryLine, PlayerEntry, AnteEntry, CommunityCardsEntry, ActionEntry, \
    PostBlindEntry, ResultsEntry, HoleCardsEntry, EntryFeeEntry, WinMoneyEntry
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def parse_hand_history(hand_history: str) -> ParsedHandHistory:
    """
    Parses a poker hand history line by line into structured data.
    Each line is categorized into a type and stored with relevant details.

    Returns:
    - A list of dictionaries where each dictionary represents one line of the hand history.
    """

    # Fixes an issue where MS are on a newline
    lines = hand_history.strip().split("\n")
    last_action = None

    parsed_lines: ParsedHandHistory = []
    win_money_line: WinMoneyEntry = None

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
                    parsed_line.credit = parse_chips("Credit:", part)
                elif "SB:" in part:
                    parsed_line.sb = parse_chips("SB:", part)
                elif "BB:" in part:
                    parsed_line.bb = parse_chips("BB:", part)
                elif "MBI:" in part:
                    parsed_line.mbi = parse_chips("MBI:", part)
                elif "CBIR:" in part:
                    parsed_line.cbir = parse_chips("CBIR:", part)

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
        elif "홀 카드딜:" in line:
            parsed_line = HoleCardsEntry()
            parsed_line.hole_cards = extract_hole_cards(line)

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

            # Keep track of the last action so we can add an uncalled_bet to it
            last_action = parsed_line

        elif "# 공베팅 반환" in line:
            start_index = line.find("# 공베팅 반환 [") + len("# 공베팅 반환 [")
            end_index = line.find("원]", start_index)
            uncalled_bet_str = line[start_index:end_index].replace(",", "")
            uncalled_bet = int(uncalled_bet_str)

            if last_action is not None:
                last_action.uncalled_bet = uncalled_bet

        elif "결과:" in line:
            parsed_line: ResultsEntry = ResultsEntry()
            parsed_line.result, parsed_line.showdown = parse_result_line(line)

        elif constants.ENTRY_FEE in line:
            parsed_line: EntryFeeEntry = EntryFeeEntry()
            parsed_line.amount, parsed_line.remaining_stack = _extract_bet_and_stack_constants(line)

        # Must be an if, not elif, because the win money string can also appear in the # returned bet string
        if "* 종료:" in line:
            win_money, credit = parse_winmoney_line(line)
            if win_money is not None and credit is not None:
                win_money_line = WinMoneyEntry()
                win_money_line.amount = win_money
                win_money_line.remaining_stack = credit

        if parsed_line is not None:
            parsed_lines.append(parsed_line)

    return parsed_lines, win_money_line

def parse_winmoney_line(line):
    pattern = r"WinMoney\[([\d,]+)원\] Credit\[([\d,]+)원\]"
    match = re.search(pattern, line)

    if match:
        # Convert captured values to integers (removing commas)
        win_money = int(match.group(1).replace(",", ""))
        credit = int(match.group(2).replace(",", ""))
        return win_money, credit
    else:
        return None

def extract_hole_cards(line):
    """
    Extracts and normalizes hole cards from poker hand history lines.

    Parameters:
        lines (list): A list of strings containing hand history lines with hole cards.

    Returns:
        list: A list of strings representing the extracted and formatted hole cards.
    """
    # Mapping suit symbols to standard poker notation
    suit_map = {
        "♥": "h",  # Hearts
        "♠": "s",  # Spades
        "♣": "c",  # Clubs
        "◆": "d"   # Diamonds (Korean uses ◆ instead of ♦)
    }

    # Convert 10 to T
    rank_map = {"10": "T"}

    hole_cards = ""

    # Extract the two hole cards using regex
    match = re.findall(r"([♠♥♣◆])(\d+|A|J|Q|K)", line)
    if match and len(match) == 2:
        # Normalize rank and suit
        normalized_cards = [
            (rank_map.get(rank, rank) + suit_map[suit]) for suit, rank in match
        ]
        hole_cards = " ".join(normalized_cards)

    return hole_cards

def parse_result_line(line):
    pattern = re.search(r"결과: (패배|승리) \[족보:(.*?)\] \[카드:(.*?)\]( - (기권승|기권))?", line)

    if not pattern:
        return None  # Return None if the line does not match

    # "result": pattern.group(1),  # 승리 (Win) or 패배 (Loss)
    # "hand_strength": pattern.group(2),  # The hand's strength (e.g., "A 탑")
    # "Final Cards": pattern.group(3),  # The player's final hand
    # "Forfeit Type": pattern.group(5) if pattern.group(5) else None  # Differentiates 기권승 (Forfeit Win) vs. 기권 (Fold)

    result_match = pattern.group(1)
    result = None
    if result_match == constants.WIN:
        result = "win"
    elif result_match == constants.LOSS:
        result = "loss"

    # If we have a pattern here, it's forfeit win or fold, which means this hand didn't get shown down for this player.
    # Only absence of a pattern indicates a showdown (I think)
    showdown = False if pattern.group(5) else True

    return result, showdown

def parse_chips(text, part):
    val = int(part.split(text)[1].replace(",", "").replace(MoneyUnit, ""))

    return val


def _parse_betting_action(line: str) -> ActionEntry:
    line = line.replace("* 베팅:", "").strip()

    bet_size, remaining_stack = _extract_bet_and_stack_constants(line)

    # Check if it's a blind posting (Small Blind / Big Blind)
    if "블라인드:SMALL" in line or "블라인드:BIG" in line:

        blind_entry = PostBlindEntry("small") if "블라인드:SMALL" in line else PostBlindEntry("big")
        blind_entry.amount = bet_size
        blind_entry.remaining_stack = remaining_stack

        return blind_entry

    parsed_data = ActionEntry()
    parsed_data.amount = bet_size
    parsed_data.remaining_stack = remaining_stack

    # Extract betting action
    if CHECK in line:
        parsed_data.action = BetType.CHECK

    if CALL in line:
        parsed_data.action = BetType.CALL

    if FOLD in line:
        parsed_data.action = BetType.FOLD

    if any(term in line for term in [GENERIC, QUARTER_POT, HALF_POT, FULL_POT, RAISE, ALL_IN]):
        parsed_data.action = BetType.BET

    if ALL_IN in line:
        parsed_data.action = BetType.ALL_IN

    if RAISE in line:
        parsed_data.action = BetType.RAISE

    # TODO extract bet sizes
    # Extract remaining stack from parentheses "(xxx,xxx원)"
    remaining_stack = None

    # Uncalled bet
    matches_after_marker = re.findall(r'\[(.*?)]', line)
    # Sometimes the uncalled bet will be at the start of the line
    if "# 공베팅 반환" in line:
        if len(matches_after_marker) >= 0:
            parsed_data.uncalled_bet = matches_after_marker[0]

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

    parsed_data.betting_position = betting_position
    parsed_data.betting_round = betting_round
    # Extract time taken in milliseconds [xxxxms]
    if "[" in line and "ms]" in line:
        if len(matches_after_marker) >= 4:
            parsed_data.time_taken_ms = matches_after_marker[3]

    return parsed_data


def _extract_bet_and_stack_constants(line):

    bet_size = 0
    remaining_stack = 0

    # Extract remaining stack first
    stack_match = re.search(rf"Credit\(([\d,]+){MoneyUnit}\)|Creadit:\s*([\d,]+){MoneyUnit}|\(([\d,]+){MoneyUnit}\)", line)
    bet_match = None

    # **Case 1: Quarter, Half, Full Pot, Raise, All-In (stack found in Credit(...))**
    if any(term in line for term in [GENERIC, QUARTER_POT, HALF_POT, FULL_POT, RAISE, ALL_IN]):
        stack_match = re.search(r"Credit\(([\d,]+)원\)", line)
        bet_match = re.search(r"\(([\d,]+)원\)", line)  # Extract bet size

    elif any(term in line for term in [SMALL_BLIND, BIG_BLIND]):
        stack_match = re.search(r"Creadit:\s*([\d,]+)원", line)  # Extract remaining stack
        bet_match = re.search(r"\[금액:([\d,]+)원\]", line)  # Extract blind amount

    elif constants.ENTRY_FEE in line:
        stack_match = re.search(r"Credit:([\d,]+)원", line)
        bet_match = re.search(r"\[금액:([\d,]+)원\]", line)  # Extract blind amount

    # **Case 3: Checks, Calls, and Folds (stack found inside parentheses `()`)**
    else:
        stack_match = re.search(r"\(([\d,]+)원\)", line)  # Extract remaining stack
        if CALL in line or CHECK in line:  # Calls and checks have a bet amount
            bet_match = re.search(r"-([\d,]+)원", line)
        elif FOLD in line:  # Folds always have a bet size of 0
            bet_match = None

    # **Extract bet size and stack**
    remaining_stack = int(stack_match.group(1).replace(",", "")) if stack_match else 0
    bet_size = int(bet_match.group(1).replace(",", "")) if bet_match else 0

    return bet_size, remaining_stack