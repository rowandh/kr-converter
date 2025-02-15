from datetime import datetime
from typing import Tuple, List

from constants import BetType
from models import PokerHand, PlayerAction, ActionEntry, PostBlindEntry
from utils import convert_korean_datetime_with_timezone, format_korean_date


def convert_to_pokerstars_format(poker_hand: PokerHand, correct_datetime: datetime = None) -> str | None:
    """
    Converts a PokerHand object into PokerStars hand history format.
    """
    if poker_hand is None:
        return None

    hand_id = poker_hand.round_id.replace("-", "")
    sb = poker_hand.get_small_blind_amount()
    bb = poker_hand.get_big_blind_amount()
    game_type = f"Hold'em No Limit ({sb}/{bb})"

    timestamp = convert_korean_datetime_with_timezone(poker_hand.timestamp) if correct_datetime is None else format_korean_date(correct_datetime)
    community_cards = poker_hand.get_community_cards()
    history_parts = []

    dealer = poker_hand.get_dealer()

    preflop_players = poker_hand.get_ordered_preflop_players()

    # HEADER DATA
    header = []
    header.append(f"PokerStars Hand #{hand_id}:  {game_type} - {timestamp}")
    header.append(f"Table 'Table 1' 9-max Seat #{dealer.flop_betting_position} is the button")

    history_parts.extend(header)

    # STATUS HISTORY
    # Seat numbers are 1-indexed
    seat_lines = []
    for idx, player in enumerate(preflop_players, start=1):
        seat_lines.append(f"Seat {idx}: {player.player} ({player.get_start_stack()} in chips)")

    history_parts.extend(seat_lines)

    # ANTE HISTORY
    antes = []
    for player in preflop_players:
        ante = player.get_ante()
        antes.append(f"{player.player}: posts the ante {ante}")

    history_parts.extend(antes)

    # BLIND HISTORY
    blinds = []
    for player in preflop_players:
        blind: PostBlindEntry = player.get_blind()
        if blind is not None:
            blind_amount = blind.amount
            if blind.blind_type == "small":
                blinds.append(f"{player.player}: posts small blind {blind_amount}")
            if blind.blind_type == "big":
                blinds.append(f"{player.player}: posts big blind {blind_amount}")

    history_parts.extend(blinds)

    # PREFLOP HISTORY
    hole_cards_str = []
    hole_cards_str.append("*** HOLE CARDS ***")
    # for player in poker_hand.players:
    #     hole_cards = player.get_hole_cards()
    #     if hole_cards:
    #         hole_cards_str.append(f"Dealt to {player.player} [{hole_cards}]")
    #
    history_parts.extend(hole_cards_str)

    preflop_actions: List[Tuple[PlayerAction, ActionEntry]] = []
    for player in preflop_players:
        flop_betting = player.get_preflop_actions()
        for action in flop_betting:
            preflop_actions.append((player, action))

    sorted_preflop_street_actions = sorted(preflop_actions, key=lambda item: item[1].betting_position)

    preflop_betting_rounds = generate_betting_rounds(bb, sorted_preflop_street_actions)

    history_parts.extend(preflop_betting_rounds)

    # If there's a flop
    flop_parts = []
    if len(community_cards) > 0:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        flop_str = f"*** FLOP *** [{flop}]"
        flop_parts.append(flop_str)

        flop_players = poker_hand.get_ordered_flop_players()

        flop_actions = []
        for player in flop_players:
            flop_betting = player.get_flop_actions()
            for action in flop_betting:
                flop_actions.append((player, action))

        # Get the flop actions in the order they occurred
        sorted_flop_street_actions = sorted(flop_actions, key=lambda item: item[1].betting_position)

        flop_parts.extend(generate_betting_rounds(0, sorted_flop_street_actions))
        history_parts.extend(flop_parts)

    # If there's a turn
    turn_parts = []
    if len(community_cards) > 1:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        turn = ' '.join(change_suit_card(s) for s in community_cards[1])
        turn_str = f"*** TURN *** [{flop}] [{turn}]"
        turn_parts.append(turn_str)

        turn_players = poker_hand.get_ordered_turn_players()

        turn_actions = []
        for player in turn_players:
            flop_betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 2]
            for action in flop_betting:
                turn_actions.append((player, action))

        sorted_turn_street_actions = sorted(turn_actions, key=lambda item: item[1].betting_position)

        turn_parts.extend(generate_betting_rounds(0, sorted_turn_street_actions))
        history_parts.extend(turn_parts)

    river_parts = []
    if len(community_cards) > 2:
        flop = ' '.join(change_suit_card(s) for s in community_cards[0])
        turn = ' '.join(change_suit_card(s) for s in community_cards[1])
        river = ' '.join(change_suit_card(s) for s in community_cards[2])
        river_str = ''f"*** RIVER *** [{flop}] [{turn}] [{river}]"
        river_parts.append(river_str)

        river_players = poker_hand.get_ordered_river_players()

        river_actions = []
        for player in river_players:
            flop_betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 2]
            for action in flop_betting:
                river_actions.append((player, action))

        sorted_river_street_actions = sorted(river_actions, key=lambda item: item[1].betting_position)

        river_parts.extend(generate_betting_rounds(0, sorted_river_street_actions))
        history_parts.extend(river_parts)

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

    for player in preflop_players:
        hole_cards = player.get_hole_cards()

        if player.is_winner():
            summary_line = f"Seat {player.flop_betting_position}: {player.player} showed [{hole_cards}] and won ({poker_hand.winning_amount})"
        elif player.went_to_showdown():
            summary_line = f"Seat {player.flop_betting_position}: {player.player} showed [{hole_cards}] and lost"
        else:
            summary_line = f"Seat {player.flop_betting_position}: {player.player} mucked [{hole_cards}]"

        history_parts.append(summary_line)

    pokerstars_history = "\n".join(history_parts)

    return pokerstars_history


def generate_betting_rounds(min_bet_size, sorted_street_actions):
    last_bet_size = min_bet_size
    result = []
    uncalled_bet = None

    # Stars format seems to expect a "raise" if there has been any kind of previous action
    # eg. if we're preflop and a blind has been posted

    for street_action in sorted_street_actions:
        player: PlayerAction = street_action[0]
        player_action = street_action[1]
        action = player_action.action
        amount = player_action.amount
        bet_diff = amount - last_bet_size

        if action is BetType.CHECK:
            result.append(f"{player.player}: checks")
        elif action is BetType.CALL:
            result.append(f"{player.player}: calls {amount}")
        elif action is BetType.FOLD:
            result.append(f"{player.player}: folds")

        elif action is BetType.BET:
            if last_bet_size == 0:
                result.append(f"{player.player}: bets {amount}")
            else:
                result.append(f"{player.player}: raises {bet_diff} to {amount}")
            last_bet_size = amount
        elif action is BetType.RAISE:
            result.append(f"{player.player}: raises {bet_diff} to {amount}")
            last_bet_size = amount
        elif action is BetType.ALL_IN:
            result.append(f"{player.player}: raises {bet_diff} to {amount} and is all-in")
            last_bet_size = amount

        if player_action.uncalled_bet is not None and not 0:
            uncalled_bet = f"Uncalled bet ({bet_diff}) returned to {player.player}"

    # Append the uncalled bet after all the other player actions
    if uncalled_bet is not None:
        result.append(uncalled_bet)

    return result


def change_suit_card(line):
    suit = {"♠": "s", "◆": "d", "♣": "c", "♥": "h"}

    return line[1] + suit[line[0]]