import unittest
from pprint import pprint
from pathlib import Path
import os
import fnmatch

from hand_parser import parse

class TestPokerstarsConverter(unittest.TestCase):

    def read_test_file(self, name):
        script_dir = Path(__file__).parent
        with open(script_dir / "data" / name, "r", encoding="utf-8") as file:
            html_content = file.read()
            return html_content

    def test_smallhand(self):
        expected ="""PokerStars Hand #15290682394:  Hold'em No Limit (1000/1000) - 2024/09/03 08:35:31 KST
Table 'Table 1' 9-max Seat #1 is the button
Seat 1: MuNnW738j1 (213827 in chips)
Seat 2: lopghfvas (869975 in chips)
MuNnW738j1: posts the ante 1000
lopghfvas: posts the ante 1000
MuNnW738j1: posts small blind 1000
lopghfvas: posts big blind 1000
*** HOLE CARDS ***
MuNnW738j1: raises 3000 to 4000
lopghfvas: folds
Uncalled bet (3000) returned to MuNnW738j1
MuNnW738j1 collected 3788 from pot
*** SUMMARY ***
Total pot 4000 | Rake 212
Seat 1: MuNnW738j1 showed [Ah 5c] and won (3788)
Seat 2: lopghfvas mucked [Ts 4s]"""
        content = self.read_test_file("smallhand.html")
        converted = parse(content)

        pprint(converted)
        self.assertTrue(converted.startswith(expected))

    def test_river_9way_bet_call(self):
        expected = """PokerStars Hand #15286756675:  Hold'em No Limit (1000/1000) - 2024/12/31 06:57:16 KST
Table 'Table 1' 9-max Seat #7 is the button
Seat 1: tblnj (164774 in chips)
Seat 2: rjrhrhh5 (85000 in chips)
Seat 3: fgyhnmr3 (256674 in chips)
Seat 4: htytff (170039 in chips)
Seat 5: vcbbvasddas (964716 in chips)
Seat 6: hjagjhgdj (369491 in chips)
Seat 7: 315fasff (326274 in chips)
Seat 8: kollosart (153967 in chips)
Seat 9: drsfbnuserfyb (366080 in chips)
tblnj: posts the ante 1000
rjrhrhh5: posts the ante 1000
fgyhnmr3: posts the ante 1000
htytff: posts the ante 1000
vcbbvasddas: posts the ante 1000
hjagjhgdj: posts the ante 1000
315fasff: posts the ante 1000
kollosart: posts the ante 1000
drsfbnuserfyb: posts the ante 1000
kollosart: posts small blind 1000
drsfbnuserfyb: posts big blind 1000
*** HOLE CARDS ***
tblnj: folds
rjrhrhh5: calls 1000
fgyhnmr3: calls 1000
htytff: folds
vcbbvasddas: calls 1000
hjagjhgdj: calls 1000
315fasff: calls 1000
kollosart: checks
drsfbnuserfyb: checks
*** FLOP *** [7h 2c 7c]
kollosart: checks
drsfbnuserfyb: checks
rjrhrhh5: checks
fgyhnmr3: checks
vcbbvasddas: checks
hjagjhgdj: checks
315fasff: checks
*** TURN *** [7h 2c 7c] [3d]
kollosart: checks
drsfbnuserfyb: folds
rjrhrhh5: bets 8000
fgyhnmr3: folds
vcbbvasddas: folds
hjagjhgdj: calls 8000
315fasff: folds
kollosart: calls 8000
*** RIVER *** [7h 2c 7c] [3d] [7d]
kollosart: checks
rjrhrhh5: bets 8000
hjagjhgdj: calls 8000
kollosart: calls 8000
hjagjhgdj collected 37880 from pot
*** SUMMARY ***
Total pot 40000 | Rake 2120
Board [7h 2c 7c 3d 7d]"""

        content = self.read_test_file("river-9way-bet-call.html")
        converted = parse(content)

        pprint(converted)

        self.assertTrue(converted.startswith(expected))

    def test_all_in_pre(self):
        expected = """PokerStars Hand #15286303849:  Hold'em No Limit (1000/1000) - 2024/11/10 15:32:02 KST
Table 'Table 1' 9-max Seat #7 is the button
Seat 1: bn09 (10917 in chips)
Seat 2: jqjwhhre (153512 in chips)
Seat 3: zjckvjvnek (96000 in chips)
Seat 4: nsukrwph (100000 in chips)
Seat 5: yydfgrr (91000 in chips)
Seat 6: skdigufa (184201 in chips)
Seat 7: itdtyf7v (114516 in chips)
Seat 8: apsdifjadsfjhzehzihn (107311 in chips)
Seat 9: zqclbn9xgi (200000 in chips)
bn09: posts the ante 1000
jqjwhhre: posts the ante 1000
zjckvjvnek: posts the ante 1000
nsukrwph: posts the ante 1000
yydfgrr: posts the ante 1000
skdigufa: posts the ante 1000
itdtyf7v: posts the ante 1000
apsdifjadsfjhzehzihn: posts the ante 1000
zqclbn9xgi: posts the ante 1000
apsdifjadsfjhzehzihn: posts small blind 1000
zqclbn9xgi: posts big blind 1000
*** HOLE CARDS ***
bn09: raises 8917 to 9917 and is all-in
jqjwhhre: folds
zjckvjvnek: folds
nsukrwph: folds
yydfgrr: folds
skdigufa: calls 9917
itdtyf7v: folds
apsdifjadsfjhzehzihn: calls 8917
zqclbn9xgi: folds
*** FLOP *** [7s Js 3d]
apsdifjadsfjhzehzihn: checks
skdigufa: checks
*** TURN *** [7s Js 3d] [2s]
apsdifjadsfjhzehzihn: checks
skdigufa: bets 9937
apsdifjadsfjhzehzihn: folds
*** RIVER *** [7s Js 3d] [2s] [Jc]
skdigufa collected 37645 from pot
*** SUMMARY ***
Total pot 39751 | Rake 2106
Board [7s Js 3d 2s Jc]
Seat 1: bn09 showed [Ac 2h] and lost
Seat 2: jqjwhhre mucked [Jh 5d]
Seat 3: zjckvjvnek mucked [Ah 8s]
Seat 4: nsukrwph mucked [Th 4h]
Seat 5: yydfgrr mucked [Qh 8d]
Seat 6: skdigufa showed [As 5s] and won (37645)
Seat 7: itdtyf7v mucked [9s 3h]
Seat 8: apsdifjadsfjhzehzihn mucked [Qd Td]
Seat 9: zqclbn9xgi mucked [Qc 2d]"""

        content = self.read_test_file("all_in_pre.html")
        converted = parse(content)

        pprint(converted)

        self.assertTrue(converted.startswith(expected))