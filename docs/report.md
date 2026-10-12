# Final technical report

FoxLang demonstrates the bounded experiment: a requirements-derived compiled
language can express the original eight programs and an additional program
written by a fresh coding-agent context using its documentation. It does not
establish production readiness or suitability for games yet.

## Implemented and verified

- **Language:** checked signed 64-bit integers, bool, immutable UTF-8 text,
  initialized let/var locals, lexical scope, conditional branches, while loops,
  scalar functions/results, forward calls and recursion, fixed immutable integer
  arrays with checked indexing, strict input and scalar output.
- **Compiler:** dependency-free Python lexer, recursive-descent parser, AST type
  and flow checker, C11 emitter and GCC-compatible native backend. Generated
  temporaries preserve left-to-right evaluation; logical operators short circuit.
  Diagnostics have stable identifiers, source paths, lines/columns and reliable
  hints where available. Runtime checks prevent integer and bounds errors.
- **Programs:** Hello World, Arithmetic, Classification, FizzBuzz, GCD, recursive
  Fibonacci, Array Statistics, Square and Primes all compile and match exact
  expected stdout, empty stderr and successful status. Invalid input and unsafe
  square values produce checked failures.
- **Verification:** 110 external Python tests pass, 0 fail. They include 40
  invalid-source fixtures, additional driver regressions, arithmetic comparisons
  against 250 seeded Python-oracle results, runtime/input boundaries, sequencing,
  standard API behavior, runner verification and frozen-implementation checks.
  The normal native suites have 37 passing tests and 0 failures. Ten deliberate
  assertion failures in the mixed runner fixture are expected and independently
  verified; these are not unresolved test failures.
- **Native testing:** named declarations, true/false/equality/inequality/custom
  assertions and explicit failure; call-site diagnostics, actual/expected values,
  per-test abort/continuation, counts, process status and a separate test mode.
  Reusable assertion wrappers are written in FoxLang. Empty suites and fatal
  runtime faults have documented behavior and external tests.
- **Environment:** pinned Nix release URL and unpacked hash supply Python, GCC
  and Git. The documented pure-shell suite and example commands ran successfully.
  Tests also run from a clean restored checkout. No global Python packages are
  required. Binary reproducibility is not claimed.

## Decisions and independent evaluation

Six ADRs explain the minimal requirements-driven scope, explicit syntax,
checked types/runtime semantics, Python-to-C pipeline, host/library boundary
and dedicated test runner. Every initial spec was committed separately before
syntax design; examples preceded compiler code; incremental compiler commits
verified previous examples at every milestone.

The fresh prime evaluator read public reference/API/testing documentation and
used compiler commands as a black box. It committed the specification and 13
native tests first, observed the expected E100 rejection, then implemented
reusable primality classification without changing the frozen language,
compiler, runtime, standard library or native framework. All 13 tests and the
26-byte output passed. Frozen SHA-256 checks corroborate the unchanged core.
The evaluator reported no blocking documentation problems. Its context was
fresh, but tools/files were shared; this is not an external audit. See
[evaluation.md](evaluation.md) for details and reproduction.

## Problems, limitations and next step

Review fixed inaccurate missing-main locations, a driver traceback on directory
outputs, acceptance of void calls as return values, and a clean-checkout setup
assumption in the external harness. Nix initially encountered sandbox store
restrictions; direct documented pure-shell invocations succeeded. The root
`.git` supplied by the environment remains read-only and empty. All development
commits are preserved in the delivered Git bundle, which restores a normal
checkout; that environment restriction was not silently ignored.

The implementation remains single-file, with no floats, structs, modules,
mutable/dynamic arrays, allocation API or recoverable errors. Host stack and
memory exhaustion are not reliably handled. The backend depends on GCC-compatible
builtins. There is no optimizer, debugger integration, fuzzing campaign or
performance evidence. Large prime inputs may take billions of divisions.

The recommended next experiment is a small deterministic grid simulation with
its specification written first. Use it to decide whether mutable collections
and structured values are justified, then benchmark only after correctness.
These are future investigations, not implemented capabilities.
