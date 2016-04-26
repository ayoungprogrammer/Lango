from nltk import Tree
import logging

logger = logging.getLogger(__name__)

def match_rules(tree, rules, fun):
    """Matches a Tree structure with the given query rules.

    Query rules are represented as a dictionary of template to action.
    Action is either a function, or a dictionary of subtemplate parameter to rules::

        rules = { 'template' : { 'key': rules } }
              | { 'template' : {} }

    Args:
        tree (Tree): Parsed tree structure
        rules (dict): A dictionary of query rules
        fun: Function to call
    Returns:
        Result of function call with context
        or
        None if nothing matched
    """
    context = match_rules_context(tree, rules)
    if not context:
        return None
    args = fun.__code__.co_varnames
    action_context = {}
    for arg in args:
        if arg in context:
            action_context[arg] = context[arg]
    return fun(**action_context)

def match_rules_context(tree, rules, parent_context={}):
    """Recursively matches a Tree structure with rules and returns context

    Args:
        tree (Tree): Parsed tree structure
        rules (dict): See match_rules
        parent_context (dict): Context of parent call
    Returns:
        dict: Context matched dictionary of matched rules or
        None if no match
    """
    for template, match_rules in rules.iteritems():
        context = parent_context.copy()
        if match_template(tree, template, context):
            for key, child_rules in match_rules.iteritems():
                child_context = match_rules_context(context[key],
                    child_rules, context)
                if child_context:
                    for k,v in child_context.iteritems():
                        context[k] = v
                else:
                    return None
            return context
    return None

def match_template(tree, template, args=None):
    """Check if match string matches Tree structure
    
    Args:
        tree (Tree): Parsed Tree structure of a sentence
        template (str): String template to match. Example: "( S ( NP ) )"
    Returns:
        bool: If they match or not
    """
    tokens = get_tokens(template.split())
    cur_args = {}
    if match_tokens(tree, tokens, cur_args):
        if args is not None:
            for k, v in cur_args.iteritems():
                args[k] = v
        logger.debug('MATCHED: {0}'.format(template))
        return True
    else:
        return False


def match_tokens(tree, tokens, args):
    """Check if stack of tokens matches the Tree structure
    
    Special matching rules that can be specified in the template::

        ':label': Label a token, the token will be returned as part of the context with key 'label'.
        '-@': Additional single letter argument determining return format of labeled token. Valid options are:
            '-w': Return token as word
            '-o': Return token as object
        '=word|word2|....|wordn': Force match the token words
        '$': Force match the number of tokens

    Args:
        tree : Parsed tree structure
        tokens : Stack of tokens
    Returns:
        Boolean if they match or not
    """
    arg_type_to_func = {
        'w': get_word,
        'o': get_object,
        'p': get_proper_word,
    }

    if len(tokens) == 0:
        return True

    if not isinstance(tree, Tree):
        return False

    root_token = tokens[0]

    # Equality
    if root_token.find('=') >= 0:
        eq_tokens = root_token.split('=')[1].lower().split('|')
        root_token = root_token.split('=')[0]
        word = get_word(tree)
        if word not in eq_tokens:
            return False

    # Get arg
    if root_token.find(':') >= 0:
        arg_tokens = root_token.split(':')[1].split('-')
        if len(arg_tokens) == 1:
            arg_name = arg_tokens[0]
            args[arg_name] = tree
        else:
            arg_name = arg_tokens[0]
            arg_type = arg_tokens[1]
            args[arg_name] = arg_type_to_func[arg_type](tree)
        root_token = root_token.split(':')[0]

    # Does not match wild card and label does not match
    if root_token != '.' and tree.label() not in root_token.split('/'):
        return False

    # Check end symbol
    if tokens[-1] == '$':
        if len(tree) != len(tokens[:-1]) - 1:
            return False
        else:
            tokens = tokens[:-1]

    # Check # of tokens
    if len(tree) < len(tokens) - 1:
        return False

    for i in xrange(len(tokens) - 1):
        if not match_tokens(tree[i], tokens[i + 1], args):
            return False
    return True


def get_tokens(tokens):
    """Recursively gets tokens from a match list
    
    Args:
        tokens : List of tokens ['(', 'S', '(', 'NP', ')', ')']
    Returns:
        Stack of tokens
    """
    tokens = tokens[1:-1]
    ret = []
    start = 0
    stack = 0
    for i in xrange(len(tokens)):
        if tokens[i] == '(':
            if stack == 0:
                start = i
            stack += 1
        elif tokens[i] == ')':
            stack -= 1
            if stack < 0:
                raise Exception('Bracket mismatch: ' + str(tokens))
            if stack == 0:
                ret.append(get_tokens(tokens[start:i + 1]))
        else:
            if stack == 0:
                ret.append(tokens[i])
    if stack != 0:
        raise Exception('Bracket mismatch: ' + str(tokens))
    return ret


def get_object(tree):
    """Get the object in the tree object.
    
    Method should remove unnecessary letters and words::

        the
        a/an
        's

    Args:
        tree (Tree): Parsed tree structure
    Returns:
        Resulting string of tree ``(Ex: "red car")``
    """
    if isinstance(tree, Tree):
        if tree.label() == 'DT' or tree.label() == 'POS':
            return ''
        words = []
        for child in tree:
            words.append(get_object(child))
        return ' '.join(filter(None, words))
    else:
        return tree.lower()


def get_word(tree):
    """Get the exact words in lowercase in the tree object.
    
    Args:
        tree (Tree): Parsed tree structure
    Returns:
        Resulting string of tree ``(Ex: "the red car")``
    """
    if isinstance(tree, Tree):
        words = []
        for child in tree:
            words.append(get_word(child))
        return ' '.join(words)
    else:
        return tree.lower()


def get_proper_word(tree):
    """Get unmodified words in the tree object

    Args:
        tree (Tree): Parsed tree structure
    Returns:
        Resulting string of tree ``(Ex: "The red car")``
    """
    if isinstance(tree, Tree):
        words = []
        for child in tree:
            words.append(get_proper_word(child))
        return ' '.join(words)
    else:
        return tree
