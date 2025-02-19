import unittest
from datetime import datetime
from pprint import pprint
from pathlib import Path

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
MuNnW738j1: raises 4000 to 5000
lopghfvas: folds
Uncalled bet (4000) returned to MuNnW738j1
MuNnW738j1 collected 3788 from pot
*** SUMMARY ***
Total pot 4000 | Rake 212
Seat 1: MuNnW738j1 showed [Ah 5c] and won (3788)
Seat 2: lopghfvas mucked [Ts 4s]"""
        content = self.read_test_file("smallhand.html")
        converted = parse(content)

        pprint(converted)
        self.assertEqual(converted, expected)

    def test_river_9way_bet_call_with_corrected_date(self):
        expected = """PokerStars Hand #15286756675:  Hold'em No Limit (1000/1000) - 2024/11/30 13:34:46 KST
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
Board [7h 2c 7c 3d 7d]
Seat 1: tblnj mucked [9d 4s]
Seat 2: rjrhrhh5 mucked [Ah Qd]
Seat 3: fgyhnmr3 mucked [Js Td]
Seat 4: htytff mucked [Kc 2s]
Seat 5: vcbbvasddas mucked [Ts 8c]
Seat 6: hjagjhgdj showed [6d 6c] and won (37880)
Seat 7: 315fasff mucked [Ks 4h]
Seat 8: kollosart showed [5h 2d] and lost
Seat 9: drsfbnuserfyb mucked [Jh 8h]"""

        content = self.read_test_file("river-9way-bet-call.html")

        correct_datetime = datetime(2024, 11,30, 13, 34, 46)
        converted = parse(content, correct_datetime)

        pprint(converted)

        self.assertEqual(converted, expected)

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
bn09: raises 9917 to 10917 and is all-in
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
Uncalled bet (9937) returned to skdigufa
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

        self.assertEqual(converted, expected)

    def test_parse_error1(self):
        expected = """PokerStars Hand #15287325953:  Hold'em No Limit (1000/1000) - 2024/12/26 17:43:21 KST
Table 'Table 1' 9-max Seat #7 is the button
Seat 1: trdhgj06 (86258 in chips)
Seat 2: vdftfa (26511 in chips)
Seat 3: AFDADFG (98000 in chips)
Seat 4: gfjhfghfg (200000 in chips)
Seat 5: mzvpbms (160363 in chips)
Seat 6: wfpsvbgo (100000 in chips)
Seat 7: gtelu940hs (414434 in chips)
Seat 8: rhmugaqgy (113622 in chips)
Seat 9: afasfasfa (129979 in chips)
trdhgj06: posts the ante 1000
vdftfa: posts the ante 1000
AFDADFG: posts the ante 1000
gfjhfghfg: posts the ante 1000
mzvpbms: posts the ante 1000
wfpsvbgo: posts the ante 1000
gtelu940hs: posts the ante 1000
rhmugaqgy: posts the ante 1000
afasfasfa: posts the ante 1000
rhmugaqgy: posts small blind 1000
afasfasfa: posts big blind 1000
*** HOLE CARDS ***
trdhgj06: calls 1000
vdftfa: folds
AFDADFG: calls 1000
gfjhfghfg: folds
mzvpbms: folds
wfpsvbgo: folds
gtelu940hs: calls 1000
rhmugaqgy: raises 5000 to 6000
afasfasfa: folds
trdhgj06: calls 5000
AFDADFG: folds
gtelu940hs: calls 5000
*** FLOP *** [4h 6c Qc]
rhmugaqgy: bets 9000
trdhgj06: folds
gtelu940hs: folds
Uncalled bet (9000) returned to rhmugaqgy
rhmugaqgy collected 27463 from pot
*** SUMMARY ***
Total pot 29000 | Rake 1537
Board [4h 6c Qc]
Seat 1: trdhgj06 mucked [Ks Tc]
Seat 2: vdftfa mucked [9h 4c]
Seat 3: AFDADFG mucked [Jd 7h]
Seat 4: gfjhfghfg mucked [8c 5s]
Seat 5: mzvpbms mucked [Jc 2s]
Seat 6: wfpsvbgo mucked [6s 3h]
Seat 7: gtelu940hs mucked [9s 7s]
Seat 8: rhmugaqgy showed [Th Td] and won (27463)
Seat 9: afasfasfa mucked [8s 6h]"""

        content = self.read_test_file("parse_error_1.html")
        converted = parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    # Scenario where HU and a player leaves before betting
    def test_parse_error2(self):
        expected = """PokerStars Hand #15292027240:  Hold'em No Limit (1000/1000) - 2024/12/23 22:25:49 KST
Table 'Table 1' 9-max Seat #1 is the button
Seat 1: i309357ai1 (200000 in chips)
Seat 2: msyjk (100000 in chips)
i309357ai1: posts the ante 1000
msyjk: posts the ante 1000
i309357ai1: posts small blind 1000
msyjk: posts big blind 1000
*** HOLE CARDS ***
i309357ai1: folds
msyjk collected 3788 from pot
*** SUMMARY ***
Total pot 4000 | Rake 212
Seat 1: i309357ai1 mucked [Qc 9s]
Seat 2: msyjk showed [9d 2d] and won (3788)"""

        content = self.read_test_file("parseerror2_2025-02-08T20-57-51.html")
        converted = parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)

    def test_all_in(self):
        expected = """PokerStars Hand #15286303596:  Hold'em No Limit (1000/1000) - 2024/09/09 22:32:44 KST
Table 'Table 1' 9-max Seat #7 is the button
Seat 1: Qqjwjqkqk (97000 in chips)
Seat 2: zxssdv (78000 in chips)
Seat 3: gtelu940hs (300000 in chips)
Seat 4: ckadmfheo (167932 in chips)
Seat 5: xbvnfgtrf (81500 in chips)
Seat 6: 3whj3jk21 (200000 in chips)
Seat 7: kvvsufhe (152615 in chips)
Seat 8: bhrghthtr (64136 in chips)
Seat 9: glkfjhl12 (415051 in chips)
Qqjwjqkqk: posts the ante 1000
zxssdv: posts the ante 1000
gtelu940hs: posts the ante 1000
ckadmfheo: posts the ante 1000
xbvnfgtrf: posts the ante 1000
3whj3jk21: posts the ante 1000
kvvsufhe: posts the ante 1000
bhrghthtr: posts the ante 1000
glkfjhl12: posts the ante 1000
bhrghthtr: posts small blind 1000
glkfjhl12: posts big blind 1000
*** HOLE CARDS ***
Qqjwjqkqk: calls 1000
zxssdv: calls 1000
gtelu940hs: calls 1000
ckadmfheo: folds
xbvnfgtrf: folds
3whj3jk21: folds
kvvsufhe: calls 1000
bhrghthtr: checks
glkfjhl12: checks
*** FLOP *** [4c 7s Jc]
bhrghthtr: folds
glkfjhl12: checks
Qqjwjqkqk: bets 15000
zxssdv: raises 22500 to 37500
gtelu940hs: folds
kvvsufhe: raises 113115 to 150615 and is all-in
glkfjhl12: folds
Qqjwjqkqk: folds
zxssdv: calls 38500 and is all-in
Uncalled bet (74615) returned to kvvsufhe
*** TURN *** [4c 7s Jc] [6h]
*** RIVER *** [4c 7s Jc] [6h] [4s]
zxssdv collected 172354 from pot
*** SUMMARY ***
Total pot 182000 | Rake 9646
Board [4c 7s Jc 6h 4s]
Seat 1: Qqjwjqkqk mucked [Js 9c]
Seat 2: zxssdv showed [Tc 7c] and won (172354)
Seat 3: gtelu940hs mucked [As 3s]
Seat 4: ckadmfheo mucked [Ks 5h]
Seat 5: xbvnfgtrf mucked [6d 3c]
Seat 6: 3whj3jk21 mucked [Jd 6s]
Seat 7: kvvsufhe showed [Ac 2c] and lost
Seat 8: bhrghthtr mucked [9d 3d]
Seat 9: glkfjhl12 mucked [Kc 7d]"""

        content = self.read_test_file("all_in.html")
        converted = parse(content)

        pprint(converted)

        self.assertEqual(converted, expected)