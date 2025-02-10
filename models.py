from typing import List, Union, TypedDict, Optional
from dataclasses import dataclass

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
    type: str = "ACTION" # "ACTION"
    action: str  # "콜", "체크", "다이", "풀"
    amount: Optional[int]
    remaining_stack: Optional[int]
    is_blind: Optional[bool]
    betting_round: Optional[int]
    betting_position: Optional[int]
    time_taken_ms: Optional[int]
    uncalled_bet: Optional[int]

class HoleCardsEntry(TypedDict):
    type: str  # "HOLE_CARDS"
    hole_cards: List[str]

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

HistoryLine = Union[
    StartEntry,
    PlayerEntry,
    AnteEntry,
    CommunityCardsEntry,
    ActionEntry
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
    amount_won_lost: str  # 변동 금액 (How much they won or lost)
    final_stack: str  # 남은 잔액 (Final stack after the hand)

    @property
    def flop_betting_position(self):
        return next((action.betting_position for action in self.betting_actions
             if isinstance(action, ActionEntry)  and action.betting_round == 0))

    def get_ante(self) -> int:
        return next((action.amount for action in self.betting_actions
             if isinstance(action, AnteEntry)  and action.amount is not None), 0)

    def get_blind(self) -> ActionEntry:
        return next((action for action in self.betting_actions
             if isinstance(action, ActionEntry) and action.is_blind is not None
                     and action.is_blind == True), None)

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
        for action in self.betting_actions:
            if isinstance(action, CommunityCardsEntry) and action.hole_cards is not None:
                return action.hole_cards

@dataclass
class PokerHand:
    """Represents a full poker hand history with metadata and player actions."""
    round_id: str  # 라운드ID (Unique hand identifier)
    timestamp: str  # 시각 (Time of the hand)
    game_type: str  # 게임 종류 (e.g., "홀덤" for Hold'em)
    winner: str  # 승자(족보) (Winner and their hand ranking)
    winning_amount: str  # 이긴금액 (Amount won by the winner)
    players: List[PlayerAction]  # List of player actions

    # Returns the players ordered by their action on the flop
    def get_ordered_preflop_players(self):
        return sorted(
            self.players,
            key=lambda item: self.get_sort_key(item, 0)
        )

    def get_ordered_flop_players(self):
        return sorted(
            self.get_players_in_hand(1),
            key=lambda item: self.get_sort_key(item, 1)
        )

    def get_players_in_hand(self, street):
        players = []
        for player in self.players:
            for betting_action in player.betting_actions:
                if isinstance(betting_action, ActionEntry) and betting_action.betting_round == street:
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

    @property
    def start_entry(self):
        return next((action for action in self.players[0].betting_actions if isinstance(action, StartEntry)))

    def get_small_blind(self):
        return self.start_entry.sb

    def get_big_blind(self):
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
        flop_ordered_players = self.get_ordered_preflop_players()
        # Dealer is SB if we're heads up
        dealer = flop_ordered_players[-3] if len(flop_ordered_players) >= 3 else flop_ordered_players[-2]

        return dealer

    def get_community_cards(self):
        return next((action.community_cards for action in reversed(self.players[0].betting_actions)
              if isinstance(action, CommunityCardsEntry)), [])
