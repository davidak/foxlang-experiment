# Working on FoxLang

## Purpose and sources of truth

FoxLang is an experimental compiled programming language developed through
progressively more demanding programs. Discover the language through working
programs, document the decisions, and verify the implementation.

This guidance distills [initial-prompt.md](initial-prompt.md) for ongoing work.
The original eight examples and independent prime-program evaluation are
complete; their development phases are historical context, not a checklist to
restart. Games, simulations, and interactive applications are long-term goals.

Before changing behavior, read the relevant specifications and documentation:

- [README.md](README.md): project overview, environment, commands, and limits.
- [docs/language.md](docs/language.md): implemented syntax, grammar, and semantics.
- [docs/stdlib.md](docs/stdlib.md): standard API and error behavior.
- [docs/testing.md](docs/testing.md): native tests and external verification.
- [docs/adr/](docs/adr/): architectural decisions and their rationale.
- Each example's `spec.md`: language-independent acceptance requirements.

Keep the implementation and reference documentation consistent. Document only
implemented capabilities as available; distinguish plans and known limitations.
When the user gives a durable preference or workflow instruction for future
FoxLang work, update this file to record it.

## Development principles

- Follow KISS, YAGNI, and separation of concerns. Prefer a few consistent,
  composable concepts and reusable library functions over special syntax.
- Add features only when a concrete program requires them. Avoid speculative
  abstractions, copying another language's feature set, and premature optimization.
- Implement general language rules. Never recognize or special-case an example
  program to make its tests pass.
- Prioritize correctness, safety, and maintainability. Preserve static checking,
  predictable runtime behavior, and explicit diagnostics for invalid operations.
- Keep syntax and formatting predictable for humans and unfamiliar coding agents.
  Use readable names, small diffs, and searchable documentation. FoxLang source
  uses four-space indentation and one statement per line.
- Make and document reasonable routine engineering decisions autonomously.
  Report unresolved limitations and their causes; never weaken acceptance
  criteria merely to report success.

## Requirements-driven workflow

For a new example or language capability:

1. Write a language-independent specification covering purpose, exact behavior,
   inputs, outputs, edge cases, acceptance criteria, and required capabilities.
2. Determine the smallest coherent language or library change needed. Update the
   reference and record significant decisions before compiler implementation.
3. Write the FoxLang program against that specification before extending the
   compiler. For evaluation tasks, write native tests before the solution.
4. Implement incrementally. Compile and run the affected programs, compare their
   output with the specification, and run regression tests after meaningful steps.
5. Update documentation and report what was implemented, verified, and left open.

Add ADRs for significant syntax, semantics, safety, compiler, library, or testing
decisions. Include status, context, decision, alternatives, rationale, and
consequences. Supersede earlier ADRs to preserve history; avoid ADRs for trivial
implementation details.

## Repository and implementation

- `fox.py`: CLI, file handling, compiler invocation, and test execution.
- `compiler/frontend.py`: lexer, parser, and source diagnostics.
- `compiler/semantics.py`: semantic and type checking.
- `compiler/backend.py` and `compiler/runtime.c`: C generation and runtime.
- `stdlib/testing.fox`: reusable native assertion wrappers.
- `examples/`: separate directories with specifications, FoxLang sources, and
  expected output/input fixtures.
- `tests/test_*.py`: independent Python verification; `tests/invalid/` contains
  rejected programs and expected diagnostics, `tests/native/` native coverage,
  and `tests/framework/` intentionally failing or empty runner fixtures.
- `docs/`: reference material, ADRs, development history, and evaluation reports.
- `build/`: generated C, binaries, and temporary verification artifacts.

The compiler uses Python's standard library and a GCC-compatible C11 backend.
Keep parsing, semantic analysis, code generation, and runtime responsibilities
separate. Add dependencies only when justified and declare them in the Nix
environment. Performance work should follow measured application requirements.

Diagnostics must have stable identifiers, accurate source locations, and clear
explanations. Offer correction hints only when reliable. Preserve deterministic
diagnostics, documented exit statuses, and rejection of invalid programs without
leaving a stale executable that appears to be a successful build.

## Environment and verification

Run commands from the repository root inside the pinned development shell:

```sh
nix-shell --pure
```

Build and execute an example:

```sh
python3 fox.py build examples/01-hello/main.fox -o build/hello
./build/hello
```

Run the initial example acceptance checks and full independent suite:

```sh
python3 tests/examples.py
python3 -m unittest discover -s tests -v
```

Run native language, library, and prime-program tests:

```sh
python3 fox.py test tests/native/language.fox
python3 fox.py test tests/native/stdlib.fox
python3 fox.py test examples/09-primes/primes.fox
```

Use relevant targeted checks during development and the full independent suite
for compiler, runtime, library, or testing-framework changes. Test documented
commands before delivering new or changed instructions. A working Nix shell
does not establish bit-for-bit reproducible builds; document actual guarantees.

Verify stdout, stderr, exit status, and exact output bytes where specified.
Cover boundaries and combinations of features beyond the original examples.
Invalid-program checks must verify rejection, diagnostic category and location,
and absence of a successful executable.

Keep the external harness independent of native assertions. Test the native
runner externally using deliberate failures, mixed results, empty suites,
counts, locations, and exit statuses. Expected failures in fixtures are part of
successful verification. Test supported language features and library functions
natively where possible; use external checks for invalid source and fatal errors.

Native tests are dedicated declarations, separate from normal execution. Test
discovery is confined to the supplied source file. Keep reusable assertion
functionality in FoxLang where practical, with compiler/runtime support only
where necessary. Avoid speculative framework features.

## Independent evaluations

For a new independent evaluation, use a fresh agent context when available and
provide only the task specification, language/API documentation, and documented
commands. Freeze the compiler, runtime, library, and testing framework during
that exercise. Record an unsupported requirement instead of extending the
language to pass it. Disclose when a fresh context is unavailable.

The existing evaluation is documented in `docs/evaluation.md`.
`tests/test_evaluation.py` checks hashes in `docs/evaluation-freeze.json`, so
changes to frozen implementation or reference files affect that check. Preserve
the historical evidence and explicitly document any transition to a new
baseline; do not silently refresh hashes to hide a failed check.

## Git and delivery

Use small, focused commits with descriptive messages at completed development
milestones. Run relevant checks before committing functionality. When Codex
creates a commit, set its author to `Codex <noreply@openai.com>` for that
commit only, for example with `git -c user.name=Codex
-c user.email=noreply@openai.com commit`. Do not change the user's Git
configuration; commits the user creates manually should continue to use their
own identity. Do not add a separate `Assisted-by` trailer unless requested.

Keep generated C, executables, caches, and temporary artifacts under `build/`
and out of version control. Preserve unrelated user changes. Keep the README,
language/API/testing references, and significant decision records synchronized
with changes. Report verification results and limitations accurately, separating
implemented behavior from verified behavior and future plans.
