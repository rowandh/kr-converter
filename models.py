from typing import List, Union, TypedDict, Optional
from dataclasses import dataclass

@dataclass
class PlayerAction:
    """Represents a player's betting action and final stack in a poker hand."""
    player: str  # 참가자 (Player name)
    betting_action: str  # 족보 (Hand action, e.g., call, fold, raise)
    amount_won_lost: str  # 변동 금액 (How much they won or lost)
    final_stack: str  # 남은 잔액 (Final stack after the hand)

@dataclass
class PokerHand:
    """Represents a full poker hand history with metadata and player actions."""
    round_id: str  # 라운드ID (Unique hand identifier)
    timestamp: str  # 시각 (Time of the hand)
    game_type: str  # 게임 종류 (e.g., "홀덤" for Hold'em)
    winner: str  # 승자(족보) (Winner and their hand ranking)
    winning_amount: str  # 이긴금액 (Amount won by the winner)
    players: List[PlayerAction]  # List of player actions

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

# Define the return type as a list of different entry types
ParsedHandHistory = List[
    Union[
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
]
