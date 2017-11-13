from nltk.parse.stanford import StanfordParser, GenericStanfordParser
from nltk.internals import find_jars_within_path
from nltk.tree import Tree
from pycorenlp import StanfordCoreNLP


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
            None if parse fails
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


class StanfordServerParser(Parser, GenericStanfordParser):
    """Follow the readme to setup the Stanford CoreNLP server"""
    def __init__(self, host='localhost', port=9000, properties={}):
        url = 'http://{0}:{1}'.format(host, port)
        self.nlp = StanfordCoreNLP(url)

        if not properties:
            self.properties = {
                'annotators': 'parse',
                'outputFormat': 'json',
            }
        else:
            self.properties = properties

    def _make_tree(self, result):
        return Tree.fromstring(result)

    def parse(self, sent):
        output = self.nlp.annotate(sent, properties=self.properties)

        # Got random html, return empty tree
        if isinstance(output, str):
            return Tree('', [])

        parse_output = output['sentences'][0]['parse'] + '\n\n'
        tree = next(next(self._parse_trees_output(parse_output)))[0]
        return tree