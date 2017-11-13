
import os
from lango.parser import StanfordServerParser
from lango.matcher import match_rules

def main():
    parser = StanfordServerParser()
    while True:
        try:
            line = input("Enter line: ")
            tree = parser.parse(line)
            tree.pretty_print()
        except EOFError:
            print("Bye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
