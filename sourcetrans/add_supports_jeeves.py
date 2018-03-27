
from macropy.core.macros import *
from macropy.core.quotes import macros, ast, u
from ast import *
import common
'\nAdds the @JeevesLib.supports_jeeves decorator to indicate that the function\nsupports Jeeves\n'

def add_supports_jeeves(node):

    @Walker
    def transform(tree, stop, **kw):
        if (isinstance(tree, FunctionDef) or isinstance(tree, ClassDef)):
            tree.decorator_list.insert(0, Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='supports_jeeves', ctx=Load()))
        if isinstance(tree, Lambda):
            args = tree.args
            body = transform.recurse(tree.body)
            stop()
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='supports_jeeves', ctx=Load()), args=[Lambda(args, body)], keywords=[], starargs=None, kwargs=None)
    return transform.recurse(node)