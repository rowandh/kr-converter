from typing import List, Dict, Optional, Tuple
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

