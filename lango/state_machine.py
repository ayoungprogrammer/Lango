import logging

from lango.context_store import DictContextStore

class StateMachine:
    """State machine to process a line of text at a time"""

    def __init__(self, root, context_store=None):
        """ Create state machine

        The state machine retrieves 

        Args: 
            root: Root reply state
        """
        if context_store != None:
            self.context_store = context_store
        else:
            self.context_store = DictContextStore()

        self.root = root
        self.logger = logging.getLogger(__name__)
        self.preprocessors = []

    def register_preprocessor(self, preprocessor):
        """Adds a preprocessor for preprocessing lines

        Args:
          preprocessor: Function f(str)->str that takes in string and outputs another string
                        Example:
                          lambda line: line.upper()
        """
        self.preprocessors.append(preprocessor)

    def preprocess(self, line):
        """Chain applies preprocessors in the order they were registered the string line

        Args:
          line: Line to be preprocessed. Example: Hello!

        Returns:
          Preprocessed line
        """
        return reduce(lambda line, fun: fun(line), self.preprocessors, line)

    def answer(self, line):
        """Gives an answer to a line of text

        Steps through the state machine and calls process, transition and reply
        to get the response for a line of text.

        Args:
          line: Line of text to be given an answer to. Exampe: Hello!

        Returns:
          Answer to line of text. Example: Hi!
          None if root reply state does not return an answer
        """
        sent = self.preprocess(line)
        self.logger.info('Preprocessed: {0}'.format(sent))

        context = self.context_store.get_context(user)

        self.logger.info('***PROCESS***')
        self.root_reply.process(sent, context)

        self.logger.info('***TRANSITION***')
        self.root_reply.transition(context)

        self.logger.info('***REPLY***')
        ans = self.root_reply.reply(context)

        self.logger.info('Context: {0}'.format(context))
        self.context_store.save_context(user, context)

        if ans:
            return ans

        return None
