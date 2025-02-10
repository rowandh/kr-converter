from typing import List, Union, TypedDict, Optional
from dataclasses import dataclass

class StartEntry(TypedDict):
    type: str  # "START"
    stage_number: str
    credit: int
    sb: int
    bb: int
    mbi: int
    cbir: int

class PlayerEntry(TypedDict):
    type: str  # "PLAYER"
    nickname: str

class AnteEntry(TypedDict):
    type: str  # "ANTE"
    ante: int
    remaining_stack: int

class HoleCardsEntry(TypedDict):
    type: str  # "HOLE_CARDS"
    hole_cards: List[str]

class CommunityCardsEntry(TypedDict):
    type: str  # "COMMUNITY_CARDS"
    hole_cards: List[str]
    community_cards: List[List[str]]

class RoundStartEntry(TypedDict):
    type: str  # "ROUND_START"
    round: str  # "Preflop", "Flop", "Turn", "River"
    hand_ranking: Optional[str]
    hole_cards: Optional[str]

class ActionEntry(TypedDict):
    type: str  # "ACTION"
    action: str  # "콜", "체크", "다이", "풀"
    amount: Optional[int]
    remaining_stack: Optional[int]
    is_blind: Optional[bool]
    betting_round: Optional[int]
    betting_position: Optional[int]
    time_taken_ms: Optional[int]

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
    HoleCardsEntry,
    CommunityCardsEntry,
    RoundStartEntry,
    ActionEntry,
    EndEntry,
    UnknownEntry
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
    betting_action: ParsedHandHistory
    amount_won_lost: str  # 변동 금액 (How much they won or lost)
    final_stack: str  # 남은 잔액 (Final stack after the hand)

    @property
    def flop_betting_position(self):
        return next((action.get("betting_position") for action in self.betting_action
             if action.get("type") == "ACTION" and action.get("betting_round") == 0))

    def get_ante(self) -> int:
        return next((action.get("amount") for action in self.betting_action
             if action.get("type") == "ANTE" and action.get("amount") is not None), 0)

    def get_blind(self) -> ActionEntry:
        return next((action for action in self.betting_action
             if action.get("type") == "ACTION" and action.get("is_blind") is not None
                     and action.get("is_blind") == True), None)

    def get_start_stack(self):
        return next((action.get("credit") for action in self.betting_action
             if action.get("type") == "START"), 0)

    def get_small_blind(self):
        return next((action.get("sb") for action in self.betting_action
             if action.get("type") == "START"), 0)

    def get_big_blind(self):
        return next((action.get("bb") for action in self.betting_action
             if action.get("type") == "START"), 0)

    def get_hole_cards(self):
        for action in self.betting_action:
            if action.get("type") == "COMMUNITY_CARDS" and action.get("hole_cards") is not None:
                cards = action.get("hole_cards")
                return cards

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
    def get_ordered_flop_players(self):
        return sorted(
            self.players,
            key=self.get_sort_key
        )

    def get_small_blind(self):
        return next((action.get("sb") for action in self.players[0].betting_action
             if action.get("type") == "START"), 0)

    def get_big_blind(self):
        return next((action.get("bb") for action in self.players[0].betting_action
             if action.get("type") == "START"), 0)

    @staticmethod
    def get_sort_key(item):
        for action in item.betting_action:
            if action.get("type") == "ACTION" and action.get("betting_round") == 0:
                return action.get("betting_position")
        # If no matching action is found, return a default value.
        # Use float('inf') if sorting ascending so that these items appear at the end.
        return float('inf')

    def get_dealer(self):
        flop_ordered_players = self.get_ordered_flop_players()
        # Dealer is SB if we're heads up
        dealer = flop_ordered_players[-3] if len(flop_ordered_players) >= 3 else flop_ordered_players[-2]

        return dealer

    def get_community_cards(self):
        for action in self.players[0].betting_action:
            if action.get("type") == "COMMUNITY_CARDS" and action.get("community_cards") is not None:
                cards = action.get("community_cards")
                return cards