"""C emission. Expression temporaries preserve FoxLang evaluation order."""
import json
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
        else:
            raise Diagnostic(node.token, 'E900', f'compiler milestone does not yet emit {node.kind}')

    def expression(self, node):
        if node.kind == 'literal' and node.type == 'text':
            return cstring(node.value)
        if node.kind == 'call' and node.value == 'print' and node.children[0].type == 'text':
            value = self.expression(node.children[0])
            self.line(f'rt_print_text({value}, {self.location(node)});')
            return ''
        raise Diagnostic(node.token, 'E900', f'compiler milestone does not yet emit {node.kind}')
