from pprint import pprint

from models import PokerHand, ParsedHandHistory, CommunityCardsEntry, PlayerAction

def convert_to_pokerstars_format(poker_hand: PokerHand) -> str | None:
    """
    Converts a PokerHand object into PokerStars hand history format.
    """
    if poker_hand is None:
        return None

    hand_id = poker_hand.round_id.replace("-", "")
    sb = poker_hand.get_small_blind()
    bb = poker_hand.get_big_blind()
    game_type = f"Hold'em No Limit ({sb}/{bb})"
    timestamp = poker_hand.timestamp.replace("오전", "AM").replace("오후", "PM")

    '''
        We have multiple histories for each player that we need to combine.
        We need to keep track of the total pot.
    '''
    dealer = poker_hand.get_dealer()

    flop_players = poker_hand.get_ordered_flop_players()

    header = f"PokerStars Hand #{hand_id}:  {game_type} - {timestamp} KST\n"
    header += f"Table 'Table 1' 9-max Seat #{dealer.flop_betting_position} is the button\n"

    # Seat numbers are 1-indexed
    seat_lines = []
    for idx, player in enumerate(flop_players, start=1):
        seat_lines.append(f"Seat {idx}: {player.player} ({player.get_start_stack()} in chips)")

    antes = []
    for player in flop_players:
        ante = player.get_ante()
        antes.append(f"{player.player}: posts the ante {ante}")

    blinds = []
    for player in flop_players:
        blind = player.get_blind()
        if blind is not None:
            if "SMALL" in blind.get("action"):
                blinds.append(f"{player.player}: posts small blind {blind.get("amount")}")
            if "BIG" in blind.get("action"):
                blinds.append(f"{player.player}: posts big blind {blind.get("amount")}")

    hole_cards_str = "*** HOLE CARDS ***\n"
    for player in poker_hand.players:
        hole_cards = player.get_hole_cards()
        if hole_cards:
            mapped_cards = [change_suit_card(card) for card in hole_cards]
            hole_cards_str += f"Dealt to {player.player} [{' '.join(mapped_cards)}]\n"

    # betting_rounds = []
    # for player in poker_hand.players:
    #     if "체크" in player.raw_betting_action:
    #         betting_rounds.append(f"{player.player}: checks")
    #     elif "콜" in player.raw_betting_action:
    #         betting_rounds.append(f"{player.player}: calls {player.amount_won_lost}")
    #     elif "다이" in player.raw_betting_action:
    #         betting_rounds.append(f"{player.player}: folds")
    #     elif "풀" in player.raw_betting_action:
    #         betting_rounds.append(f"{player.player}: raises to {player.amount_won_lost}")
    #
    # # Format community cards dynamically
    # flop_str = f"*** FLOP *** [{' '.join(community_cards['flop'])}]" if community_cards["flop"] else ""
    # turn_str = f"*** TURN *** [{' '.join(community_cards['flop'])}] [{community_cards['turn']}]" if community_cards[
    #     "turn"] else ""
    # river_str = f"*** RIVER *** [{' '.join(community_cards['flop'])} {community_cards['turn']}] [{community_cards['river']}]" if \
    #     community_cards["river"] else ""
    #
    # showdown = "*** SHOWDOWN ***\n"
    # for player in poker_hand.players:
    #     if "shows" in player.raw_betting_action:
    #         showdown += f"{player.player}: shows [{player.hole_cards}]\n"

    winner_statement = f"{poker_hand.winner} collected {poker_hand.winning_amount} from pot\n"

    summary = "*** SUMMARY ***"

    # TODO don't calculate based on known rake but rather on total pot
    pot = int(poker_hand.winning_amount) / (1 - 0.053)
    total_pot = f"Total pot {pot} | Rake {pot - int(poker_hand.winning_amount)}"

    community_cards = poker_hand.get_community_cards()

    history_parts = [
        header,
        "\n".join(seat_lines),
        "\n".join(blinds),
        hole_cards_str,
        # "\n".join(betting_rounds),
        # flop_str,
        # turn_str,
        # river_str,
        # showdown,

        winner_statement,
        summary,
        total_pot
    ]

    if community_cards is not None and len(community_cards) > 0:
        result = ' '.join(change_suit_card(s) for sublist in community_cards for s in sublist)
        # A board is not always printed if there are no community cards
        board_part = f"Board [{result}]"
        history_parts.append(board_part)

    pokerstars_history = "\n".join(history_parts)

    pprint(pokerstars_history)
    return pokerstars_history

def change_suit_card(line):
    suit = {"♠": "s", "◆": "d", "♣": "c", "♥": "h"}

    return line[1] + suit[line[0]]