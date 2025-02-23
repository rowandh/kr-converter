from typing import List, Union, TypedDict, Optional
from dataclasses import dataclass

import constants
from constants import BetType


class StartEntry:
    type: str  = "START" # "START"
    stage_number: str
    credit: int
    sb: int
    bb: int
    mbi: int
    cbir: int

class PlayerEntry:
    type: str = "PLAYER"  # "PLAYER"
    nickname: str

class AnteEntry:
    type: str = "ANTE" # "ANTE"
    amount: int
    remaining_stack: int

class CommunityCardsEntry:
    type: str  = "COMMUNITY_CARDS" # "COMMUNITY_CARDS"
    hole_cards: List[str]
    community_cards: List[List[str]]

class ActionEntry:

    def __init__(self):
        self.uncalled_bet = None

    type: str = "ACTION" # "ACTION"
    action: BetType  # "콜", "체크", "다이", "풀"
    amount: Optional[int]
    remaining_stack: Optional[int]
    betting_round: Optional[int]
    betting_position: Optional[int]
    time_taken_ms: Optional[int]
    uncalled_bet: Optional[int]


class PostBlindEntry():
    def __init__(self, blind_type):
        self.blind_type = blind_type

    type: str = "POST_BLIND"
    amount: int
    blind_type: str
    remaining_stack: int

class HoleCardsEntry():
    type: str  = "HOLE_CARDS"
    hole_cards: str

class RoundStartEntry(TypedDict):
    type: str  # "ROUND_START"
    round: str  # "Preflop", "Flop", "Turn", "River"
    hand_ranking: Optional[str]
    hole_cards: Optional[str]

class EndEntry(TypedDict):
    type: str  # "END"
    win_money: Optional[int]
    final_credit: Optional[int]

class UnknownEntry(TypedDict):
    type: str  # "UNKNOWN"
    content: str

class ResultsEntry:
    type: str = "RESULTS"
    result: str
    showdown: str

class EntryFeeEntry:
    type: str = "ENTRY_FEE"
    amount: int
    remaining_stack: int

class WinMoneyEntry:
    type: str = "WIN_MONEY"
    amount: int
    final_stack: int

HistoryLine = Union[
    StartEntry,
    PlayerEntry,
    AnteEntry,
    CommunityCardsEntry,
    ActionEntry,
    ResultsEntry,
    EntryFeeEntry
]

# Define the return type as a list of different entry types
ParsedHandHistory = List[
    HistoryLine
]

@dataclass
class PlayerAction:
    """Represents a player's betting action and final stack in a poker hand."""
    player: str  # 참가자 (Player name)
    raw_betting_action: str  # 족보 (Hand action, e.g., call, fold, raise)
    betting_actions: ParsedHandHistory
    amount_won_lost: int  # 변동 금액 (How much they won or lost)
    final_stack: int  # 남은 잔액 (Final stack after the hand)
    win_money: WinMoneyEntry

    def is_blind(self):
        return self.get_blind() is not None

    def is_winner(self):
        return self.win_money is not None and self.win_money.amount > 0

    def went_to_showdown(self):
        result = self.results()
        return result is not None and result.showdown

    def results(self):
        return next((action for action in self.betting_actions
             if isinstance(action, ResultsEntry)), None)

    def get_round_actions(self, betting_round):
        return [action for action in self.betting_actions if
                isinstance(action, ActionEntry) and action.betting_round == betting_round]

    def get_preflop_actions(self):
        return self.get_round_actions(0)

    def get_flop_actions(self):
        return self.get_round_actions(1)

    def get_turn_actions(self):
        return self.get_round_actions(2)

    def get_river_actions(self):
        return self.get_round_actions(3)

    def get_all_betting_actions(self):
        return [action for action in self.betting_actions if isinstance(action, ActionEntry)]

    @property
    def flop_betting_position(self):
        return next((action.betting_position for action in self.betting_actions
             if isinstance(action, ActionEntry)  and action.betting_round == 0))

    def get_ante(self) -> int:
        return next((action.amount for action in self.betting_actions
             if isinstance(action, AnteEntry)  and action.amount is not None), 0)

    def get_blind_investment(self) -> PostBlindEntry | EntryFeeEntry:
        return next((action.amount for action in self.betting_actions
                     if isinstance(action, PostBlindEntry) or isinstance(action, EntryFeeEntry)), 0)

    def get_blind(self) -> PostBlindEntry:
        return next((action for action in self.betting_actions
             if isinstance(action, PostBlindEntry)), None)

    def get_entry_fee(self) -> PostBlindEntry:
        return next((action for action in self.betting_actions
             if isinstance(action, EntryFeeEntry)), None)

    def get_start_stack(self):
        return next((action.credit for action in self.betting_actions
             if isinstance(action, StartEntry)), 0)

    def get_small_blind(self):
        return next((action.sb for action in self.betting_actions
             if isinstance(action, StartEntry)), 0)

    def get_big_blind(self):
        return next((action.bb for action in self.betting_actions
             if isinstance(action, StartEntry)), 0)

    def get_hole_cards(self):
        return next((action.hole_cards for action in self.betting_actions
                     if isinstance(action, HoleCardsEntry)))

@dataclass
class PokerHand:
    """Represents a full poker hand history with metadata and player actions."""
    round_id: str  # 라운드ID (Unique hand identifier)
    timestamp: str  # 시각 (Time of the hand)
    game_type: str  # 게임 종류 (e.g., "홀덤" for Hold'em)
    winner: str  # 승자(족보) (Winner and their hand ranking)
    winning_amount: str  # 이긴금액 (Amount won by the winner)
    players: List[PlayerAction]  # List of player actions

    # We can have multiple winners in a multi-pot scenario
    # Make sure we always return the main pot winner first
    def get_winners(self):
        return [a for a in self.players if a.win_money is not None and a.win_money.amount > 0]

    def get_betting_position(self, player: PlayerAction):
        return self.get_ordered_preflop_players().index(player) + 1

    # Returns the players ordered by their action on the flop
    def get_ordered_preflop_players(self):
        blinds = [self.get_small_blind_player(), self.get_big_blind_player()]
        if len(self.players) <= 2:
            return blinds

        """
        Getting preflop players is tricky:
        - Sometimes players don't have a preflop action eg. they are auto all-in
        - Sometimes players are the blind but don't have a preflop action
        - Players can act multiple times preflop
        
        To reconstruct the order correctly:
        - Ignore blinds and append to the end of any list
        - Find all other players who aren't blinds but don't have any betting actions and put them first
        - Finally, append players in betting order
        """
        ordered_players = [None] * len(self.players)
        unordered_players = []

        for value in self.players:
            if value.is_blind():
                continue

            preflop_betting_actions = [a for a in value.betting_actions if isinstance(a, ActionEntry) and a.betting_round == 0]

            # Append players without a betting_order to the start of the list
            if len(preflop_betting_actions) == 0:
                unordered_players.append(value)
                continue

            # We don't want to add the player twice
            if value not in ordered_players:
                ordered_players[preflop_betting_actions[0].betting_position] = value
            else:
                print("Already found")

        # Ensure the players who don't bet at all are returned before the players who bet preflop
        return unordered_players + [p for p in ordered_players if p is not None] + blinds

    def get_ordered_flop_players(self):
        return sorted(
            self.get_players_in_hand(1),
            key=lambda item: self.get_sort_key(item, 1)
        )

    def get_players_in_hand(self, street):
        if len(self.players) <= 2:
            return [self.get_small_blind_player(), self.get_big_blind_player()]

        players = []

        for player in self.players:
            match = [a for a in player.betting_actions if isinstance(a, ActionEntry) and a.betting_round == street]
            if match:
                players.append(player)
        return players

    def get_ordered_turn_players(self):
        return sorted(
            self.get_players_in_hand(2),
            key=lambda item: self.get_sort_key(item, 2)
        )

    def get_ordered_river_players(self):
        return sorted(
            self.get_players_in_hand(3),
            key=lambda item: self.get_sort_key(item, 3)
        )

    def get_small_blind_player(self):
        for player in self.players:
            blind = player.get_blind()
            if blind is not None and blind.blind_type == "small":
                return player
        return None

    def get_big_blind_player(self):
        for player in self.players:
            blind = player.get_blind()
            if blind is not None and blind.blind_type == "big":
                return player
        return None

    @property
    def start_entry(self):
        return next((action for action in self.players[0].betting_actions if isinstance(action, StartEntry)))

    def get_small_blind_amount(self):
        return self.start_entry.sb

    def get_big_blind_amount(self):
        return self.start_entry.bb

    @staticmethod
    def get_sort_key(item, street):
        for action in item.betting_actions:
            if isinstance(action, ActionEntry) and action.betting_round == street:
                return action.betting_position
        # If no matching action is found, return a default value.
        # Use float('inf') if sorting ascending so that these items appear at the end.
        return float('inf')

    def get_dealer(self):
        sb = self.get_small_blind_player()

        # HU, return the SB. Can't get the preflop ordered players because they're not always there.
        if (len(self.players) <= 2):
            return sb

        preflop = self.get_ordered_preflop_players()

        # Get the player to the right of the SB
        return preflop[-3]

    def get_community_cards(self):
        return max(
            (action.community_cards
             for player in self.players
             for action in player.betting_actions
              if isinstance(action, CommunityCardsEntry)),
            key=lambda cards: len(cards),
            default=[])
