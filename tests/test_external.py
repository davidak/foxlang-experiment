"""Black-box compiler verification; does not depend on FoxLang assertions."""
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build/external'


class External(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        BUILD.mkdir(parents=True, exist_ok=True)

    def compile(self, source, name='case', command='build'):
        if isinstance(source, str):
            path = BUILD / f'{name}.fox'
            path.write_text(source)
        else:
            path = source
        binary = BUILD / name
        result = subprocess.run([sys.executable, str(ROOT / 'fox.py'), command, str(path), '-o', str(binary)], capture_output=True, timeout=30)
        return result, binary, path

    def run_source(self, source, name='case', input=b''):
        result, binary, _ = self.compile(source, name)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertTrue(binary.is_file())
        return subprocess.run([str(binary)], input=input, capture_output=True, timeout=10)

    def test_evaluation_order(self):
        source = '''fn mark(n: int) -> int { print(n); return n; }
fn pair(a: int, b: int) -> int { return a * 10 + b; }
fn main() {
    print(pair(mark(1), mark(2)));
    print(mark(3) + mark(4));
    print([mark(5), mark(6)][mark(0)]);
    print(len([mark(7), mark(8)]));
    var x = 0;
    while x < 2 { print(x); x = x + 1; }
    print(false && 1 / 0 == 0);
    print(true || 1 / 0 == 0);
}'''
        ran = self.run_source(source, 'order')
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, b'1\n2\n12\n3\n4\n7\n5\n6\n0\n5\n7\n8\n2\n0\n1\nfalse\ntrue\n', b''))

    def test_forward_mutual_calls_and_text(self):
        ran = self.run_source('''fn odd(n: int) -> bool { if n == 0 { return false; } return even(n - 1); }
fn label(value: text) -> text { return value; }
fn even(n: int) -> bool { if n == 0 { return true; } return odd(n - 1); }
fn main() { print(even(8)); print(odd(9)); print(label("héllo 🦊")); print(label("fox") == "fox"); }''', 'mutual')
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, 'true\ntrue\nhéllo 🦊\ntrue\n'.encode(), b''))

    def test_arithmetic_against_python(self):
        rng = random.Random(764)
        expressions, expected = [], []
        for _ in range(50):
            a, b = rng.randint(-1000000, 1000000), rng.choice([i for i in range(-20, 21) if i])
            quotient = (abs(a) // abs(b)) * (-1 if (a < 0) != (b < 0) else 1)
            for op, value in [('+', a+b), ('-', a-b), ('*', a*b), ('/', quotient), ('%', a-quotient*b)]:
                expressions.append(f'print(({a}) {op} ({b}));')
                expected.append(str(value))
        ran = self.run_source('fn main() {\n'+'\n'.join(expressions)+'\n}', 'arithmetic')
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, ('\n'.join(expected)+'\n').encode(), b''))

    def test_integer_read_boundaries(self):
        result, binary, _ = self.compile('fn main() { print(read_int()); }', 'read-boundaries')
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in [-(2**63), 2**63-1, 0, -1, 1]:
            with self.subTest(value=value):
                ran = subprocess.run([str(binary)], input=str(value).encode(), capture_output=True)
                self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, f'{value}\n'.encode(), b''))

    def test_backend_failure(self):
        source = BUILD / 'backend.fox'
        source.write_text('fn main() {}')
        binary = BUILD / 'backend'
        ran = subprocess.run([sys.executable, str(ROOT/'fox.py'), 'build', str(source), '-o', str(binary)], env={**os.environ, 'CC': '/no/such/cc'}, capture_output=True)
        self.assertEqual(ran.returncode, 1)
        self.assertIn(b'E900', ran.stderr)
        self.assertFalse(binary.exists())

    def test_source_protected(self):
        source = BUILD / 'protected.fox'
        content = 'fn main() {}'
        source.write_text(content)
        ran = subprocess.run([sys.executable, str(ROOT/'fox.py'), 'build', str(source), '-o', str(source)], capture_output=True)
        self.assertEqual(ran.returncode, 1)
        self.assertEqual(source.read_text(), content)

    def test_missing_file(self):
        ran, binary, _ = self.compile(BUILD / 'absent.fox', 'missing')
        self.assertEqual(ran.returncode, 1)
        self.assertIn(b'E900', ran.stderr)
        self.assertFalse(binary.exists())

    def test_output_io_error(self):
        ran, binary, _ = self.compile('fn main() { print("x"); }', 'write-error')
        self.assertEqual(ran.returncode, 0, ran.stderr)
        with open('/dev/full', 'wb') as sink:
            ran = subprocess.run([str(binary)], stdout=sink, stderr=subprocess.PIPE)
        self.assertEqual(ran.returncode, 2)
        self.assertIn(b'R005', ran.stderr)

    def test_input_io_error(self):
        ran, binary, _ = self.compile('fn main() { print(read_int()); }', 'read-error')
        self.assertEqual(ran.returncode, 0, ran.stderr)
        fd = os.open(BUILD, os.O_RDONLY)
        try:
            ran = subprocess.run([str(binary)], stdin=fd, capture_output=True)
        finally:
            os.close(fd)
        self.assertEqual(ran.returncode, 2)
        self.assertIn(b'R005', ran.stderr)


def example_test(directory):
    def test(self):
        result, binary, _ = self.compile(directory/'main.fox', directory.name)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b'')
        self.assertTrue(binary.is_file())
        input_file = directory/'input.txt'
        ran = subprocess.run([str(binary)], input=input_file.read_bytes() if input_file.exists() else b'', capture_output=True, timeout=10)
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, (directory/'expected.txt').read_bytes(), b''))
    return test


def invalid_test(name, expected):
    def test(self):
        # Seed a stale executable to verify rejection cannot retain it.
        binary = BUILD / name
        binary.write_text('stale')
        result, binary, source = self.compile(ROOT/'tests/invalid'/f'{name}.fox', name)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(binary.exists())
        diagnostic = result.stderr.decode()
        prefix = f"{source}:{expected['line']}:{expected['column']}: error[{expected['code']}]: "
        self.assertTrue(diagnostic.startswith(prefix), diagnostic)
        self.assertGreater(len(diagnostic.splitlines()[0][len(prefix):]), 12)
        self.assertNotIn('Traceback', diagnostic)
        if expected['hint']:
            self.assertIn('hint: ', diagnostic)
    return test


def square_test(data, value, code):
    def test(self):
        ran = self.run_source(ROOT/'examples/08-square/main.fox', self._testMethodName, data)
        if code:
            self.assertEqual(ran.returncode, 2)
            self.assertEqual(ran.stdout, b'')
            self.assertIn(code.encode(), ran.stderr)
            self.assertIn(b'main.fox:', ran.stderr)
        else:
            self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, f'{value}\n'.encode(), b''))
    return test


def runtime_test(expression, code):
    def test(self):
        ran = self.run_source(f'fn main() {{\n    print({expression});\n}}', self._testMethodName)
        self.assertEqual(ran.returncode, 2)
        self.assertEqual(ran.stdout, b'')
        self.assertIn(f'error[{code}]'.encode(), ran.stderr)
        self.assertIn(b'.fox:2:', ran.stderr)
    return test


for directory in sorted((ROOT/'examples').glob('0[1-8]-*')):
    setattr(External, 'test_example_'+directory.name.replace('-', '_'), example_test(directory))
for name, expected in json.loads((ROOT/'tests/invalid/expected.json').read_text()).items():
    setattr(External, 'test_invalid_'+name, invalid_test(name, expected))
for i, (data, value, code) in enumerate([
    (b'0', 0, None), (b'-12\n', 144, None), (b' +12 \t\r\n\v\f', 144, None),
    (b'-0', 0, None), (b'00012', 144, None),
    (b'3037000499', 9223372030926249001, None), (b'-3037000499', 9223372030926249001, None),
    (b'', None, 'R004'), (b' \n', None, 'R004'), (b'+', None, 'R004'),
    (b'12x', None, 'R004'), (b'1 2', None, 'R004'), (b'1\x00', None, 'R004'),
    (b'\xff', None, 'R004'), (b'--1', None, 'R004'), (b'1.0', None, 'R004'),
    (b'9223372036854775808', None, 'R004'), (b'-9223372036854775809', None, 'R004'),
    (b'9'*10000, None, 'R004'), (b'3037000500', None, 'R001'),
    (b'-3037000500', None, 'R001'), (b'-9223372036854775808', None, 'R001'),
    (b'9223372036854775807', None, 'R001')]):
    setattr(External, f'test_square_{i:02}', square_test(data, value, code))
for name, expression, code in [
    ('add', '9223372036854775807 + 1', 'R001'),
    ('sub', '-9223372036854775808 - 1', 'R001'),
    ('mul', '9223372036854775807 * 2', 'R001'),
    ('neg', '-(-9223372036854775808)', 'R001'),
    ('div', '-9223372036854775808 / -1', 'R001'),
    ('rem', '-9223372036854775808 % -1', 'R001'),
    ('zero_div', '1 / 0', 'R002'), ('zero_rem', '1 % 0', 'R002'),
    ('negative_index', '[1][-1]', 'R003'), ('large_index', '[1][1]', 'R003')]:
    setattr(External, 'test_runtime_'+name, runtime_test(expression, code))

if __name__ == '__main__':
    unittest.main()
