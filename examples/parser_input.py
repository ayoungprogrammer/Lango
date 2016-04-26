from lango.parser import LibParser
from lango.matcher import match_rules
import os

os.environ['STANFORD_PARSER'] = 'stanford-parser-full-2015-12-09'
os.environ['STANFORD_MODELS'] = 'stanford-parser-full-2015-12-09'

def main():
    parser = LibParser()
    while True:
        try:
            line = raw_input("Enter line: ")
            print parser.parse(line)
        except EOFError:
            print "Bye!"
            sys.exit(0)

if __name__ == "__main__":
    main()
