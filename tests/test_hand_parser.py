import unittest
from pprint import pprint
from pathlib import Path

from individual_history_parser import parse_hand_history, parse_betting_action  # Import your function
from html_parser import extract_hand_histories_from_html

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
        pprint(result)

    def test_parse_actions(self):
        test_lines = [
            "* 베팅: 다이 [0](169,039원) - 베팅순서: [0][4] [3085ms]",
            "* 베팅: 체크 -0원(364,080원) - 베팅순서: [1][2] [1831ms]",
            "* 베팅: 다이 [1](364,080원) - 베팅순서: [2][2] [7371ms]",
            "* 베팅: 콜 -1,000원(367,491원) - 베팅순서: [0][6] [318ms]",
            "* 베팅: 체크 -0원(359,491원) - 베팅순서: [3][3] [950ms]",
            "* 베팅: [블라인드:BIG] [금액:1,000원] [Creadit:364,080원]",
            "* 베팅: [블라인드:SMALL] [금액:1,000원] [Creadit:151,967원]",
        ]

        for line in test_lines:
            print(parse_betting_action(line))

    def test_parse_html(self):
        script_dir = Path(__file__).parent

        # Define the path to the "data" subdirectory
        data_folder = script_dir / "data"

        files = [f for f in data_folder.iterdir() if f.is_file()]

        for file in files:
            with open(file, "r", encoding="utf-8") as file:
                html_content = file.read()
                str = extract_hand_histories_from_html(html_content)
                pprint(str)

if __name__ == '__main__':
    unittest.main()