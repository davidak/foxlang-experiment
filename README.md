# FoxLang

FoxLang is a small compiled language developed from progressively more demanding
programs. This experiment specifies programs first, designs only the features
they require, writes the programs before the compiler, then verifies a general
Python-to-C compiler and a native test framework. It is a working experimental
foundation, not yet a games or simulation production language.

The language has checked signed 64-bit integers, booleans, immutable text,
mutable scalar locals, functions and recursion, conditionals, loops, immutable
integer arrays, strict integer input, and dedicated named unit tests. See the
[language reference](docs/language.md), [standard API](docs/stdlib.md), and
[architecture decisions](docs/adr).

## Development environment

Enter the pinned Nix shell from the repository root:

```sh
nix-shell --pure
```

It supplies Python 3, GCC and Git. Python uses only its standard library; no
pip install or compiler bootstrap is needed. The release archive URL and its
unpacked SHA-256 are pinned in [shell.nix](shell.nix). Downloads require network
access unless cached. The tested host is x86_64 Linux. Nix fixes the dependency
source, not every build input: target platform, environment, source paths,
`CC` overrides and toolchain behavior still affect binaries. Builds are not
claimed bit-for-bit reproducible. `CC` can name one GCC-compatible executable,
not a shell command or flags.

## Build, run and test

Inside the shell, from the repository root:

```sh
python3 fox.py build examples/01-hello/main.fox -o build/hello
./build/hello
python3 fox.py build examples/08-square/main.fox -o build/square
printf '12\n' | ./build/square
python3 tests/examples.py
python3 -m unittest discover -s tests -v
python3 fox.py test tests/native/language.fox
python3 fox.py test tests/native/stdlib.fox
python3 fox.py test examples/05-gcd/main.fox
python3 fox.py build examples/09-primes/primes.fox -o build/primes
./build/primes
python3 fox.py test examples/09-primes/primes.fox
```

The full external suite compiles and runs every initial example, tests invalid
source and runtime failures, runs native feature/library tests, and independently
checks intentionally failing framework fixtures. Expected fixture failures are
successful external tests; they do not mean the verification suite failed.
The native standard-library suite needs no stdin. The external suite supplies
input automatically for the separate `read_int()` integration fixture.

The compiler writes C beside the requested executable (`build/hello.c` above).
Build artifacts and caches are ignored by Git. Without `-o`, output defaults to
`build/program` for build and `build/tests` for test. A failed compilation removes
stale outputs. Square reads through EOF; pipe input or send EOF interactively.

## Writing native tests

Place dedicated test declarations beside the functions they exercise:

```text
fn twice(n: int) -> int {
    return n * 2;
}

test "twice" {
    assert_eq(twice(6), 12);
    assert_ne(twice(6), 0);
    assert_true(twice(1) > 0);
    assert_false(twice(0) > 0);
    assert(true, "custom failure explanation");
    // fail("explicit failure explanation");
}
```

Run `python3 fox.py test path/to/file.fox`. No main is needed for tests.
Normal builds require `fn main()` and never execute tests. The runner reports
individual names, failure locations and final counts; failures return status 1.
Runtime faults return 2 and stop the suite. Test discovery is the declarations
in the one named file. See [testing](docs/testing.md) for details.

## Repository map

| Path | Contents |
| --- | --- |
| `fox.py` | CLI driver |
| `compiler/` | Lexer/parser, semantic checker, C emitter and C runtime |
| `stdlib/` | Reusable assertion wrappers written in FoxLang |
| `examples/01-hello` through `08-square` | Independent specs, FoxLang source, exact outputs and input fixtures |
| `examples/09-primes/` | Fresh-agent prime specification, prewritten native tests and implementation |
| `tests/invalid/` | Invalid sources and expected diagnostic identifiers/locations |
| `tests/native/` | Native language and standard-library tests |
| `tests/framework/` | Runner fixtures, including deliberate failures and input integration |
| `tests/test_*.py` | Independent black-box verification |
| `docs/` | Reference, API, testing guide, development record, evaluation and ADRs |
| `build/` | Ignored generated C, executables and verification output |

The initial examples are Hello World, Basic Arithmetic, Number Classification,
FizzBuzz, Greatest Common Divisor, recursive Fibonacci, Array Statistics and
Square Calculator. Each directory has a `spec.md` and exact `expected.txt`.

The ninth program prints primes from 2 through 30. A fresh agent wrote its
specification and 13 tests before its solution, using the frozen documentation
and compiler without language changes. See the [independent evaluation](docs/evaluation.md)
and [final technical report](docs/report.md). Verification passes 111 external
tests and 37 normal native tests, with zero unexpected failures. All nine
program outputs pass exact-byte comparisons in the pinned Nix shell.

## Coding agent usage

The coding agent ran for 25 minutes. Its reported token usage was:

| Measure | Tokens |
| --- | ---: |
| Input | 2,855,191 |
| Cached input (included in input) | 2,770,048 |
| Cache write input | 0 |
| Output | 47,239 |
| Reasoning output (included in output) | 8,254 |
| Total | 2,902,430 |

## Limitations and next experiment

Single source files; no imports, floats, structs, mutable/dynamic collections,
heap API or recoverable errors. Arrays cannot cross function boundaries. Host
stack or memory exhaustion is not reliably diagnosed. The C backend requires
GCC-compatible overflow builtins. There is no optimization effort, debugger
integration or formatter. These omissions keep the implementation bounded by
the current requirements.

Next, specify a small deterministic grid simulation before extending the
language. Let that program establish whether mutable collections, structured
values or recoverable input errors are actually needed. Measure correctness
and development friction before introducing performance work.

## License

FoxLang is licensed under the GNU General Public License, version 3 or
(at your option) any later version (`GPL-3.0-or-later`). See [LICENSE](LICENSE)
for the full license text.
