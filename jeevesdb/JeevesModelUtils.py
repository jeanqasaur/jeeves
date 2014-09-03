"""Utility functions for Jeeves database interface.

    :synopsis: Various functions used in JeevesModel.py.

.. moduleauthor: Travis Hance <tjhance7@gmail.com>
.. moduleauthor: Jean Yang <jeanyang@csail.mit.edu>
"""
import string
import random
import itertools

# From python docs
def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    as_list = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(as_list, r) for r in range(len(as_list)+1))

ALPHANUM = string.digits + string.letters
SYSRAND = random.SystemRandom()
JEEVES_ID_LEN = 32
def get_random_jeeves_id():
    """Returns a random Jeeves ID.
    """
    return "".join(ALPHANUM[SYSRAND.randint(0, len(ALPHANUM)-1)]
                    for i in xrange(JEEVES_ID_LEN))

def serialize_vars(expr):
    """Serializing Jeeves-related variables.
    """
    return ';' + ''.join('%s=%d;' % (var_name, var_value)
                            for var_name, var_value in expr.iteritems())

def unserialize_vars(sexpr):
    """Unserializing Jeeves-related variables.
    """
    var_strs = sexpr[1:].split(';')
    evars = {}
    for var_str in var_strs:
        if var_str != "":
            var_val = var_str.split('=')
            evars[var_val[0]] = bool(int(var_val[1]))
    return evars
