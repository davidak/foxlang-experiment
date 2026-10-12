# Independent prime-program evaluation

## Scope and independence

A fresh subagent evaluated the completed language by implementing a previously
unseen prime-number program. Its only language, API and compiler-command
learning resources were `docs/language.md`, `docs/stdlib.md` and
`docs/testing.md`. It invoked the compiler as a black box and did not read
compiler sources, runtime sources, standard-library implementation, existing
examples, the original prompt, architectural decisions or development history.
It did not inspect generated C.

This is a constrained independent exercise, not an external audit. The evaluator
had a fresh subagent context without the design conversation, but shared the
parent agent's tools and filesystem. The parent supplied the task, permitted
paths, environment command, and commit helper; the evaluator communicated
progress back to the parent. Shared access was not an enforced information
barrier. The same evaluator authored the new specification, tests and solution.

Compiler, runtime, standard library and testing framework were frozen. New or
changed files were restricted to `examples/09-primes`, this report, and
`build/independent`. No preexisting files were modified.

## Specification and tests before implementation

The language-independent contract is `examples/09-primes/spec.md`. It requires
exact prime output from 2 through 30 and a reusable signed-64-bit classification
operation. Thirteen native tests were written in
`examples/09-primes/primes.fox` before either application function existed.
They cover negative numbers including the integer minimum, zero, one, the
smallest primes, even and odd composites, square divisor boundaries, every
prime in the output interval, interval neighbors, larger primes and composites,
and both upper integer endpoints.

The initial command was:

```sh
nix-shell --pure --run 'python3 fox.py test examples/09-primes/primes.fox -o build/independent/primes-tests'
```

It returned status 1, with empty stdout and this stderr:

```text
examples/09-primes/primes.fox:2:18: error[E100]: unknown function is_prime
hint: Declare the function or check its spelling.
```

The rejection was expected and identified the unresolved function at the first
call. It establishes the initial compilation failure, not an executed failing
assertion. The specification and all thirteen tests were committed as `73a06c1`
before implementation. The tests remained unchanged during implementation.

## Implementation and results

The reusable `is_prime` function rejects inputs below 2 and tries divisors
beginning at 2. Its inclusive loop bound is `divisor <= n / divisor`, avoiding
overflow from squaring a divisor. Early returns reject composites. The positive
divisor cannot be zero, and its increment remains far below the signed integer
limit. `main` classifies integers 2 through 30 and prints the successful ones.
Only documented integer arithmetic, comparisons, functions, local bindings,
loops, conditionals and printing were needed. Native tests also use documented
immutable arrays and assertion functions.

Verification ran successfully in `nix-shell --pure`; the cached-GCC fallback
was not needed. The independent Python driver
`build/independent/verify.py` invoked the documented `python3 fox.py test` and
`python3 fox.py build` commands as subprocesses inside that pure environment.
It captured bytes, statuses and stderr, and imposed a 30-second timeout on
each subprocess. Reproduce with:

```sh
nix-shell --pure --run 'python3 build/independent/verify.py'
```

| Check | Result |
| --- | --- |
| Native tests | 13 passed; 0 failed; exit 0; empty stderr |
| Normal compilation | Exit 0; empty stderr |
| Program execution | Exit 0; empty stderr |
| Exact stdout comparison | Passed: 26 bytes, including the final LF |

The exact expected bytes were
`2\n3\n5\n7\n11\n13\n17\n19\n23\n29\n`.
The normal executable emitted no test-runner output. The native test run emitted
only its thirteen passing result lines and final summary, consistent with the
documented separation of `main` and tests. Raw verification output and command
statuses were saved under `build/independent`, including `results.json` and
`initial-rejection.txt`.

## Documentation findings and limitations

No blocking documentation omissions or contradictions were encountered. The
references supplied enough information to write the tests and complete the
program on the first implementation attempt. The documented lack of `break`
was handled with function returns. The single-source-file test model was
handled by appending implementation functions after the precommitted tests;
forward function declarations are explicitly supported. The expected E100
diagnostic and runner output matched the references.

The exercise does not prove correctness across every signed-64-bit input or
validate the whole language. Large prime inputs can require billions of trial
divisions; no performance guarantee was tested or claimed. Integer endpoints
were exercised with quickly classified negative or composite values, and the
largest tested prime was 2147483647. This task did not exercise input handling,
recursion, text manipulation, imports or I/O failure behavior. The regression
suite and compiler implementation were not independently inspected or rerun.

No compiler, runtime, library, framework or reference-document changes were
needed. The only delivered source changes are the new prime example and this
evaluation report; verification artifacts are confined to `build/independent`.
