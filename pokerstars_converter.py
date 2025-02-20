from datetime import datetime
from typing import Tuple, List
from constants import BetType
from models import PokerHand, PlayerAction, ActionEntry, PostBlindEntry, EntryFeeEntry
from utils import convert_korean_datetime_with_timezone, format_korean_date


class PokerStarsConverter():
    def __init__(self, currency_symbol = None):
        self.currency_symbol = currency_symbol if currency_symbol is not None else ""
        pass

    def convert_to_pokerstars_format(self, poker_hand: PokerHand, correct_datetime: datetime = None) -> str | None:
        """
        Converts a PokerHand object into PokerStars hand history format.
        """
        if poker_hand is None:
            return None

        hand_id = poker_hand.round_id.replace("-", "")
        sb = poker_hand.get_small_blind_amount()
        bb = poker_hand.get_big_blind_amount()
        game_type = f"Hold'em No Limit ({self.format_currency(sb)}/{self.format_currency(bb)})"

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
            seat_lines.append(f"Seat {idx}: {player.player} ({self.format_currency(player.get_start_stack())} in chips)")

        history_parts.extend(seat_lines)

        # ANTE HISTORY
        antes = []
        for player in preflop_players:
            ante = player.get_ante()
            antes.append(f"{player.player}: posts the ante {self.format_currency(ante)}")

        history_parts.extend(antes)

        # BLIND HISTORY
        blinds = []
        for player in preflop_players:
            blind: PostBlindEntry = player.get_blind()
            if blind is not None:
                blind_amount = blind.amount
                if blind.blind_type == "small":
                    blinds.append(f"{player.player}: posts small blind {self.format_currency(blind_amount)}")
                if blind.blind_type == "big":
                    blinds.append(f"{player.player}: posts big blind {self.format_currency(blind_amount)}")

        # Now post the entry fees
        for player in preflop_players:
            entry_fee: EntryFeeEntry = player.get_entry_fee()
            if entry_fee is not None:
                blinds.append(f"{player.player}: posts big blind {self.format_currency(entry_fee.amount)}")

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
            river_betting = player.get_preflop_actions()
            for action in river_betting:
                preflop_actions.append((player, action))

        sorted_preflop_street_actions = sorted(preflop_actions, key=lambda item: item[1].betting_position)

        preflop_betting_rounds = self.generate_betting_rounds(bb, sorted_preflop_street_actions, True)

        history_parts.extend(preflop_betting_rounds)

        # If there's a flop
        flop_parts = []
        if len(community_cards) > 0:
            flop = ' '.join(self.change_suit_card(s) for s in community_cards[0])
            flop_str = f"*** FLOP *** [{flop}]"
            flop_parts.append(flop_str)

            flop_players = poker_hand.get_ordered_flop_players()

            flop_actions = []
            for player in flop_players:
                river_betting = player.get_flop_actions()
                for action in river_betting:
                    flop_actions.append((player, action))

            # Get the flop actions in the order they occurred
            sorted_flop_street_actions = sorted(flop_actions, key=lambda item: item[1].betting_position)

            flop_parts.extend(self.generate_betting_rounds(0, sorted_flop_street_actions))
            history_parts.extend(flop_parts)

        # If there's a turn
        turn_parts = []
        if len(community_cards) > 1:
            flop = ' '.join(self.change_suit_card(s) for s in community_cards[0])
            turn = ' '.join(self.change_suit_card(s) for s in community_cards[1])
            turn_str = f"*** TURN *** [{flop}] [{turn}]"
            turn_parts.append(turn_str)

            turn_players = poker_hand.get_ordered_turn_players()

            turn_actions = []
            for player in turn_players:
                river_betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 2]
                for action in river_betting:
                    turn_actions.append((player, action))

            sorted_turn_street_actions = sorted(turn_actions, key=lambda item: item[1].betting_position)

            turn_parts.extend(self.generate_betting_rounds(0, sorted_turn_street_actions))
            history_parts.extend(turn_parts)

        river_parts = []
        if len(community_cards) > 2:
            flop = ' '.join(self.change_suit_card(s) for s in community_cards[0])
            turn = ' '.join(self.change_suit_card(s) for s in community_cards[1])
            river = ' '.join(self.change_suit_card(s) for s in community_cards[2])
            river_str = ''f"*** RIVER *** [{flop}] [{turn}] [{river}]"
            river_parts.append(river_str)

            river_players = poker_hand.get_ordered_river_players()

            river_actions = []
            for player in river_players:
                river_betting = [action for action in player.betting_actions if action.type == "ACTION" and action.betting_round == 3]
                for action in river_betting:
                    river_actions.append((player, action))

            sorted_river_street_actions = sorted(river_actions, key=lambda item: item[1].betting_position)

            river_parts.extend(self.generate_betting_rounds(0, sorted_river_street_actions))
            history_parts.extend(river_parts)

        winner_statements = []
        winners = poker_hand.get_winners()

        for winner in winners:
            pot_type = ""
            if len(winners) > 1:
                pot_type = " main" if winner.win_money.amount == int(poker_hand.winning_amount) else " side"
            winner_statements.append(f"{winner.player} collected {self.format_currency(winner.win_money.amount)} from{pot_type} pot")

        history_parts.extend(winner_statements)

        summary = "*** SUMMARY ***"

        # Let's calculate the rake by adding up all the chips before minus all the chips after
        chips_before = 0
        chips_after = 0
        for player in poker_hand.players:
            chips_after += int(player.final_stack)
            chips_before += player.get_start_stack()

        rake = chips_before - chips_after
        pot = int(poker_hand.winning_amount) + rake
        total_pot = f"Total pot {self.format_currency(pot)} | Rake {self.format_currency(rake)}"

        history_parts.append(summary)
        history_parts.append(total_pot)

        if community_cards is not None and len(community_cards) > 0:
            flop = ' '.join(self.change_suit_card(s) for sublist in community_cards for s in sublist)
            # A board is not always printed if there are no community cards
            board_part = f"Board [{flop}]"
            history_parts.append(board_part)

        for player in preflop_players:
            hole_cards = player.get_hole_cards()

            betting_position = poker_hand.get_betting_position(player)

            if player.is_winner():
                summary_line = f"Seat {betting_position}: {player.player} showed [{hole_cards}] and won ({self.format_currency(player.win_money.amount)})"
            elif player.went_to_showdown():
                summary_line = f"Seat {betting_position}: {player.player} showed [{hole_cards}] and lost"
            else:
                summary_line = f"Seat {betting_position}: {player.player} mucked [{hole_cards}]"

            history_parts.append(summary_line)

        pokerstars_history = "\n".join(history_parts)

        return pokerstars_history


    def generate_betting_rounds(self, min_bet_size, sorted_street_actions, include_blind = False):
        last_bet_size = min_bet_size
        result = []
        uncalled_bet = None
        action_opened = include_blind

        # Keep track of the amount invested in this street by each player
        player_invested = {}

        for street_action in sorted_street_actions:
            player: PlayerAction = street_action[0]
            player_action = street_action[1]
            action = player_action.action

            if player.player not in player_invested:
                # We can have multiple blinds eg. for entry fees so make sure we include all of these
                blind_amount = player.get_blind_investment() if include_blind else 0
                player_invested[player.player] = blind_amount
            player_invested[player.player] += player_action.amount

            player_invested_this_street = player_invested[player.player]
            bet_diff = player_invested_this_street - last_bet_size
            amount = player_invested_this_street
            all_in = " and is all-in" if player_action.remaining_stack == 0 else ""

            if action is BetType.CHECK:
                result.append(f"{player.player}: checks")
            elif action is BetType.CALL:
                result.append(f"{player.player}: calls {self.format_currency(player_action.amount)}")
            elif action is BetType.FOLD:
                result.append(f"{player.player}: folds")
            elif action is BetType.BET:
                if not action_opened:
                    result.append(f"{player.player}: bets {self.format_currency(amount)}")
                    last_bet_size = amount
                else:
                    result.append(f"{player.player}: raises {self.format_currency(bet_diff)} to {self.format_currency(player_invested_this_street)}{all_in}")
                    last_bet_size = player_invested_this_street
                action_opened = True

            elif action is BetType.ALL_IN or BetType.RAISE:
                if not action_opened:
                    result.append(f"{player.player}: bets {self.format_currency(player_invested_this_street)}{all_in}")
                    last_bet_size = player_invested_this_street
                else:
                    if bet_diff <= 0: # We are calling an all-in
                        result.append(f"{player.player}: calls {self.format_currency(player_action.amount)}{all_in}")
                        last_bet_size = player_action.amount
                    else:
                        result.append(f"{player.player}: raises {self.format_currency(bet_diff)} to {self.format_currency(player_invested_this_street)}{all_in}")
                        last_bet_size = player_invested_this_street
                action_opened = True

            if player_action.uncalled_bet is not None and not 0:
                uncalled_bet = f"Uncalled bet ({self.format_currency(player_action.uncalled_bet)}) returned to {player.player}"

        # Append the uncalled bet after all the other player actions
        if uncalled_bet is not None:
            result.append(uncalled_bet)

        return result


    @staticmethod
    def change_suit_card(line):
        suit = {"♠": "s", "◆": "d", "♣": "c", "♥": "h"}

        return line[1] + suit[line[0]]

    def format_currency(self, amount):

        return f"{self.currency_symbol}{amount}"