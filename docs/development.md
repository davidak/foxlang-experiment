# Development record

## Phase 1 review

All eight language-independent specifications and exact output fixtures were
written and individually committed before syntax design. Reviewed sign/parity,
FizzBuzz precedence, GCD zero cases, recursive Fibonacci base cases, duplicate
array values and strict square input/range failures. Successful output is LF
terminated and stderr-free. Square consumes stdin through EOF.

## Phase 2 review

Coverage: text output (1), checked integer locals/operators (2), bool/if (3),
while and mutation (4), parameters/returns (5), recursion (6), fixed arrays,
indexing and len (7), strict read_int and overflow failure (8). Dedicated test
declarations and a minimal assertion API cover the testing requirement.
No extra application features are needed. Reference and six ADRs precede the
compiler. Arrays are deliberately local and immutable, sufficient for the
collection requirement; all reusable application computations use scalars.

## Environment constraints

The supplied `.git` directory is empty and read-only. Development commits use
separate Git metadata at `/tmp/foxlang-git-history`; a final portable Git bundle
will preserve the full history. Standard Git commands in this workspace cannot
work until writable metadata is available. Nix initially cannot access its
daemon socket in the sandbox. Cached store tools are being investigated.

## Phase 3 review

All eight implementations were written before compiler development and checked
against the reference: locals initialize before use; parameters stay immutable;
result functions return on all paths; conditions are bool; collection elements
are int; square delegates strict parsing and arithmetic safety to the runtime.
No language additions were needed. Examples are committed as executable
requirements, with no compiler yet present.

## Compiler milestones 1–6

The front end was built as independent lexical, parsing and semantic passes;
C emission was enabled incrementally. Verified and committed: Hello World;
checked arithmetic; sign/parity decisions and void function calls; mutation,
while and short circuit; result-bearing functions and GCD. Each milestone
reran every preceding example with byte-for-byte output comparison.
Recursive Fibonacci then passed without compiler changes: function prototypes
and general call emission already support recursion. All six examples pass.
Native builds use cached Nix GCC 15.2.0; no ad-hoc compiler installation.
