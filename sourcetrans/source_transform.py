import ast
import sys

filename = sys.argv[1]
with open(filename) as f:
    source = f.read()
st = ast.parse(source, filename=filename, mode='exec')

class JeevesTransformer(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        """
            Transforms
                not a
            into
                jnot(a)
        """
        node = self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            return ast.copy_location(ast.Call(
                func=ast.copy_location(ast.Name(id="jnot", ctx=ast.Load()), node),
                args=[node.operand],
                keywords=[],
                starargs=None,
                kwargs=None,
            ), node)
        else:
            return node

    def visit_IfExp(self, node):
        """
            Transforms
                a if test else b
            into
                jif(test, lambda:a, lambda:b)
        """
        node = self.generic_visit(node)
        return ast.copy_location(ast.Call(
            func=ast.copy_location(ast.Name(id="jif", ctx=ast.Load()), node),
            args=[
                node.test,
                ast.copy_location(ast.Lambda(args=ast.arguments(
                    args=[],
                    vararg=None,
                    kwarg=None,
                    defaults=[],
                ), body=node.body), node.body),
                ast.copy_location(ast.Lambda(args=ast.arguments(
                    args=[],
                    vararg=None,
                    kwarg=None,
                    defaults=[],
                ), body=node.orelse), node.orelse),
            ],
            keywords=[],
            starargs=None,
            kwargs=None,
        ), node)
    
st = JeevesTransformer().visit(st)

eval(compile(st, filename=filename, mode='exec'))
