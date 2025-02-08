from html_parser import extract_hand_histories_from_html

html_content = ""

# Read the hand from HTML
hand_history_raw = extract_hand_histories_from_html(html_content)

# Convert to Pokerstars format
