"""General type, binding and control-flow validation, independent of C generation."""
from .frontend import Diagnostic, Token

BUILTINS = {'print', 'read_int', 'len', 'assert', 'assert_eq', 'assert_ne'}
SCALARS = ('int', 'bool', 'text')


class Checker:
    def __init__(self, nodes, test_mode=False, source_token=None):
        self.nodes = nodes
        self.functions = {}
        self.test_mode = test_mode
        self.source_token = source_token

    def error(self, node, code, message, hint=None):
        raise Diagnostic(node.token, code, message, hint)

    def require(self, node, actual, expected):
        if actual != expected:
            self.error(node, 'E102', f'expected {expected}, found {actual}')

    def check(self):
        tests = set()
        for node in self.nodes:
            if node.kind == 'fn':
                if node.value in self.functions or node.value in BUILTINS:
                    self.error(node, 'E101', f'duplicate or reserved function {node.value}')
                self.functions[node.value] = node
            else:
                if not node.value or any(ord(c) < 32 or ord(c) == 127 for c in node.value):
                    self.error(node, 'E101', 'test name must be nonempty and contain no control characters')
                if node.value in tests:
                    self.error(node, 'E101', f'duplicate test name {node.value!r}')
                tests.add(node.value)
        main = self.functions.get('main')
        if main and (main.type != 'void' or main.children[0]):
            self.error(main, 'E107', 'main must have no parameters and no result', 'Declare fn main() { ... }.')
        if not self.test_mode and not main:
            token = self.source_token or (self.nodes[0].token if self.nodes else Token('', '', '<source>', 1, 1))
            raise Diagnostic(token, 'E107', 'normal build requires fn main()', 'Add fn main() { ... } or use test mode.')
        for node in self.nodes:
            env = {}
            if node.kind == 'fn':
                for param in node.children[0]:
                    self.declare(param, env, param.type, False)
                returns = self.block(node.children[1], env, node.type)
                if node.type != 'void' and not returns:
                    self.error(node, 'E105', f'function {node.value} may finish without returning {node.type}', 'Return a value on every path.')
            else:
                self.block(node.children[0], env, 'test')
        return self.nodes

    def declare(self, node, env, typ, mutable):
        if node.value in env or node.value in self.functions or node.value in BUILTINS:
            self.error(node, 'E101', f'duplicate or shadowing declaration {node.value}', 'Choose a distinct name.')
        env[node.value] = (typ, mutable)
        node.type = typ

    def lookup(self, node, env):
        if node.value not in env:
            self.error(node, 'E100', f'unknown identifier {node.value}', 'Declare the name before using it; check its spelling.')
        return env[node.value]

    def block(self, block, outer, result):
        env = dict(outer)
        returns = False
        for node in block.children:
            if returns:
                self.error(node, 'E105', 'unreachable statement after return')
            returns = self.statement(node, env, result)
        return returns

    def statement(self, node, env, result):
        k = node.kind
        if k in ('let', 'var'):
            value = node.children[0]
            typ = self.expression(value, env)
            if typ == 'void':
                self.error(node, 'E102', 'cannot bind a void result')
            if isinstance(typ, tuple) and (k == 'var' or value.kind != 'array'):
                self.error(node, 'E106', 'arrays require let with an array literal; aliases and mutation are unsupported')
            self.declare(node, env, typ, k == 'var')
        elif k == 'assign':
            typ, mutable = self.lookup(node, env)
            if not mutable:
                self.error(node, 'E104', f'{node.value} is immutable', 'Use var for a mutable scalar binding.')
            self.require(node, self.expression(node.children[0], env), typ)
        elif k == 'expr':
            value = node.children[0]
            if value.kind != 'call':
                self.error(node, 'E105', 'only function calls can be expression statements')
            self.expression(value, env)
        elif k == 'return':
            if result == 'test':
                self.error(node, 'E105', 'return is forbidden inside a test')
            actual = self.expression(node.children[0], env) if node.children else 'void'
            if node.children and actual == 'void':
                self.error(node, 'E102', 'a void call cannot be a return value', 'Use the call as a statement followed by return;.')
            self.require(node, actual, result)
            return True
        elif k in ('if', 'while'):
            self.require(node.children[0], self.expression(node.children[0], env), 'bool')
            yes = self.block(node.children[1], env, result)
            if k == 'if' and node.children[2]:
                other = node.children[2]
                no = self.block(other, env, result) if other.kind == 'block' else self.statement(other, dict(env), result)
                return yes and no
        return False

    def expression(self, node, env):
        k = node.kind
        if k == 'literal':
            if node.token.kind == 'INT':
                # Compare digit strings to avoid Python's large decimal conversion limit.
                digits = node.value.lstrip('0') or '0'
                if len(digits) > 19 or (len(digits) == 19 and digits > '9223372036854775807'):
                    self.error(node, 'E108', 'integer literal exceeds signed 64-bit range')
                node.value = int(digits)
                typ = 'int'
            else:
                typ = 'text' if node.token.kind == 'STRING' else 'bool'
        elif k == 'name':
            typ = self.lookup(node, env)[0]
        elif k == 'unary':
            child = node.children[0]
            if node.value == '-' and child.kind == 'literal' and child.token.kind == 'INT' and (str(child.value).lstrip('0') or '0') == '9223372036854775808':
                node.kind, node.value, node.children = 'literal', -9223372036854775808, []
                typ = 'int'
            else:
                typ = 'bool' if node.value == '!' else 'int'
                self.require(node, self.expression(child, env), typ)
        elif k == 'binary':
            left, right = (self.expression(c, env) for c in node.children)
            op = node.value
            if op in ('==', '!='):
                if left not in SCALARS or right != left:
                    self.error(node, 'E102', 'equality requires two values of the same scalar type')
                typ = 'bool'
            elif op in ('&&', '||'):
                self.require(node, left, 'bool')
                self.require(node, right, 'bool')
                typ = 'bool'
            else:
                self.require(node, left, 'int')
                self.require(node, right, 'int')
                typ = 'bool' if op in ('<', '>', '<=', '>=') else 'int'
        elif k == 'array':
            for child in node.children:
                if self.expression(child, env) != 'int':
                    self.error(child, 'E106', 'array elements must be int')
            typ = ('array', len(node.children))
        elif k == 'index':
            base = self.expression(node.children[0], env)
            if not isinstance(base, tuple):
                self.error(node, 'E106', 'indexing requires an integer array')
            if self.expression(node.children[1], env) != 'int':
                self.error(node, 'E106', 'array index must be int')
            typ = 'int'
        elif k == 'call':
            name = node.value
            if name not in BUILTINS and name not in self.functions:
                self.error(node, 'E100', f'unknown function {name}', 'Declare the function or check its spelling.')
            types = [self.expression(c, env) for c in node.children]
            def arity(n):
                if len(types) != n:
                    self.error(node, 'E103', f'{name} expects {n} arguments, found {len(types)}')
            typ = 'void'
            if name == 'print':
                arity(1)
                if types[0] not in SCALARS:
                    self.error(node, 'E102', 'print requires an int, bool or text')
            elif name == 'read_int':
                arity(0)
                typ = 'int'
            elif name == 'len':
                arity(1)
                if not isinstance(types[0], tuple):
                    self.error(node, 'E106', 'len requires an integer array')
                typ = 'int'
            elif name == 'assert':
                arity(2)
                self.require(node, types[0], 'bool')
                self.require(node, types[1], 'text')
            elif name in ('assert_eq', 'assert_ne'):
                arity(2)
                if types[0] not in SCALARS or types[1] != types[0]:
                    self.error(node, 'E102', f'{name} requires two values of the same scalar type')
            else:
                fn = self.functions[name]
                arity(len(fn.children[0]))
                for actual, param in zip(types, fn.children[0]):
                    self.require(node, actual, param.type)
                typ = fn.type
        else:
            raise AssertionError(k)
        node.type = typ
        return typ
