from nltk.parse.stanford import StanfordParser
from nltk.internals import find_jars_within_path


class Parser:
    """Abstract Parser class"""
    def __init__():
        pass

    def parse(self, sent):
        pass


class OldStanfordLibParser(Parser):
    """For StanfordParser < 3.6.0"""

    def __init__(self):
        self.parser = StanfordParser()

    def parse(self, line):
        """Returns tree objects from a sentence

        Args:
            line: Sentence to be parsed into a tree

        Returns:
            Tree object representing parsed sentence
        """
        tree = list(self.parser.raw_parse(line))[0]
        tree = tree[0]
        return tree


class StanfordLibParser(OldStanfordLibParser):
    """For StanfordParser == 3.6.0"""
    def __init__(self):
        self.parser = StanfordParser(
            model_path='edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
        stanford_dir = self.parser._classpath[0].rpartition('/')[0]
        self.parser._classpath = tuple(find_jars_within_path(stanford_dir))