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

        round_methods = [
            ("FLOP", poker_hand.get_ordered_flop_players, lambda p: p.get_flop_actions()),
            ("TURN", poker_hand.get_ordered_turn_players, lambda p: p.get_turn_actions()),
            ("RIVER", poker_hand.get_ordered_river_players, lambda p: p.get_river_actions())
        ]

        for round_index, (round_name, get_players_func, get_actions_func) in enumerate(round_methods, start=1):
            if len(community_cards) >= round_index:
                history_parts.append(f"*** {round_name} *** {self.format_community_cards(community_cards, round_index)}")
                actions = [(player, action) for player in get_players_func() for action in get_actions_func(player)]
                sorted_actions = sorted(actions, key=lambda item: item[1].betting_position)
                history_parts.extend(self.generate_betting_rounds(0, sorted_actions))

        winner_statements = []
        winners = poker_hand.get_winners()
        main_pot = 0
        side_pot = 0
        main_pot_text = ""
        side_pot_text = ""

        """TODO side pots are n-indexed if there's more than 1.
*** SHOW DOWN ***
maybesteve: shows [Js 4h 8h Qh] (a straight, Four to Eight)
Calligula2: mucks hand 
maybesteve collected 80777 from side pot-2 
Bluff_R_Fish: mucks hand 
maybesteve collected 38366 from side pot-1 
aldan55: mucks hand 
maybesteve collected 36385 from main pot        
*** SUMMARY ***
Total pot 162857 Main pot 36385. Side pot-1 38366. Side pot-2 80777. | Rake 7329 
        """

        # TODO this is not how you determine side pots, because there can be multiple side pots
        # in the HH that are won by the same player
        # We need to keep track of side pots correctly
        # A side pot happens if a player is all in and there is further betting
        for winner in winners:
            pot_type = ""
            if len(winners) > 1:
                if winner.win_money.amount == int(poker_hand.winning_amount):
                    pot_type = " main"
                    main_pot = winner.win_money.amount
                    main_pot_text = f" Main pot {self.format_currency(winner.win_money.amount)}."
                else:
                    pot_type = " side"
                    side_pot = winner.win_money.amount
                    side_pot_text = f" Side pot {self.format_currency(winner.win_money.amount)}."
            else:
                main_pot = winner.win_money.amount
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
        pot = main_pot + side_pot + rake

        total_pot = f"Total pot {self.format_currency(pot)}{main_pot_text}{side_pot_text} | Rake {self.format_currency(rake)}"

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

        for player, player_action in sorted_street_actions:
            action = player_action.action

            if player.player not in player_invested:
                # We can have multiple blinds eg. for entry fees so make sure we include all of these
                blind_amount = player.get_blind_investment() if include_blind else 0
                player_invested[player.player] = blind_amount
            player_invested[player.player] += player_action.amount

            invested = player_invested[player.player]
            bet_diff = invested - last_bet_size
            all_in = " and is all-in" if player_action.remaining_stack == 0 else ""

            if action is BetType.CHECK:
                result.append(f"{player.player}: checks")
            elif action is BetType.CALL:
                result.append(f"{player.player}: calls {self.format_currency(player_action.amount)}")
            elif action is BetType.FOLD:
                result.append(f"{player.player}: folds")
            elif action in (BetType.BET, BetType.ALL_IN, BetType.RAISE):
                if not action_opened:
                    verb = "bets"
                    value = self.format_currency(invested)
                    new_last = invested
                else:
                    if bet_diff <= 0:
                        verb = "calls"
                        value = self.format_currency(player_action.amount)
                        new_last = player_action.amount
                    else:
                        verb = "raises"
                        value = f"{self.format_currency(bet_diff)} to {self.format_currency(invested)}"
                        new_last = invested

                result.append(f"{player.player}: {verb} {value}{all_in}")
                last_bet_size = new_last
                action_opened = True

            if player_action.uncalled_bet not in (None, 0):
                uncalled_bet = f"Uncalled bet ({self.format_currency(player_action.uncalled_bet)}) returned to {player.player}"

        # Append the uncalled bet after all the other player actions
        if uncalled_bet is not None:
            result.append(uncalled_bet)

        return result

    def format_community_cards(self, cards, street_index):
        """Formats community cards up to the current street."""
        return ' '.join(f'[{" ".join(self.change_suit_card(card) for card in cards[i])}]' for i in range(street_index))

    def change_suit_card(self, line):
        suit = {"♠": "s", "◆": "d", "♣": "c", "♥": "h"}

        return line[1] + suit[line[0]]

    def format_currency(self, amount):

        return f"{self.currency_symbol}{amount}"