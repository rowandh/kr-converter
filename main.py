import sys
from individual_history_parser import parse_hand_history

def main():
    """
    A simple CLI tool to parse an HTML poker hand using 'parser.py'
    """

    html_file_path = "C:\\Users\\Work\\Desktop\\hh-samples\\river-9way.html"

    try:
        hand_data = parse_hand_history(html_file_path)

        # Print out the resulting dictionary
        import pprint
        pprint.pprint(hand_data)

    except Exception as e:
        print(f"Error parsing file '{html_file_path}': {e}")

if __name__ == "__main__":
    main()