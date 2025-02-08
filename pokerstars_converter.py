from models import PokerHand, ParsedHandHistory


def convert_to_pokerstars_format(poker_hand: PokerHand, parsed_lines: ParsedHandHistory) -> str:
    """
    Converts a PokerHand object into PokerStars hand history format,
    including dynamically extracted community cards.
    """
    hand_id = poker_hand.round_id.replace("-", "")
    game_type = "Hold'em No Limit" if "홀덤" in poker_hand.game_type else poker_hand.game_type
    timestamp = poker_hand.timestamp.replace("오전", "AM").replace("오후", "PM")

    dealer = get_dealer_position(parsed_lines, poker_hand)

    header = f"PokerStars Hand #{hand_id}:  {game_type} - {timestamp} KST\n"
    header += f"Table 'Table 1' 9-max {dealer} is the button\n"

    # Seat numbers are 1-indexed
    seat_lines = []
    for idx, player in enumerate(poker_hand.players, start=1):
        seat_lines.append(f"Seat {idx}: {player.player} ({player.final_stack} in chips)")

    blinds = []
    for player in poker_hand.players:
        if "블라인드:SMALL" in player.betting_action:
            blinds.append(f"{player.player}: posts small blind {player.amount_won_lost}")
        if "블라인드:BIG" in player.betting_action:
            blinds.append(f"{player.player}: posts big blind {player.amount_won_lost}")

    hole_cards = "*** HOLE CARDS ***\n"
    for player in poker_hand.players:
        if player.hole_cards:
            hole_cards += f"Dealt to {player.player} [{player.hole_cards}]\n"

    betting_rounds = []
    for player in poker_hand.players:
        if "체크" in player.betting_action:
            betting_rounds.append(f"{player.player}: checks")
        elif "콜" in player.betting_action:
            betting_rounds.append(f"{player.player}: calls {player.amount_won_lost}")
        elif "다이" in player.betting_action:
            betting_rounds.append(f"{player.player}: folds")
        elif "풀" in player.betting_action:
            betting_rounds.append(f"{player.player}: raises to {player.amount_won_lost}")

    # Extract **real** community cards from the parsed history
    community_cards = {"flop": [], "turn": None, "river": None}

    for entry in parsed_lines:
        if entry["type"] == "COMMUNITY_CARDS":
            if "flop" in entry:
                community_cards["flop"] = entry["flop"]
            if "turn" in entry:
                community_cards["turn"] = entry["turn"]
            if "river" in entry:
                community_cards["river"] = entry["river"]

    # Format community cards dynamically
    flop_str = f"*** FLOP *** [{' '.join(community_cards['flop'])}]" if community_cards["flop"] else ""
    turn_str = f"*** TURN *** [{' '.join(community_cards['flop'])}] [{community_cards['turn']}]" if community_cards[
        "turn"] else ""
    river_str = f"*** RIVER *** [{' '.join(community_cards['flop'])} {community_cards['turn']}] [{community_cards['river']}]" if \
    community_cards["river"] else ""

    showdown = "*** SHOWDOWN ***\n"
    for player in poker_hand.players:
        if "shows" in player.betting_action:
            showdown += f"{player.player}: shows [{player.hole_cards}]\n"

    winner_statement = f"{poker_hand.winner} collected {poker_hand.winning_amount} from pot\n"

    pokerstars_history = "\n".join([
        header,
        "\n".join(seat_lines),
        "\n".join(blinds),
        hole_cards,
        "\n".join(betting_rounds),
        flop_str,
        turn_str,
        river_str,
        showdown,
        winner_statement
    ])

    return pokerstars_history


def get_dealer_position(parsed_lines: ParsedHandHistory, poker_hand: PokerHand) -> str:
    """
    Determines which player is on the button (dealer) for the hand.

    Returns:
    - The player's name who is on the button.
    """
    for entry in parsed_lines: # TODO FIX
        if entry["type"] == "ACTION" and "버튼" in entry.get("betting_action", ""):
            return entry["player"]  # Found the dealer

    # If no explicit button is found, assume the last player in the list (fallback)
    return poker_hand.players[-1].player if poker_hand.players else "Unknown"

