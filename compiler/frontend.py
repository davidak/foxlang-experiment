"""Source locations, lexer and recursive-descent parser."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    path: str
    line: int
    column: int

    @property
    def location(self):
        return f"{self.path}:{self.line}:{self.column}"


class Diagnostic(Exception):
    def __init__(self, token, code, message, hint=None):
        self.token, self.code, self.message, self.hint = token, code, message, hint

    def __str__(self):
        result = f"{self.token.location}: error[{self.code}]: {self.message}"
        return result + (f"\nhint: {self.hint}" if self.hint else "")


@dataclass
class Node:
    kind: str
    token: Token
    value: object = None
    children: list = field(default_factory=list)
    type: object = None


KEYWORDS = set('fn let var if else while return test true false int bool text'.split())


def lex(source, path):
    tokens = []
    i, line, column = 0, 1, 1

    def advance():
        nonlocal i, line, column
        if source[i] == '\n':
            line, column = line + 1, 1
        else:
            column += 1
        i += 1

    while i < len(source):
        c = source[i]
        start = Token('', '', path, line, column)
        if c in ' \t\r\n\v\f':
            advance()
            continue
        if source.startswith('//', i):
            while i < len(source) and source[i] != '\n':
                advance()
            continue
        if c.isascii() and (c.isalpha() or c == '_'):
            begin = i
            while i < len(source) and source[i].isascii() and (source[i].isalnum() or source[i] == '_'):
                advance()
            value = source[begin:i]
            kind = value if value in KEYWORDS else 'IDENT'
        elif c in '0123456789':
            begin = i
            while i < len(source) and source[i] in '0123456789':
                advance()
            kind, value = 'INT', source[begin:i]
        elif c == '"':
            advance()
            value = ''
            while i < len(source) and source[i] != '"':
                if ord(source[i]) < 32 or ord(source[i]) == 127:
                    raise Diagnostic(start, 'E001', 'control character in text literal', 'Use a supported escape such as \\n.')
                if source[i] == '\\':
                    advance()
                    escapes = {'n': '\n', 'r': '\r', 't': '\t', '"': '"', '\\': '\\'}
                    if i == len(source) or source[i] not in escapes:
                        raise Diagnostic(start, 'E001', 'unsupported or incomplete text escape')
                    value += escapes[source[i]]
                else:
                    value += source[i]
                advance()
            if i == len(source):
                raise Diagnostic(start, 'E001', 'unterminated text literal', 'Add a closing double quote.')
            advance()
            kind = 'STRING'
        else:
            pair = source[i:i + 2]
            if pair in ('->', '==', '!=', '<=', '>=', '&&', '||'):
                kind = value = pair
                advance()
                advance()
            elif c in '(){}[],:;=+-*/%<>!':
                kind = value = c
                advance()
            else:
                raise Diagnostic(start, 'E001', f'unexpected character {c!r}')
        tokens.append(Token(kind, value, path, start.line, start.column))
    tokens.append(Token('EOF', '', path, line, column))
    return tokens


class Parser:
    PRECEDENCE = {'||': 1, '&&': 2, '==': 3, '!=': 3, '<': 4, '<=': 4,
                  '>': 4, '>=': 4, '+': 5, '-': 5, '*': 6, '/': 6, '%': 6}

    def __init__(self, source, path):
        self.tokens = lex(source, path)
        self.i = 0

    @property
    def token(self):
        return self.tokens[self.i]

    def accept(self, kind):
        if self.token.kind == kind:
            token = self.token
            self.i += 1
            return token
        return None

    def expect(self, kind):
        token = self.accept(kind)
        if token is None:
            raise Diagnostic(self.token, 'E002', f'expected {kind}, found {self.token.kind}', f'Use {kind} here.')
        return token

    def scalar(self):
        if self.token.kind not in ('int', 'bool', 'text'):
            raise Diagnostic(self.token, 'E002', 'expected scalar type int, bool or text')
        token = self.token
        self.i += 1
        return token.value

    def parse(self):
        nodes = []
        while self.token.kind != 'EOF':
            if token := self.accept('fn'):
                name = self.expect('IDENT')
                self.expect('(')
                params = []
                if self.token.kind != ')':
                    while True:
                        param = self.expect('IDENT')
                        self.expect(':')
                        params.append(Node('param', param, param.value, type=self.scalar()))
                        if not self.accept(','):
                            break
                self.expect(')')
                result = self.scalar() if self.accept('->') else 'void'
                nodes.append(Node('fn', name, name.value, [params, self.block()], result))
            elif token := self.accept('test'):
                name = self.expect('STRING')
                nodes.append(Node('test', name, name.value, [self.block()]))
            else:
                raise Diagnostic(self.token, 'E002', 'expected a function or test declaration')
        return nodes

    def block(self):
        token = self.expect('{')
        nodes = []
        while self.token.kind not in ('}', 'EOF'):
            nodes.append(self.statement())
        self.expect('}')
        return Node('block', token, children=nodes)

    def statement(self):
        token = self.token
        if token.kind in ('let', 'var'):
            self.i += 1
            name = self.expect('IDENT')
            self.expect('=')
            value = self.expression()
            self.expect(';')
            return Node(token.kind, name, name.value, [value])
        if self.accept('if'):
            condition = self.expression()
            yes = self.block()
            no = None
            if self.accept('else'):
                no = self.statement() if self.token.kind == 'if' else self.block()
            return Node('if', token, children=[condition, yes, no])
        if self.accept('while'):
            condition = self.expression()
            return Node('while', token, children=[condition, self.block()])
        if self.accept('return'):
            value = [] if self.token.kind == ';' else [self.expression()]
            self.expect(';')
            return Node('return', token, children=value)
        if token.kind == 'IDENT' and self.tokens[self.i + 1].kind == '=':
            self.i += 2
            value = self.expression()
            self.expect(';')
            return Node('assign', token, token.value, [value])
        value = self.expression()
        self.expect(';')
        return Node('expr', token, children=[value])

    def expression(self, minimum=1):
        left = self.unary()
        while self.PRECEDENCE.get(self.token.kind, 0) >= minimum:
            operator = self.token
            self.i += 1
            right = self.expression(self.PRECEDENCE[operator.kind] + 1)
            left = Node('binary', operator, operator.kind, [left, right])
        return left

    def unary(self):
        if self.token.kind in ('-', '!'):
            token = self.token
            self.i += 1
            return Node('unary', token, token.kind, [self.unary()])
        node = self.primary()
        while token := self.accept('['):
            index = self.expression()
            self.expect(']')
            node = Node('index', token, children=[node, index])
        return node

    def primary(self):
        token = self.token
        self.i += 1
        if token.kind in ('INT', 'STRING', 'true', 'false'):
            return Node('literal', token, token.value)
        if token.kind == 'IDENT':
            if not self.accept('('):
                return Node('name', token, token.value)
            args = []
            if self.token.kind != ')':
                args.append(self.expression())
                while self.accept(','):
                    args.append(self.expression())
            self.expect(')')
            return Node('call', token, token.value, args)
        if token.kind == '(':
            node = self.expression()
            self.expect(')')
            return node
        if token.kind == '[':
            if self.token.kind == ']':
                raise Diagnostic(token, 'E106', 'empty arrays are unsupported', 'Provide at least one integer element.')
            items = [self.expression()]
            while self.accept(','):
                items.append(self.expression())
            self.expect(']')
            return Node('array', token, children=items)
        raise Diagnostic(token, 'E002', f'expected expression, found {token.kind}')
