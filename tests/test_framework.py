"""The native framework's independent acceptance suite, including failures."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'build/framework'


class Framework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        BUILD.mkdir(parents=True, exist_ok=True)

    def run_fox(self, path, command='test', input=b''):
        return subprocess.run([sys.executable, str(ROOT/'fox.py'), command, str(path), '-o', str(BUILD/path.stem)], input=input, capture_output=True, timeout=30)

    def test_language(self):
        result = self.run_fox(ROOT/'tests/native/language.fox')
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b'')
        self.assertEqual(result.stdout.count(b'PASS '), 16)
        self.assertTrue(result.stdout.endswith(b'16 passed; 0 failed\n'))

    def test_smoke(self):
        result = self.run_fox(ROOT/'tests/native/smoke.fox')
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'PASS all assertion forms\n1 passed; 0 failed\n', b''))

    def test_stdlib(self):
        result = self.run_fox(ROOT/'tests/native/stdlib.fox')
        expected = ('9223372036854775807\n-9223372036854775808\ntrue\nfalse\nfox 🦊\n\n'
                    'PASS print every scalar type and empty text\n'
                    'PASS len single and multiple elements\n'
                    'PASS assertion library scalar overloads\n3 passed; 0 failed\n').encode()
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, b''))

    def test_read_int(self):
        result = self.run_fox(ROOT/'tests/framework/read_int.fox', input=b' \t-12\n')
        expected = b'PASS read_int representative signed input\n1 passed; 0 failed\n'
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, b''))

    def test_mixed(self):
        path = ROOT/'tests/framework/mixed.fox'
        result = self.run_fox(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count(b'PASS '), 2)
        self.assertEqual(result.stdout.count(b'FAIL '), 10)
        self.assertTrue(result.stdout.endswith(b'2 passed; 10 failed\n'))
        self.assertNotIn(b'UNREACHABLE', result.stdout)
        self.assertNotIn(b'normal main', result.stdout)
        diagnostics = result.stderr.decode().splitlines()
        self.assertEqual(len(diagnostics), 10)
        lines = [10, 15, 19, 23, 27, 31, 35, 39, 43, 47]
        for diagnostic, line in zip(diagnostics, lines):
            self.assertTrue(diagnostic.startswith(f'{path}:{line}:5: assertion failed in '), diagnostic)
        for text in ['expected true', 'expected false', 'actual=1, expected=2',
                     'actual=3, expected=3', 'actual=true, expected=false',
                     'actual=true, expected=true', 'actual="fox", expected="wolf"',
                     'actual="fox", expected="fox"', 'custom reason', 'intentional reason']:
            self.assertIn(text, result.stderr.decode())

    def test_normal_main_excludes_tests(self):
        result = self.run_fox(ROOT/'tests/framework/mixed.fox', 'build')
        self.assertEqual(result.returncode, 0, result.stderr)
        ran = subprocess.run([str(BUILD/'mixed')], capture_output=True)
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, b'normal main only\n', b''))

    def test_empty(self):
        result = self.run_fox(ROOT/'tests/framework/empty.fox')
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'0 passed; 0 failed\n', b''))

    def test_runtime_fault_stops_suite(self):
        result = self.run_fox(ROOT/'tests/framework/fatal.fox')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertIn(b'R002', result.stderr)
        self.assertNotIn(b'never reached', result.stderr)

    def test_assertion_in_normal_program(self):
        path = BUILD/'assertion.fox'
        path.write_text('fn main() { fail("normal failure"); }')
        result = self.run_fox(path, 'build')
        self.assertEqual(result.returncode, 0, result.stderr)
        ran = subprocess.run([str(BUILD/'assertion')], capture_output=True)
        self.assertEqual(ran.returncode, 1)
        self.assertIn(f'{path}:1:13: assertion failed in <program>: normal failure'.encode(), ran.stderr)

    def test_helper_failure_location_and_abort(self):
        path = BUILD/'helper.fox'
        path.write_text('fn helper() {\n    assert_eq(3, 4);\n}\ntest "caller" { helper(); print("BAD"); }\ntest "next" {}')
        result = self.run_fox(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b'FAIL caller\nPASS next\n1 passed; 1 failed\n')
        self.assertIn(f'{path}:2:5: assertion failed in caller:'.encode(), result.stderr)

    def test_invalid_test_body_checked_in_normal_mode(self):
        path = BUILD/'invalid-test.fox'
        path.write_text('fn main() {}\ntest "invalid" { assert_true(1); }')
        result = self.run_fox(path, 'build')
        self.assertEqual(result.returncode, 1)
        self.assertIn(f'{path}:2:18: error[E102]'.encode(), result.stderr)
        self.assertFalse((BUILD/path.stem).exists())

    def test_gcd_contract(self):
        result = self.run_fox(ROOT/'examples/05-gcd/main.fox')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.endswith(b'2 passed; 0 failed\n'))

    def test_fibonacci_contract(self):
        result = self.run_fox(ROOT/'examples/06-fibonacci/main.fox')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.endswith(b'1 passed; 0 failed\n'))


if __name__ == '__main__':
    unittest.main()
