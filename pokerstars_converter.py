from pprint import pprint
from typing import Tuple, List

from models import PokerHand, ParsedHandHistory, CommunityCardsEntry, PlayerAction, ActionEntry


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
    community_cards = poker_hand.get_community_cards()
    history_parts = []

    dealer = poker_hand.get_dealer()

    preflop_players = poker_hand.get_ordered_preflop_players()

    # HEADER DATA
    header = f"PokerStars Hand #{hand_id}:  {game_type} - {timestamp} KST\n"
    header += f"Table 'Table 1' 9-max Seat #{dealer.flop_betting_position} is the button"

    history_parts.append(header)

    # STATUS HISTORY
    # Seat numbers are 1-indexed
    seat_lines = []
    for idx, player in enumerate(preflop_players, start=1):
        seat_lines.append(f"Seat {idx}: {player.player} ({player.get_start_stack()} in chips)")

    history_parts.append("\n".join(seat_lines))

    # ANTE HISTORY
    antes = []
    for player in preflop_players:
        ante = player.get_ante()
        antes.append(f"{player.player}: posts the ante {ante}")

    history_parts.append("\n".join(antes))

    # BLIND HISTORY
    blinds = []
    for player in preflop_players:
        blind = player.get_blind()
        if blind is not None:
            blind_amount = blind.amount
            if "SMALL" in blind.action:
                blinds.append(f"{player.player}: posts small blind {blind_amount}")
            if "BIG" in blind.action:
                blinds.append(f"{player.player}: posts big blind {blind_amount}")

    history_parts.append("\n".join(blinds))

    # PREFLOP HISTORY
    hole_cards_str = "*** HOLE CARDS ***\n"
    for player in poker_hand.players:
        hole_cards = player.get_hole_cards()
        if hole_cards:
            mapped_cards = [change_suit_card(card) for card in hole_cards]
            hole_cards_str += f"Dealt to {player.player} [{' '.join(mapped_cards)}]\n"

    history_parts.append(hole_cards_str)

    preflop_actions: List[Tuple[PlayerAction, ActionEntry]] = []
    for player in preflop_players:
        flop_betting = [action for action in player.betting_actions if action.type == "ACTION" and action.type == 0]
        for action in flop_betting:
            preflop_actions.append((player, action))

    sorted_preflop_street_actions = sorted(preflop_actions, key=lambda item: item[1].betting_position)

    preflop_betting_rounds = generate_betting_rounds(bb, sorted_preflop_street_actions)

    history_parts = history_parts + preflop_betting_rounds

    # If there's a flop
    if len(community_cards) > 0:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        flop_str = f"*** FLOP *** [{flop}]"
        history_parts.append(flop_str)

        flop_players = poker_hand.get_ordered_flop_players()

        flop_actions = []
        for player in flop_players:
            betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 1]
            for action in betting:
                flop_actions.append((player, action))

        sorted_flop_street_actions = sorted(flop_actions, key=lambda item: item[1].betting_position)

        flop_betting_rounds = generate_betting_rounds(bb, sorted_flop_street_actions)

        history_parts.append("\n".join(flop_betting_rounds))

    # If there's a turn
    if len(community_cards) > 1:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        turn = ' '.join(change_suit_card(s) for s in community_cards[1])
        turn_str = f"*** TURN *** [{flop}] [{turn}]"
        history_parts.append(turn_str)

        turn_players = poker_hand.get_ordered_turn_players()

        turn_actions = []
        for player in turn_players:
            betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 2]
            for action in betting:
                turn_actions.append((player, action))

        sorted_turn_street_actions = sorted(turn_actions, key=lambda item: item[1].betting_position)

        turn_betting_rounds = generate_betting_rounds(bb, sorted_turn_street_actions)

        history_parts.append("\n".join(turn_betting_rounds))

    if len(community_cards) > 2:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        turn = ' '.join(change_suit_card(s) for s in community_cards[1])
        river = ' '.join(change_suit_card(s) for s in community_cards[2])
        river_str = ''f"*** RIVER *** [{flop}] [{turn}] [{river}]"
        history_parts.append(river_str)

        river_players = poker_hand.get_ordered_river_players()

        river_actions = []
        for player in river_players:
            betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 2]
            for action in betting:
                river_actions.append((player, action))

        sorted_river_street_actions = sorted(river_actions, key=lambda item: item[1].betting_position)

        river_betting_rounds = generate_betting_rounds(bb, sorted_river_street_actions)

        history_parts.append("\n".join(river_betting_rounds))
    # showdown = "*** SHOWDOWN ***\n"
    # for player in poker_hand.players:
    #     if "shows" in player.raw_betting_action:
    #         showdown += f"{player.player}: shows [{player.hole_cards}]\n"

    winner_statement = f"{poker_hand.winner} collected {poker_hand.winning_amount} from pot"

    summary = "*** SUMMARY ***"

    # Let's calculate the rake by adding up all the chips before minus all the chips after
    chips_before = 0
    chips_after = 0
    for player in poker_hand.players:
        chips_after += int(player.final_stack)
        chips_before += player.get_start_stack()

    rake = chips_before - chips_after
    pot = int(poker_hand.winning_amount) + rake
    total_pot = f"Total pot {pot} | Rake {rake}"

    history_parts.append(winner_statement)
    history_parts.append(summary)
    history_parts.append(total_pot)

    if community_cards is not None and len(community_cards) > 0:
        flop = ' '.join(change_suit_card(s) for sublist in community_cards for s in sublist)
        # A board is not always printed if there are no community cards
        board_part = f"Board [{flop}]"
        history_parts.append(board_part)

    pokerstars_history = "\n".join(history_parts)

    pprint(pokerstars_history)
    return pokerstars_history


def generate_betting_rounds(min_bet_size, sorted_flop_street_actions):
    last_bet_size = min_bet_size
    result = []

    for flop_action in sorted_flop_street_actions:
        player = flop_action[0]
        player_action = flop_action[1]
        action = player_action.action
        amount = player_action.amount
        if "체크" in action:
            result.append(f"{player.player}: checks")
        elif "콜" in action:
            result.append(f"{player.player}: calls {amount}")
        elif "다이" in action:
            result.append(f"{player.player}: folds")
        elif "하프" in action:
            result.append(f"{player.player}: bets {amount}")
        elif "풀" in action:
            raise_size = amount
            result.append(f"{player.player}: raises {raise_size - last_bet_size} to {amount}")
            last_bet_size = raise_size # TODO CHECK THIS

    return result


def change_suit_card(line):
    suit = {"♠": "s", "◆": "d", "♣": "c", "♥": "h"}

    return line[1] + suit[line[0]]