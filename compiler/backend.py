"""C emission. Expression temporaries preserve FoxLang evaluation order."""
from pathlib import Path
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
                self.library = node.token.path == str(Path(__file__).resolve().parents[1] / 'stdlib/testing.fox')
                self.line(self.signature(node) + ' {')
                self.block(node.children[1])
                self.line('}')
        self.library = False
        tests = [node for node in self.nodes if node.kind == 'test']
        if self.test_mode:
            for i, node in enumerate(tests):
                self.line(f'static void test_{i}(void) {{')
                self.block(node.children[0])
                self.line('}')
        self.line('int main(void) {')
        self.line('rt_start();')
        if self.test_mode:
            self.line('static int passed = 0, failed = 0;')
            for i, node in enumerate(tests):
                self.line(f'rt_test_name = {cstring(node.value)};')
                self.line('rt_testing = true;')
                self.line('if (setjmp(rt_jump) == 0) {')
                self.line(f'test_{i}();')
                self.line('passed++; printf("PASS %s\\n", rt_test_name);')
                self.line('} else {')
                self.line('failed++; printf("FAIL %s\\n", rt_test_name);')
                self.line('}')
            self.line('printf("%d passed; %d failed\\n", passed, failed);')
            self.line('if (fflush(stdout) == EOF) rt_error("<runner>", "R005", "could not write test results");')
            self.line('return failed ? 1 : 0;')
        else:
            self.line('f_main("<entry>");')
            self.line('return 0;')
        self.line('}')
        return '\n'.join(self.lines) + '\n'

    def block(self, node):
        for statement in node.children:
            self.statement(statement)

    def statement(self, node):
        if node.kind == 'expr':
            self.expression(node.children[0])
        elif node.kind in ('let', 'var'):
            value = self.expression(node.children[0])
            ctype = 'const int64_t *' if isinstance(node.type, tuple) else self.CTYPES[node.type]
            self.line(f'{ctype} v_{node.value} = {value};')
        elif node.kind == 'return':
            value = self.expression(node.children[0]) if node.children else ''
            self.line(f'return {value};')
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
            raise Diagnostic(node.token, 'E900', f'internal compiler error: unsupported statement {node.kind}')

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
            if isinstance(node.type, tuple):
                return f'v_{node.value}'
            name = self.temporary()
            self.line(f'{self.CTYPES[node.type]} {name} = v_{node.value};')
            return name
        if k == 'array':
            values = [self.expression(c) for c in node.children]
            name = self.temporary()
            self.line(f'const int64_t {name}[] = {{{", ".join(values)}}};')
            return name
        if k == 'index':
            base = self.expression(node.children[0])
            index = self.expression(node.children[1])
            length = node.children[0].type[1]
            name = self.temporary()
            self.line(f'int64_t {name} = {base}[rt_index({index}, {length}, {self.location(node)})];')
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
        elif k == 'call' and node.value in ('assert', 'assert_eq', 'assert_ne'):
            args = [self.expression(c) for c in node.children]
            if node.value == 'assert':
                self.line(f'rt_assert({args[0]}, {args[1]}, {self.location(node)});')
            else:
                equal = 'true' if node.value == 'assert_eq' else 'false'
                self.line(f'rt_compare_{node.children[0].type}({args[0]}, {args[1]}, {equal}, {self.location(node)});')
            return ''
        elif k == 'call' and node.value == 'read_int':
            code = f'rt_read_int({self.location(node)})'
        elif k == 'call' and node.value == 'len':
            self.expression(node.children[0])
            return f'INT64_C({node.children[0].type[1]})'
        elif k == 'call':
            args = [self.expression(c) for c in node.children]
            args.append(self.location(node))
            code = f'f_{node.value}({", ".join(args)})'
            if node.type == 'void':
                self.line(code + ';')
                return ''
        else:
            raise Diagnostic(node.token, 'E900', f'internal compiler error: unsupported expression {k}')
        name = self.temporary()
        self.line(f'{self.CTYPES[node.type]} {name} = {code};')
        return name
