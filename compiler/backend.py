"""C emission. Expression temporaries preserve FoxLang evaluation order."""
from .frontend import Diagnostic


def cstring(value):
    # Octal UTF-8 bytes avoid C's variable-length hexadecimal escapes.
    return '"' + ''.join(chr(b) if 32 <= b < 127 and b not in (34, 92) else f'\\{b:03o}' for b in value.encode('utf-8')) + '"'


class Emitter:
    CTYPES = {'int': 'int64_t', 'bool': 'bool', 'text': 'const char *', 'void': 'void'}

    def __init__(self, nodes, runtime, test_mode=False):
        self.nodes, self.runtime, self.test_mode = nodes, runtime, test_mode
        self.lines = []
        self.serial = 0
        self.library = False

    def line(self, text):
        self.lines.append(text)

    def temporary(self):
        self.serial += 1
        return f't_{self.serial}'

    def location(self, node):
        return 'call_location' if self.library else cstring(node.token.location)

    def signature(self, node):
        args = [f'{self.CTYPES[p.type]} v_{p.value}' for p in node.children[0]]
        args.append('const char *call_location')
        return f'{self.CTYPES[node.type]} f_{node.value}({", ".join(args)})'

    def emit(self):
        self.line(self.runtime)
        for node in self.nodes:
            if node.kind == 'fn':
                self.line(self.signature(node) + ';')
        for node in self.nodes:
            if node.kind == 'fn':
                self.library = node.token.path.endswith('/stdlib/testing.fox')
                self.line(self.signature(node) + ' {')
                self.block(node.children[1])
                self.line('}')
        self.line('int main(void) {')
        self.line('f_main("<entry>");')
        self.line('return 0;\n}')
        return '\n'.join(self.lines) + '\n'

    def block(self, node):
        for statement in node.children:
            self.statement(statement)

    def statement(self, node):
        if node.kind == 'expr':
            self.expression(node.children[0])
        elif node.kind in ('let', 'var'):
            value = self.expression(node.children[0])
            self.line(f'{self.CTYPES[node.type]} v_{node.value} = {value};')
        elif node.kind == 'assign':
            value = self.expression(node.children[0])
            self.line(f'v_{node.value} = {value};')
        elif node.kind == 'while':
            self.line('while (true) {')
            condition = self.expression(node.children[0])
            self.line(f'if (!({condition})) break;')
            self.block(node.children[1])
            self.line('}')
        elif node.kind == 'if':
            condition = self.expression(node.children[0])
            self.line(f'if ({condition}) {{')
            self.block(node.children[1])
            self.line('}')
            if node.children[2]:
                self.line('else {')
                other = node.children[2]
                if other.kind == 'block':
                    self.block(other)
                else:
                    self.statement(other)
                self.line('}')
        else:
            raise Diagnostic(node.token, 'E900', f'compiler milestone does not yet emit {node.kind}')

    def expression(self, node):
        k = node.kind
        if k == 'literal':
            if node.type == 'text':
                return cstring(node.value)
            if node.type == 'bool':
                return node.value
            if node.value == -9223372036854775808:
                return 'INT64_MIN'
            return f'INT64_C({node.value})'
        if k == 'name':
            name = self.temporary()
            self.line(f'{self.CTYPES[node.type]} {name} = v_{node.value};')
            return name
        if k == 'binary' and node.value in ('&&', '||'):
            left = self.expression(node.children[0])
            name = self.temporary()
            self.line(f'bool {name} = {left};')
            condition = name if node.value == '&&' else f'!{name}'
            self.line(f'if ({condition}) {{')
            right = self.expression(node.children[1])
            self.line(f'{name} = {right};')
            self.line('}')
            return name
        if k == 'binary':
            left, right = [self.expression(c) for c in node.children]
            names = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'rem'}
            if node.value in names:
                code = f'rt_{names[node.value]}({left}, {right}, {self.location(node)})'
            elif node.children[0].type == 'text':
                code = f'(strcmp({left}, {right}) {node.value} 0)'
            else:
                code = f'({left} {node.value} {right})' 
        elif k == 'unary':
            child = self.expression(node.children[0])
            code = f'(!{child})' if node.value == '!' else f'rt_sub(0, {child}, {self.location(node)})'
        elif k == 'call' and node.value == 'print':
            child = node.children[0]
            value = self.expression(child)
            self.line(f'rt_print_{child.type}({value}, {self.location(node)});')
            return ''
        elif k == 'call':
            args = [self.expression(c) for c in node.children]
            args.append(self.location(node))
            code = f'f_{node.value}({", ".join(args)})'
            if node.type == 'void':
                self.line(code + ';')
                return ''
        else:
            raise Diagnostic(node.token, 'E900', f'compiler milestone does not yet emit {k}')
        name = self.temporary()
        self.line(f'{self.CTYPES[node.type]} {name} = {code};')
        return name
