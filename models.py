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

#
# class Player:
#     def __init__(
#         self,
#         nickname: str,
#         position: int,
#         starting_stack: int,
#         hole_cards: Tuple[str, str],
#         community_cards: List[List[str]],
#         final_stack: int,
#         actions: List[Tuple[str, str, int]],  # (street, action, amount)
#         final_hand: Optional[str],
#         winnings: int
#     ):
#         self.nickname: str = nickname
#         self.position: int = position
#         self.starting_stack: int = starting_stack
#         self.hole_cards: Tuple[str, str] = hole_cards
#         self.community_cards: List[List[str]] = community_cards
#         self.final_stack: int = final_stack
#         self.actions: List[Tuple[str, str, int]] = actions
#         self.final_hand: Optional[str] = final_hand
#         self.winnings: int = winnings
#
#     def __repr__(self) -> str:
#         return f"Player({self.nickname}, {self.position}, Stack: {self.starting_stack} -> {self.final_stack}, Winnings: {self.winnings})"
#
# class PokerHand:
#     def __init__(
#         self,
#         stage_number: str,
#         sb: int,
#         bb: int,
#         players: List[Player],
#         community_cards: Dict[str, List[str]],  # {'flop': [...], 'turn': [...], 'river': [...]}
#         actions: List[Tuple[str, str, str, Optional[int]]],  # (street, action, player, amount)
#         winner: Optional[str]
#     ):
#         self.stage_number: str = stage_number
#         self.sb: int = sb
#         self.bb: int = bb
#         self.players: List[Player] = players
#         self.community_cards: Dict[str, List[str]] = community_cards
#         self.actions: List[Tuple[str, str, str, Optional[int]]] = actions
#         self.winner: Optional[str] = winner
#
#     def __repr__(self) -> str:
#         return f"PokerHand(Stage {self.stage_number}, Players: {len(self.players)}, Winner: {self.winner})"
