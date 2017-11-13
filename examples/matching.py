
from collections import OrderedDict
import os
from lango.parser import StanfordServerParser
from lango.matcher import match_rules



parser = StanfordServerParser()

sents = [
    'Call me an Uber.',
    'Get my mother some flowers.',
    'Find me a pizza with extra cheese.',
    'Give Sam\'s dog a biscuit from Petshop.'
]

"""
me.call({'item': u'uber'})
my.mother.get({'item': u'flowers'})
me.order({'item': u'pizza', u'with': u'extra cheese'})
sam.dog.give({'item': u'biscuit', u'from': u'petshop'})
"""

subj_obj_rules = {
    'subj_t': OrderedDict([
        # my brother / my mother
        ('( NP ( PRP$:subject-o=my ) ( NN:relation-o ) )', {}),
        # Sam's dog
        ('( NP ( NP ( NNP:subject-o ) ( POS ) ) ( NN:relation-o ) )', {}),
        # me
        ('( NP:subject-o )', {}),
    ]),
    'obj_t': OrderedDict([
        # pizza with onions
        ('( NP ( NP:item-O ) ( PP ( IN:item_in-O ) ( NP:item_addon-O ) ) )', {}),
        # pizza
        ('( NP:item-O )', {}),
    ])
}

rules = {
    # Get me a pizza
    '( S ( VP ( VB:action-o ) ( S ( NP:subj_t ) ( NP:obj_t ) ) ) )': subj_obj_rules,
    # Get my mother flowers
    '( S ( VP ( VB:action-o ) ( NP:subj_t ) ( NP:obj_t ) ) )': subj_obj_rules,
}

def perform_action(action, item, subject, relation=None,
    item_addon=None, item_in=None):

    entity = subject
    if entity == "my":
        entity = "me"
    if relation:
        entity = '{0}.{1}'.format(entity, relation)

    item_props = {'item': item}
    if item_in and item_addon:
        item_props[item_in] = item_addon

    return '{0}.{1}({2})'.format(entity, action, item_props)

for sent in sents:
    tree = parser.parse(sent)
    print(match_rules(tree, rules, perform_action))
