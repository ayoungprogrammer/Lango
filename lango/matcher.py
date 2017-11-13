from nltk import Tree
import logging

logger = logging.getLogger(__name__)

def match_rules(tree, rules, fun=None, multi=False):
    """Matches a Tree structure with the given query rules.

    Query rules are represented as a dictionary of template to action.
    Action is either a function, or a dictionary of subtemplate parameter to rules::

        rules = { 'template' : { 'key': rules } }
              | { 'template' : {} }

    Args:
        tree (Tree): Parsed tree structure
        rules (dict): A dictionary of query rules
        fun (function): Function to call with context (set to None if you want to return context)
        multi (Bool): If True, returns all matched contexts, else returns first matched context
    Returns:
        Contexts from matched rules
    """
    if multi:
        context = match_rules_context_multi(tree, rules)
    else:
        context = match_rules_context(tree, rules)
        if not context:
            return None

    if fun:
        args = fun.__code__.co_varnames
        if multi:
            res = []
            for c in context:
                action_context = {}
                for arg in args:
                    if arg in c:
                        action_context[arg] = c[arg]
                res.append(fun(**action_context))
            return res
        else:
            action_context = {}
            for arg in args:
                if arg in context:
                    action_context[arg] = context[arg]
            return fun(**action_context)
    else:
        return context

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
    for template, match_rules in rules.items():
        context = parent_context.copy()
        if match_template(tree, template, context):
            for key, child_rules in match_rules.items():
                child_context = match_rules_context(context[key], child_rules, context)
                if child_context:
                    for k, v in child_context.items():
                        context[k] = v
                else:
                    return None
            return context
    return None

def cross_context(contextss):
    """
    Cross product of all contexts
    [[a], [b], [c]] -> [[a] x [b] x [c]]

    """
    if not contextss:
        return []

    product = [{}]

    for contexts in contextss:
        tmp_product = []
        for c in contexts:
            for ce in product:
                c_copy = c.copy()
                c_copy.update(ce)
                tmp_product.append(c_copy)
        product = tmp_product
    return product

def match_rules_context_multi(tree, rules, parent_context={}):
    """Recursively matches a Tree structure with rules and returns context

    Args:
        tree (Tree): Parsed tree structure
        rules (dict): See match_rules
        parent_context (dict): Context of parent call
    Returns:
        dict: Context matched dictionary of matched rules or
        None if no match
    """
    all_contexts = []
    for template, match_rules in rules.items():
        context = parent_context.copy()
        if match_template(tree, template, context):
            child_contextss = []
            if not match_rules:
                all_contexts += [context]
            else:
                for key, child_rules in match_rules.items():
                    child_contextss.append(match_rules_context_multi(context[key], child_rules, context))
                all_contexts += cross_context(child_contextss)    
    return all_contexts

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
            for k, v in cur_args.items():
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
            '-r': Return token as word
            '-o': Return token as object
        '=word|word2|....|wordn': Force match raw lower case
        '$': Match end of tree

    Args:
        tree : Parsed tree structure
        tokens : Stack of tokens
    Returns:
        Boolean if they match or not
    """
    arg_type_to_func = {
        'r': get_raw_lower,
        'R': get_raw,
        'o': get_object_lower,
        'O': get_object,
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
        word = get_raw_lower(tree)
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

    for i in range(len(tokens) - 1):
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
    for i in range(len(tokens)):
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
        return ' '.join([_f for _f in words if _f])
    else:
        return tree


def get_object_lower(tree):
    return get_object(tree).lower()


def get_raw(tree):
    """Get the exact words in lowercase in the tree object.
    
    Args:
        tree (Tree): Parsed tree structure
    Returns:
        Resulting string of tree ``(Ex: "The red car")``
    """
    if isinstance(tree, Tree):
        words = []
        for child in tree:
            words.append(get_raw(child))
        return ' '.join(words)
    else:
        return tree


def get_raw_lower(tree):
    return get_raw(tree).lower()