from collections import defaultdict


class ContextStore:

    def __init__(self):
        pass

    def get_context(self, user):
        pass

    def save_context(self, user, context):
        pass


class DictContextStore(ContextStore):

    def __init__(self):
        self.store = defaultdict(dict)
        self.store['me'] = {}

    def get_context(self, user):
        return self.store[user]

    def save_context(self, user, context):
        self.store[user] = context
