"""Reply State"""
class ReplyState:
    """Recursive reply state to model a conversation

    Has three main methods:
    process: Processes a line of text and uses it to change context
    transition: Use current context to transititon to new reply state
    reply: Uses context to generate a reply or prompt
    """
    def __init__(self, prompt, parent_done=None):
        """Initializes base reply state

        Args:
          prompt: Prompt to be used for reply. Can be a string or a function 
              that takes in a context. 
              Examples:
                'What is your name?' or
                lambda context: 'Hello {0}'.format(context.get('name'))
          parent_done: Function to call after current state is done. Usually
              this function will be used to clear the context.
        """
        self.prompt = prompt
        self.end_state = 'done'
        self.parent_done = parent_done

    def reply(self, context):
        """Returns a reply given a context
        
        Args:
          context: Dictionary of current context
        Returns:
          Prompt 
        """
        if isinstance(self.prompt, str):
            return self.prompt
        else:
            return self.prompt(context)

    def process(self, sent, context):
        """Processes a line to change context
        
        Args:
            sent: Line of text to process
            context: Dictionary of current context
        """
        pass

    def transition(self, context):
        """Uses context to transition internal state
        
        Args:
            context: Dictionary of current context
        """
        pass

    def done(self, context):
        """Final function to call before exiting state. Used for clearing
            context
        
        Args:
            context: Dictionary of current context
        """
        if self.parent_done:
            self.parent_done(context)
        context.pop(self.state_name, None)


class ReplyMatch(ReplyState):
    """Matches a sentence to a reply"""
    def __init__(self, state_name, parent_done=None, replies={}):
        """Creates a ReplyMatch
        
        Args:
          state_name: Name of context
          parent_done: Function to call after done
          Replies: Map of states to ReplyPrompts
        """
        ReplyPrompt.__init__(self, None, parent_done)
        self.state_name = state_name
        self.replies = replies

    def match(self, sent, context):
        pass

    def process(self, sent, context):
        state = context.get(self.state_name)
        if state:
            return self.replies[state].process(sent, tree, context)
        else:
            return self.match(sent, tree, context)

    def transition(self, context):
        state = context.get(self.state_name)
        if state:
            self.replies[state].transition(context)

    def reply(self, context):
        state = context.get(self.state_name)
        if state == self.end_state:
            return self.done(context)
        elif state:
            return self.replies[state].reply(context)


class ReplyFlow(ReplyState):
    """Replies to a sentence based on current flow"""
    def __init__(self, state_name, parent_done, replies):
        ReplyPrompt.__init__(self, None, parent_done)
        self.state_name = state_name

    def process(self, sent, tree, context):
        state = context[self.state_name]
        if state:
            self.replies[state].process(sent, tree, context)

    def transition(self, context):
        state = context.get(self.state_name)
        if state:
            self.replies[state].transition(context)

    def reply(self, context):
        state = context.get(self.state_name)
        if state == self.end_state:
            return self.done(context)
        elif state:
            return self.replies[state].reply(context)
