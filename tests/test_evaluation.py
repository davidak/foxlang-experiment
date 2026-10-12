"""Reproduce ninth-program acceptance without changing the frozen language."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'build/evaluation'
PROGRAM = ROOT/'examples/09-primes/primes.fox'


class IndependentEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        BUILD.mkdir(parents=True, exist_ok=True)

    def test_implementation_and_reference_remain_frozen(self):
        manifest = json.loads((ROOT/'docs/evaluation-freeze.json').read_text())
        for path, expected in manifest.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected)

    def test_prime_output(self):
        binary = BUILD/'primes'
        compiled = subprocess.run([sys.executable, str(ROOT/'fox.py'), 'build', str(PROGRAM), '-o', str(binary)], capture_output=True, timeout=30)
        self.assertEqual((compiled.returncode, compiled.stdout, compiled.stderr), (0, b'', b''))
        self.assertTrue(binary.is_file())
        result = subprocess.run([str(binary)], capture_output=True, timeout=10)
        expected = b'2\n3\n5\n7\n11\n13\n17\n19\n23\n29\n'
        self.assertEqual((ROOT/'examples/09-primes/expected.txt').read_bytes(), expected)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, b''))

    def test_prime_native_tests(self):
        result = subprocess.run([sys.executable, str(ROOT/'fox.py'), 'test', str(PROGRAM), '-o', str(BUILD/'prime-tests')], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b'')
        self.assertEqual(result.stdout.count(b'PASS '), 13)
        self.assertTrue(result.stdout.endswith(b'13 passed; 0 failed\n'), result.stdout)


if __name__ == '__main__':
    unittest.main()
