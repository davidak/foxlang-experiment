# Testing FoxLang

Use `python3 -m unittest discover -s tests -v` for the full independent suite.
It requires Python and GCC, available through `nix-shell --pure`. Tests write
only under build. They compare stdout/stderr/status and diagnostic locations.
The Linux I/O failure tests use `/dev/full` and directory file descriptors.
Each subprocess has a timeout for compiler/example execution where applicable.

## Native tests

Write `test "unique descriptive name" { ... }` at file scope. Execute with
`python3 fox.py test FILE`. Functions may follow or precede tests. Tests run in
source order with fresh local variables, and can call application functions.
There is no cross-file discovery, fixture system or parallel execution.

| Assertion | Success condition |
| --- | --- |
| `assert_true(condition)` | condition is true |
| `assert_false(condition)` | condition is false |
| `assert_eq(actual, expected)` | same-typed scalar values are equal |
| `assert_ne(actual, expected)` | same-typed scalar values differ |
| `assert(condition, message)` | condition is true |
| `fail(message)` | never; explicitly abort the current test |

Failure aborts the current test and resumes with the next one. Messages identify
the test and source call location, with both values for comparison failures.
The three FoxLang library wrappers preserve their caller's location. User
helpers report their internal assertion location. Main is never run in test
mode; tests are never run in normal mode. All bodies are statically checked in
both modes. A test-only file can have no main.

Expected output consists of `PASS name` or `FAIL name` followed by
`N passed; M failed`. Application output such as print calls can occur between
result lines. Assertion details use stderr. Exit 0 means no failures, including
zero discovered tests; exit 1 means assertions failed (or compilation failed,
which is distinguished by an error identifier). Fatal runtime errors exit 2
without a summary. CLI usage errors also exit 2.

`tests/native/language.fox` has 16 feature tests; `stdlib.fox` has four API tests
and consumes `-12` from stdin. `smoke.fox` tests the assertion API minimally.
GCD and Fibonacci carry their own contract tests. Negative library/runtime
behavior is covered externally because a fatal error cannot be caught in
FoxLang. The mixed framework fixture has two passing and ten failing tests;
the external harness verifies every expected failure location and final count.

## Coverage boundaries

The suite covers lexing, syntax, scope, types, function calls/results, recursion,
control flow, every operator, integer endpoints, short circuit, evaluation
order, immutable arrays, I/O, assertions and runner behavior. A seeded Python
oracle compares 250 arithmetic computations. Invalid fixtures specify exact
source positions and codes in JSON. Square tests cover malformed/empty input,
ASCII whitespace, non-ASCII/NUL bytes, conversion limits and square overflow.

This is regression and acceptance coverage, not a proof of correctness or an
exhaustive test of every possible source. Resource exhaustion, platform-specific
compiler failures and operating-system faults remain limitations. No fuzzing
coverage percentage or performance guarantee is claimed.
