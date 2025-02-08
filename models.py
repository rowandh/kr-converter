from typing import List, Dict, Optional, Tuple

class Player:
    def __init__(
        self, 
        nickname: str, 
        position: int,
        starting_stack: int, 
        hole_cards: Tuple[str, str],
        community_cards: List[List[str]],
        final_stack: int, 
        actions: List[Tuple[str, str, int]],  # (street, action, amount)
        final_hand: Optional[str], 
        winnings: int
    ):
        self.nickname: str = nickname
        self.position: int = position
        self.starting_stack: int = starting_stack
        self.hole_cards: Tuple[str, str] = hole_cards
        self.community_cards: List[List[str]] = community_cards
        self.final_stack: int = final_stack
        self.actions: List[Tuple[str, str, int]] = actions
        self.final_hand: Optional[str] = final_hand
        self.winnings: int = winnings

    def __repr__(self) -> str:
        return f"Player({self.nickname}, {self.position}, Stack: {self.starting_stack} -> {self.final_stack}, Winnings: {self.winnings})"

class PokerHand:
    def __init__(
        self, 
        stage_number: str, 
        sb: int, 
        bb: int, 
        players: List[Player], 
        community_cards: Dict[str, List[str]],  # {'flop': [...], 'turn': [...], 'river': [...]}
        actions: List[Tuple[str, str, str, Optional[int]]],  # (street, action, player, amount)
        winner: Optional[str]
    ):
        self.stage_number: str = stage_number
        self.sb: int = sb
        self.bb: int = bb
        self.players: List[Player] = players
        self.community_cards: Dict[str, List[str]] = community_cards
        self.actions: List[Tuple[str, str, str, Optional[int]]] = actions
        self.winner: Optional[str] = winner

    def __repr__(self) -> str:
        return f"PokerHand(Stage {self.stage_number}, Players: {len(self.players)}, Winner: {self.winner})"
