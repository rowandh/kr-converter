import re
from bs4 import BeautifulSoup

def parse_html_hand(source_html: str) -> dict:
    """
    Parse a single HTML for a Hold'em hand (NLHE cash) and return
    a dictionary containing all relevant data: round ID, date/time,
    stakes, players, actions, streets, winner info, and final pot.
    """
    soup = BeautifulSoup(source_html, "html.parser")

    hand_data = {
        "round_id_raw": None,
        "hand_id": None,
        "datetime": None,
        "game_type": None,
        "stakes": {
            "small_blind": None,
            "big_blind": None,
            "currency": "KRW"
        },
        "players": [],
        "streets": {
            "preflop": {
                "community_cards": [],
                "actions": []
            },
            "flop": {
                "community_cards": [],
                "actions": []
            },
            "turn": {
                "community_cards": [],
                "actions": []
            },
            "river": {
                "community_cards": [],
                "actions": []
            }
        },
        "board": [],
        "winner": {
            "name": None,
            "hand_name": None,
            "amount_won": 0
        },
        "final_pot": 0
    }

    # 1) Locate the main table containing 라운드ID, 승자(족보), etc.
    all_main_tables = soup.find_all("table", attrs={"cellspacing": "0", "width": "100%", "border": "0"})
    main_table = None
    for tbl in all_main_tables:
        ths = [th.get_text(strip=True) for th in tbl.find_all("th")]
        # We look for the header row that has "라운드ID" and "승자(족보)" in it
        if len(ths) >= 5 and "라운드ID" in ths[0] and "승자(족보)" in ths[3]:
            main_table = tbl
            break

    if not main_table:
        raise ValueError("Could not find the main table containing 라운드ID, 승자(족보), etc.")

    data_rows = main_table.find_all("tr")
    if len(data_rows) < 2:
        raise ValueError("Main table found, but missing data rows.")

    data_cells = data_rows[1].find_all("td")
    if len(data_cells) < 6:
        raise ValueError("Main table's second row does not have 6 columns (expected).")

    # 2) Extract top-level info: round ID, date/time, game type, winner, final pot
    round_id_raw = data_cells[0].get_text(strip=True)  # e.g. "15-2-90683415"
    hand_data["round_id_raw"] = round_id_raw
    hand_data["hand_id"] = _extract_numeric_hand_id(round_id_raw)

    raw_datetime = data_cells[1].get_text(strip=True)  # e.g. "2024-07-11 오전 12:31:27"
    hand_data["datetime"] = _convert_datetime(raw_datetime)

    raw_game_type = data_cells[2].get_text(strip=True)  # e.g. "홀덤"
    hand_data["game_type"] = "Hold'em" if "홀덤" in raw_game_type else raw_game_type

    winner_info = data_cells[3].get_text(strip=True)   # e.g. "wpticnsosck (A 스트레이트)"
    winner_name, winner_hand = _extract_winner_name_and_hand(winner_info)
    hand_data["winner"]["name"] = winner_name
    hand_data["winner"]["hand_name"] = winner_hand

    raw_amount_won = data_cells[4].get_text(strip=True)  # e.g. "141,263"
    final_pot = _parse_int(raw_amount_won)
    hand_data["winner"]["amount_won"] = final_pot
    hand_data["final_pot"] = final_pot

    # 3) The 6th column has the nested participant details
    participants_container = data_cells[5]
    player_table = participants_container.find("table", attrs={"cellspacing": "0", "width": "100%", "border": "0"})
    if not player_table:
        raise ValueError("Could not locate participants sub-table.")

    player_rows = player_table.find_all("tr")
    if len(player_rows) < 2:
        raise ValueError("No player rows found in participants sub-table.")

    sb_amount = None
    bb_amount = None

    # 4) For each player row, parse name, net, final credit, detail text
    for row in player_rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        player_name = cols[0].get_text(strip=True)
        detail_td = cols[1]
        raw_net_str = cols[2].get_text(strip=True)
        raw_final_str = cols[3].get_text(strip=True)

        net_change = _parse_int(raw_net_str)
        final_credit = _parse_int(raw_final_str)

        # The second column is the big HTML snippet
        detail_text = detail_td.get_text("\n", strip=True)

        parsed_detail = _parse_player_detail(detail_text)

        # If we discovered blinds in the detail, store them
        if parsed_detail["sb_amount"] is not None:
            sb_amount = parsed_detail["sb_amount"]
        if parsed_detail["bb_amount"] is not None:
            bb_amount = parsed_detail["bb_amount"]

        player_data = {
            "name": player_name,
            "start_credit": parsed_detail["start_credit"],
            "final_credit": final_credit,
            "net": net_change,
            "hole_cards": parsed_detail["hole_cards"],
            "actions": parsed_detail["actions"]
        }

        hand_data["players"].append(player_data)

    # Store discovered blinds
    hand_data["stakes"]["small_blind"] = sb_amount
    hand_data["stakes"]["big_blind"] = bb_amount

    # 5) Build the street-by-street action & board from the first player
    #    who has the full flop/turn/river lines.
    for p in hand_data["players"]:
        if p["actions"]:
            streets_info = _extract_streets_from_actions(p["actions"])
            if streets_info["found_complete_board"] or streets_info["has_any_board"]:
                hand_data["streets"] = streets_info["streets"]
                hand_data["board"] = streets_info["full_board"]
                break

    return hand_data

###############################################################################
# HELPER FUNCTIONS
###############################################################################

def _extract_numeric_hand_id(round_id_raw: str) -> str:
    """
    e.g. '15-2-90683415' => '90683415'
    """
    match = re.search(r"(\d+)$", round_id_raw)
    if match:
        return match.group(1)
    return round_id_raw

def _convert_datetime(raw_datetime: str) -> str:
    """
    Convert '2024-07-11 오전 12:31:27' => '2024-07-11 00:31:27'.
    """
    # e.g. '2024-07-11 오전 12:31:27'
    date_part, time_part = raw_datetime.split(" ", 1)
    pm = '오후' in time_part
    am = '오전' in time_part
    time_digits = time_part.replace("오후", "").replace("오전", "").strip()

    h, m, s = time_digits.split(":")
    hour = int(h)
    if pm and hour < 12:
        hour += 12
    if am and hour == 12:
        hour = 0
    hour_str = f"{hour:02d}"
    return f"{date_part} {hour_str}:{m}:{s}"

def _extract_winner_name_and_hand(winner_info: str) -> tuple:
    """
    e.g. 'wpticnsosck (A 스트레이트)' => ('wpticnsosck','A 스트레이트')
    """
    match = re.match(r"^(\S+)\s*\((.+)\)$", winner_info)
    if match:
        return match.group(1), match.group(2)
    return winner_info, None

def _parse_int(text: str) -> int:
    """
    Convert '-30,000' => -30000 or '141,263' => 141263
    """
    text = text.replace(",", "")
    match = re.match(r"([-]?\d+)", text)
    if match:
        return int(match.group(1))
    return 0

def _parse_player_detail(detail_text: str) -> dict:
    """
    Within the participant's big text block, parse:
      - start_credit
      - hole_cards
      - a list of actions (bet/fold/check/all-in)
      - discovered SB/BB amounts
    """
    lines = detail_text.split("\n")
    start_credit = None
    hole_cards = []
    actions = []
    sb_amount = None
    bb_amount = None
    current_street = "preflop"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1) Starting credit
        if line.startswith("* 시작 :"):
            cred_match = re.search(r"Credit:(\d[\d,]*)원", line)
            if cred_match:
                start_credit = _parse_int(cred_match.group(1))
            sb_match = re.search(r"SB:(\d[\d,]*)원", line)
            if sb_match:
                sb_amount = _parse_int(sb_match.group(1))
            bb_match = re.search(r"BB:(\d[\d,]*)원", line)
            if bb_match:
                bb_amount = _parse_int(bb_match.group(1))

        # 2) Hole cards
        if "홀 카드딜:" in line:
            raw_cards = line.split("홀 카드딜:")[1].strip()
            raw_cards = re.sub(r"\(.*?\)", "", raw_cards)
            raw_cards = re.sub(r"<[^>]*>", "", raw_cards)
            parts = raw_cards.split()
            hole_cards = [_convert_card_symbol(c) for c in parts]

        # 3) Street transitions
        #    ex: "[프리플랍(0)]" => preflop, "[플랍(1)]" => flop, etc.
        if "턴 시작:" in line:
            if "[프리플랍(" in line:
                current_street = "preflop"
            elif "[플랍(" in line:
                current_street = "flop"
            elif "[턴(" in line:
                current_street = "turn"
            elif "[리버(" in line:
                current_street = "river"

        # 4) Actions
        if line.startswith("* 베팅:"):
            parsed_action = _parse_betting_line(line, current_street)
            if parsed_action:
                actions.append(parsed_action)

        # 5) Community card deals
        if "커뮤니티 카드 딜:" in line:
            actions.append({
                "street": current_street,
                "type": "deal_community",
                "raw_line": line
            })

    return {
        "start_credit": start_credit,
        "hole_cards": hole_cards,
        "actions": actions,
        "sb_amount": sb_amount,
        "bb_amount": bb_amount
    }

def _parse_betting_line(line: str, street: str) -> dict:
    """
    Parse lines like:
      * 베팅: 다이 [0](59,252원)
      * 베팅: 콜 -7,000원(60,502원)
      * 베팅: [쿼터] (8,000원) Credit(52,502원)
      * 베팅: [하프] (7,000원) Credit(488,476원)
      * 베팅: [올인] (52,502원) Credit(0원)
      * 베팅: 체크 -0원(47,584원)
      * 베팅: [하프] (14,000원) ...
      ...
    """
    action_data = {
        "street": street,
        "type": None,
        "amount": 0,
        "raw_line": line
    }
    content = line.split("* 베팅:", 1)[1].strip()

    # 1) Fold (다이)
    if "다이" in content:
        action_data["type"] = "fold"
        return action_data

    # 2) Check (체크)
    if "체크" in content:
        action_data["type"] = "check"
        amt_match = re.search(r"-([\d,]+)원", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    # 3) SB / BB
    if "[블라인드:SMALL]" in content:
        action_data["type"] = "post_small_blind"
        amt_match = re.search(r"금액:(\d[\d,]*)원", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    if "[블라인드:BIG]" in content:
        action_data["type"] = "post_big_blind"
        amt_match = re.search(r"금액:(\d[\d,]*)원", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    # 4) Call (콜)
    if "콜" in content:
        action_data["type"] = "call"
        amt_match = re.search(r"콜\s*-([\d,]+)원", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    # 5) Quoter / Half (쿼터, 하프)
    #    We treat them as "bet" (or "raise" if you prefer).
    if "[쿼터]" in content or "[하프]" in content:
        action_data["type"] = "bet"
        amt_match = re.search(r"\((\d[\d,]*)원\)", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    # 6) All-In (올인)
    if "[올인]" in content:
        action_data["type"] = "all_in"
        amt_match = re.search(r"\((\d[\d,]*)원\)", content)
        if amt_match:
            action_data["amount"] = _parse_int(amt_match.group(1))
        return action_data

    # 7) Generic bet pattern, e.g. "(7,000원)"
    bet_match = re.search(r"\((\d[\d,]*)원\)", content)
    if bet_match:
        action_data["type"] = "bet"
        action_data["amount"] = _parse_int(bet_match.group(1))
        return action_data

    # If unrecognized
    return action_data

def _convert_card_symbol(symbol: str) -> str:
    """
    Convert suits ♠/♥/♣/◆ to s/h/c/d.
    Convert rank 10 => T, etc.
    e.g. ♣10 => Tc, ◆K => Kd
    """
    symbol = re.sub(r"<[^>]*>", "", symbol)
    symbol = re.sub(r"\(.*?\)", "", symbol)
    symbol = symbol.strip()

    if '♠' in symbol:
        suit = 's'
    elif '♥' in symbol:
        suit = 'h'
    elif '♣' in symbol:
        suit = 'c'
    elif '◆' in symbol:
        suit = 'd'
    else:
        suit = '?'

    rank = symbol.replace('♠','').replace('♥','').replace('♣','').replace('◆','').strip()
    if rank == '10':
        rank = 'T'

    return f"{rank}{suit}"

def _extract_streets_from_actions(actions: list) -> dict:
    """
    Scan the player's actions to gather flop, turn, river deals and build
    a structured record of each street's community cards plus final board.
    """
    result = {
        "streets": {
            "preflop": {
                "community_cards": [],
                "actions": []
            },
            "flop": {
                "community_cards": [],
                "actions": []
            },
            "turn": {
                "community_cards": [],
                "actions": []
            },
            "river": {
                "community_cards": [],
                "actions": []
            }
        },
        "full_board": [],
        "found_complete_board": False,
        "has_any_board": False
    }

    current_street = "preflop"
    flop_found = False
    turn_found = False
    river_found = False

    for act in actions:
        # The action's 'street' tells us which street was active
        current_street = act["street"]

        # If it's not "deal_community", treat it as a normal betting action
        if act["type"] not in ("deal_community", None):
            result["streets"][current_street]["actions"].append(act)

        # If it's a line that deals community cards
        if act["type"] == "deal_community":
            new_cards = _extract_community_from_line(act["raw_line"])
            if new_cards:
                result["has_any_board"] = True

            # Depending on the current street:
            if current_street == "preflop":
                # this should be the flop
                result["streets"]["flop"]["community_cards"].extend(new_cards)
                flop_found = True
            elif current_street == "flop":
                # turn
                result["streets"]["turn"]["community_cards"].extend(new_cards)
                turn_found = True
            elif current_street == "turn":
                # river
                result["streets"]["river"]["community_cards"].extend(new_cards)
                river_found = True

    # Combine all found community cards
    all_cards = []
    all_cards.extend(result["streets"]["flop"]["community_cards"])
    all_cards.extend(result["streets"]["turn"]["community_cards"])
    all_cards.extend(result["streets"]["river"]["community_cards"])
    result["full_board"] = all_cards

    if flop_found and turn_found and river_found:
        result["found_complete_board"] = True

    return result

def _extract_community_from_line(line: str) -> list:
    """
    e.g.
      "* 커뮤니티 카드 딜: H(♣4◆Q♥J) C ..."
      Extract each ( ... ) group => parse suits.
    """
    cards_found = []
    if "* 커뮤니티 카드 딜:" in line:
        content = line.split("* 커뮤니티 카드 딜:", 1)[1].strip()
    else:
        content = line.strip()

    groups = re.findall(r"\(([^)]*)\)", content)
    for grp in groups:
        # e.g. "♣4◆Q♥J" or "◆4" or "♥K"
        chunk = re.sub(r"<[^>]*>", "", grp)
        chunk_cards = _split_suits(chunk)
        for c in chunk_cards:
            cconv = _convert_card_symbol(c)
            if cconv != "?":
                cards_found.append(cconv)
    return cards_found

def _split_suits(text: str) -> list:
    """
    Split a string like '♣4◆Q♥J' into ['♣4','◆Q','♥J'].
    """
    pattern = r"(♠[AKQJ\d]+|♥[AKQJ\d]+|♣[AKQJ\d]+|◆[AKQJ\d]+)"
    return re.findall(pattern, text)
