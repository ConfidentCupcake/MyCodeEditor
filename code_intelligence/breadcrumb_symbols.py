"""Pure Python scope ranges for a cached breadcrumb model."""
import ast

def scope_ranges(source):
    """Return (name, start, end, depth) without importing or executing source."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError):
        return ()
    result = []
    def visit(node, depth):
        """Traverse conditional bodies too, retaining actual lexical nesting."""
        scope = isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        if scope:
            result.append((node.name, node.lineno - 1, node.end_lineno - 1, depth))
        for child in ast.iter_child_nodes(node):
            visit(child, depth + int(scope))
    visit(tree, 0)
    return tuple(result)