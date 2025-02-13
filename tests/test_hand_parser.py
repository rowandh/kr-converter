import unittest
from pprint import pprint
from pathlib import Path

from constants import BetType
from individual_history_parser import parse_hand_history, _parse_betting_action  # Import your function
from html_parser import extract_hand_histories_from_html
from models import StartEntry, PlayerEntry, AnteEntry, CommunityCardsEntry, ActionEntry, PostBlindEntry


def get_next(list, type, default=None):
    return next((r for r in list if isinstance(r, type)), default)

def get_all(list, type):
    return [r for r in list if isinstance(r, type)]

class TestActionsParsing(unittest.TestCase):
    def test_parse(self):
        hand_history = """
        ♥A ♣8 ♥6 ◆3 ♥4 ◆9 ♥7 [A 탑] (다이)
        * 시작 : [StageNo:27891125] [Credit:264,846원] [SB:2,000원] [BB:2,000원] [MBI:200,000원] [CBIR:100]
        * NICKNAME:[hfcbh]
        * 앤티: -2,000원(262,846원)
        * 홀 카드딜: ♥A(26) ♣8(46) [A 탑]
        * 턴 시작: [프리플랍(0)] [족보:A 탑(♥A ♣8)]
        * 베팅: 콜 -2,000원(260,846원) - 베팅순서: [0][5] [216ms]
        * 커뮤니티 카드 딜: H(♥A♣8) C (♥6◆3♥4)
        * 턴 시작: [플랍(1)] [족보:A 탑(♥A ♣8 ♥6 ♥4 ◆3)]
        * 베팅: 체크 -0원(260,846원) - 베팅순서: [1][4] [1087ms]
        * 커뮤니티 카드 딜: H(♥A♣8) C (♥6◆3♥4) (◆9)
        * 턴 시작: [턴(2)] [족보:A 탑(♥A ◆9 ♣8 ♥6 ♥4)]
        * 베팅: 체크 -0원(260,846원) - 베팅순서: [2][4] [1854ms]
        * 커뮤니티 카드 딜: H(♥A♣8) C (♥6◆3♥4) (◆9) (♥7)
        * 턴 시작: [리버(3)] [족보:A 탑(♥A ◆9 ♣8 ♥7 ♥6)]
        * 베팅: 다이 [0](260,846원) - 베팅순서: [3][4] [236ms]
        * 종료: WinMoney[0원] Credit[260,846원]
        * 결과: 패배 [족보:A 탑] [카드:♥A ◆9 ♣8 ♥7 ♥6] - 기권
        """
        result = parse_hand_history(hand_history)

        start_entry: StartEntry = get_next(result, StartEntry)
        nickname: PlayerEntry = get_next(result, PlayerEntry)
        ante: AnteEntry = get_next(result, AnteEntry)
        community_cards: CommunityCardsEntry = get_all(result, CommunityCardsEntry)[-1]
        betting_actions: list[ActionEntry] = get_all(result, ActionEntry)

        self.assertEqual(start_entry.bb, 2000)
        self.assertEqual(start_entry.sb, 2000)
        self.assertEqual(start_entry.mbi, 200000)
        self.assertEqual(start_entry.cbir, 100)
        self.assertEqual(start_entry.credit, 264846)
        self.assertEqual(start_entry.stage_number, "27891125")

        self.assertEqual(nickname.nickname, "hfcbh")

        self.assertEqual(ante.amount, 2000)
        self.assertEqual(ante.remaining_stack, 262846)

        self.assertEqual(community_cards.hole_cards, ["♥A", "♣8"])
        self.assertEqual(community_cards.community_cards, [["♥6", "◆3", "♥4"], ["◆9"], ["♥7"]])

        self.assertEqual(betting_actions[0].action, BetType.CALL)
        self.assertEqual(betting_actions[0].amount, 2000)

    def test_parse_blinds(self):

        hand_history = """
        ♣J ♣9 ♥K ◆4 ◆10 [K 탑] (다이) (Small Blind)
        * 시작 : [StageNo:86303449] [Credit:200,000원] [SB:1,000원] [BB:1,000원] [MBI:100,000원] [CBIR:200]
        * NICKNAME:[3whj3jk21]
        * 앤티: -1,000원(199,000원)
        * 홀 카드딜: ♣J(49) ♣9(47) [J 탑]
        * 턴 시작: [프리플랍(0)] [족보:J 탑(♣J ♣9)]
        * 베팅: [블라인드:SMALL] [금액:1,000원] [Creadit:198,000원]
        * 베팅: 콜 -7,500원(190,500원) - 베팅순서: [0][8] [4109ms]
        * 커뮤니티 카드 딜: H(♣J♣9) C (♥K◆4◆10)
        * 턴 시작: [플랍(1)] [족보:K 탑(♥K ♣J ◆10 ♣9 ◆4)]
        * 베팅: 체크 -0원(190,500원) - 베팅순서: [1][1] [3662ms]
        * 베팅: 다이 [0](190,500원) - 베팅순서: [1][6] [3927ms]
        * 종료: WinMoney[0원] Credit[190,500원]
        * 결과: 패배 [족보:K 탑] [카드:♥K ♣J ◆10 ♣9 ◆4] - 기권
        """

        result = parse_hand_history(hand_history)

        blind = get_next(result, PostBlindEntry)
        self.assertEqual(blind.blind_type, "small")
        self.assertEqual(blind.amount, 1000)
        self.assertEqual(blind.remaining_stack, 198000)

    def test_parse_check(self):
        action = parse_hand_history("* 베팅: 체크 -0원(364,080원) - 베팅순서: [1][2] [1831ms]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.CHECK)
        self.assertEqual(bet.betting_round, 1)
        self.assertEqual(bet.betting_position, 2)
        self.assertEqual(bet.amount, 0)
        self.assertEqual(bet.remaining_stack, 364080)

    def test_parse_fold(self):
        action = parse_hand_history("* 베팅: 다이 [0](169,039원) - 베팅순서: [0][4] [3085ms]")

        fold: ActionEntry = action[0]
        self.assertEqual(fold.betting_round, 0)
        self.assertEqual(fold.betting_position, 4)
        self.assertEqual(fold.action, BetType.FOLD)
        self.assertEqual(fold.amount, 0)
        self.assertEqual(fold.remaining_stack, 169039)

    def test_parse_call(self):
        action = parse_hand_history("* 베팅: 콜 -1,000원(367,491원) - 베팅순서: [0][6] [318ms]")

        call: ActionEntry = action[0]
        self.assertEqual(call.action, BetType.CALL)
        self.assertEqual(call.betting_round, 0)
        self.assertEqual(call.betting_position, 6)
        self.assertEqual(call.amount, 1000)
        self.assertEqual(call.remaining_stack, 367491)

    def test_parse_small_blind(self):
        action = parse_hand_history("* 베팅: [블라인드:SMALL] [금액:1,022원] [Creadit:151,967원]")

        blind: PostBlindEntry = action[0]
        self.assertEqual(blind.blind_type, "small")
        self.assertEqual(blind.amount, 1022)
        self.assertEqual(blind.remaining_stack, 151967)

    def test_parse_big_blind(self):
        action = parse_hand_history("* 베팅: [블라인드:BIG] [금액:1,001원] [Creadit:364,080원]")

        blind: PostBlindEntry = action[0]
        self.assertEqual(blind.blind_type, "big")
        self.assertEqual(blind.amount, 1001)
        self.assertEqual(blind.remaining_stack, 364080)

    def test_parse_full_pot(self):
        action = parse_hand_history("* 베팅: [풀] (13,000원) Credit(391,687원) - 베팅순서: [0][1]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.BET)
        self.assertEqual(bet.amount, 13000)
        self.assertEqual(bet.remaining_stack, 391687)
        self.assertEqual(bet.betting_round, 0)
        self.assertEqual(bet.betting_position, 1)

    def test_parse_half_pot(self):
        action = parse_hand_history("* 베팅: [하프] (8,500원) Credit(405,687원) - 베팅순서: [0][2]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.BET)
        self.assertEqual(bet.amount, 8500)
        self.assertEqual(bet.remaining_stack, 405687)
        self.assertEqual(bet.betting_round, 0)
        self.assertEqual(bet.betting_position, 2)

    def test_parse_quarter_pot(self):
        action = parse_hand_history("* 베팅: [쿼터] (9,937원) Credit(163,347원) - 베팅순서: [2][2]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.BET)
        self.assertEqual(bet.amount, 9937)
        self.assertEqual(bet.remaining_stack, 163347)
        self.assertEqual(bet.betting_round, 2)
        self.assertEqual(bet.betting_position, 2)

    def test_parse_raise(self):
        action = parse_hand_history("* 베팅: [레이즈] (7,000원) Credit(92,000원) - 베팅순서: [0][6]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.RAISE)
        self.assertEqual(bet.amount, 7000)
        self.assertEqual(bet.remaining_stack, 92000)
        self.assertEqual(bet.betting_round, 0)
        self.assertEqual(bet.betting_position, 6)

    def test_parse_all_in(self):
        action = parse_hand_history("* 베팅: [올인] (38,500원) Credit(0원) - 베팅순서: [1][9]")

        bet: ActionEntry = action[0]
        self.assertEqual(bet.action, BetType.ALL_IN)
        self.assertEqual(bet.amount, 38500)
        self.assertEqual(bet.remaining_stack, 0)
        self.assertEqual(bet.betting_round, 1)
        self.assertEqual(bet.betting_position, 9)

    def test_parse_actions(self):
        test_lines = [
            # Fold
            "* 베팅: 다이 [0](169,039원) - 베팅순서: [0][4] [3085ms]",

            # Check
            "* 베팅: 체크 -0원(364,080원) - 베팅순서: [1][2] [1831ms]",

            # Fold
            "* 베팅: 다이 [1](364,080원) - 베팅순서: [2][2] [7371ms]",

            # Call 1000
            "* 베팅: 콜 -1,000원(367,491원) - 베팅순서: [0][6] [318ms]",

            # Check
            "* 베팅: 체크 -0원(359,491원) - 베팅순서: [3][3] [950ms]",

            # Post big blind
            "* 베팅: [블라인드:BIG] [금액:1,000원] [Creadit:364,080원]",

            # Post small blind
            "* 베팅: [블라인드:SMALL] [금액:1,000원] [Creadit:151,967원]",

            # Call 2000
            "* 베팅: 콜 -2,000원(260,846원) - 베팅순서: [0][5] [216ms]",

            # Check
            "* 베팅: 체크 -0원(260,846원) - 베팅순서: [1][4] [1087ms]",

            # Fold
            "* 베팅: 다이 [0](260,846원) - 베팅순서: [3][4] [236ms]",

            # Raise to an all-in size
            "* 베팅: [레이즈] (150,615원) Credit(0원) - 베팅순서: [1][6] [3394ms]",

            # Raise to a non-all-in size
            "* 베팅: [레이즈] (7,000원) Credit(92,000원) - 베팅순서: [0][6]",

            # All-in
            "* 베팅: [올인] (38,500원) Credit(0원) - 베팅순서: [1][9]",

            # Quarter pot
            "* 베팅: [쿼터] (9,937원) Credit(163,347원) - 베팅순서: [2][2]",

            # Half pot
            "* 베팅: [하프] (8,500원) Credit(405,687원) - 베팅순서: [0][2]",

            # Full pot
            "* 베팅: [풀] (13,000원) Credit(391,687원) - 베팅순서: [0][1]"
        ]

        for line in test_lines:
            print(_parse_betting_action(line))

    def test_parse_html(self):
        script_dir = Path(__file__).parent

        # Define the path to the "data" subdirectory
        data_folder = script_dir / "data"

        files = [f for f in data_folder.iterdir() if f.is_file() and f.name.lower().endswith('.html')]

        for file in files:
            with open(file, "r", encoding="utf-8") as file:
                html_content = file.read()
                str = extract_hand_histories_from_html(html_content)
                pprint(str)

if __name__ == '__main__':
    unittest.main()