import os
from lango.parser import StanfordLibParser
from lango.matcher import match_rules

os.environ['STANFORD_PARSER'] = 'stanford-parser-full-2015-12-09'
os.environ['STANFORD_MODELS'] = 'stanford-parser-full-2015-12-09'

def main():
    parser = StanfordLibParser()
    while True:
        try:
            line = raw_input("Enter line: ")
            tree = parser.parse(line)
            tree.pretty_print()
        except EOFError:
            print "Bye!"
            sys.exit(0)

if __name__ == "__main__":
    main()
