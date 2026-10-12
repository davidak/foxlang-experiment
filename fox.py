#!/usr/bin/env python3
"""FoxLang command-line compiler. Uses only the Python standard library."""
import argparse
from contextlib import suppress
import os
from pathlib import Path
import subprocess
import sys
from compiler.frontend import Parser, Diagnostic, Token
from compiler.semantics import Checker
from compiler.backend import Emitter

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compile FoxLang to C and a native executable.')
    parser.add_argument('command', choices=['build', 'test'])
    parser.add_argument('source', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    args = parser.parse_args(argv)
    output = (args.output or Path('build/tests' if args.command == 'test' else 'build/program')).absolute()
    cfile = Path(str(output) + '.c')
    location = Token('', '', str(args.source), 1, 1)
    try:
        if args.source.resolve() in (output.resolve(), cfile.resolve()):
            raise Diagnostic(location, 'E900', 'output path would overwrite source', 'Choose an output path under build/.')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        cfile.unlink(missing_ok=True)
        nodes = Parser(args.source.read_text(encoding='utf-8'), str(args.source)).parse()
        library = ROOT / 'stdlib/testing.fox'
        if library.exists():
            nodes = Parser(library.read_text(encoding='utf-8'), str(library)).parse() + nodes
        Checker(nodes, args.command == 'test', location).check()
        runtime = (ROOT / 'compiler/runtime.c').read_text()
        cfile.write_text(Emitter(nodes, runtime, args.command == 'test').emit(), encoding='utf-8')
        result = subprocess.run([os.environ.get('CC', 'cc'), '-std=c11', '-O0', str(cfile), '-o', str(output)], capture_output=True, text=True)
        if result.returncode:
            output.unlink(missing_ok=True)
            raise Diagnostic(location, 'E900', f'C backend failed (exit {result.returncode}):\n{result.stderr.strip()}')
        if not output.is_file():
            raise Diagnostic(location, 'E900', 'C backend reported success but produced no executable')
        if args.command == 'test':
            return subprocess.run([str(output)]).returncode
        return 0
    except Diagnostic as error:
        print(error, file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        with suppress(OSError):
            output.unlink(missing_ok=True)
        print(Diagnostic(location, 'E900', str(error)), file=sys.stderr)
        return 1
    except RecursionError:
        print(Diagnostic(location, 'E002', 'source nesting exceeds compiler resource limit'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
