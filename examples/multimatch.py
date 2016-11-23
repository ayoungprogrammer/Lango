from collections import OrderedDict
import os
from lango.parser import StanfordServerParser
from lango.matcher import match_rules


parser = StanfordServerParser()

sents = [
    'What religion is the President of the United States?'
]

rules = {
    '( SBARQ ( WHNP/WHADVP:wh_t ) ( SQ ( VBZ ) ( NP:np_t ) ) )': {
        'np_t': {
            '( NP ( NP:subj-o ) ( PP ( IN:subj_in-o ) ( NP:obj-o ) ) )': {},
            '( NP:subj-o )': {},
        },
        'wh_t': {
            '( WHNP:whnp ( WDT ) ( NN:prop-o ) )': {},
            '( WHNP/WHADVP:qtype-o )': {},
        }
    },
    '( SBARQ:subj-o )': {},
}

keys = ['subj', 'subj_in', 'obj', 'prop', 'qtype']

for sent in sents:
    tree = parser.parse(sent)
    contexts = match_rules(tree, rules, multi=True)
    for context in contexts:
        print ", ".join(['%s:%s' % (k, context.get(k)) for k in keys])

"""
5 possible matches:
subj:president of united states, subj_in:None, obj:None, prop:religion, qtype:None
subj:president of united states, subj_in:None, obj:None, prop:None, qtype:what religion
subj:president, subj_in:of, obj:united states, prop:religion, qtype:None
subj:president, subj_in:of, obj:united states, prop:None, qtype:what religion
subj:what religion is president of united states ?, subj_in:None, obj:None, prop:None, qtype:None
"""