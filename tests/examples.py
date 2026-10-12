"""Initial executable requirements, independent of native assertions."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def verify(count=8):
    for directory in sorted((ROOT / 'examples').glob('0[1-8]-*'))[:count]:
        binary = ROOT / 'build' / directory.name
        compiled = subprocess.run([sys.executable, str(ROOT / 'fox.py'), 'build', str(directory / 'main.fox'), '-o', str(binary)], capture_output=True)
        assert compiled.returncode == 0, compiled.stderr.decode()
        assert binary.is_file()
        input_file = directory / 'input.txt'
        ran = subprocess.run([str(binary)], input=input_file.read_bytes() if input_file.exists() else b'', capture_output=True, timeout=10)
        assert (ran.returncode, ran.stdout, ran.stderr) == (0, (directory / 'expected.txt').read_bytes(), b''), (directory, ran)
        print(f'PASS {directory.name}')


if __name__ == '__main__':
    verify(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
