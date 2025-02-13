from enum import Enum

MoneyUnit = "원"

CHECK = "체크"
HALF_POT = "하프"
QUARTER_POT = "쿼터"
FULL_POT = "풀"
RAISE = "레이즈"
GENERIC = ""  # ?? Could be the same as RAISE
CALL = "콜"
ALL_IN = "올인"
FOLD = "다이"
LEFT_ROOM = "방나감"  # Treat as fold
TIMEOUT = "타임아웃"  # Treat as fold
BIG_BLIND = "블라인드:BIG"
SMALL_BLIND = "블라인드:SMALL"

class BetType(Enum):
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all-in"
    FOLD = "fold"


