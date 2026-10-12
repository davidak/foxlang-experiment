# FoxLang: Evolutionary Programming Language Experiment

## 1. Project Overview

Develop a new compiled programming language, provisionally named **FoxLang**, through an evolutionary, requirements-driven development process.

The long-term goal is a simple, reliable, efficient programming language suitable for games, simulations, and interactive applications, with particular attention to development by AI coding agents.

Rather than designing the entire language in advance, derive its features from a collection of progressively more demanding programs.

The central experiment is to determine whether an AI coding agent can:

1. Specify a collection of small programs independently of any programming language.
2. Design a coherent programming language capable of expressing those programs.
3. Implement the programs in that language before a compiler exists.
4. Develop a working compiler based on the language specification.
5. Develop a native unit-testing framework using the new language.
6. Verify the compiler, language features, standard library, and testing framework.
7. Implement an additional, previously unseen program using only the completed language and its documentation.

The objective is a **small, functional, documented, and thoroughly tested programming language**, not an ambitious or prematurely optimized implementation.

Work autonomously. Make and document reasonable engineering decisions instead of requesting approval for routine implementation details.

## 2. General Design Principles

### Simplicity

Follow KISS, YAGNI, and separation of concerns.

Prefer a small number of consistent, composable concepts over numerous specialized features.

Avoid premature abstraction, speculative generalization, and unnecessary complexity.

Introduce language features only when they are justified by concrete requirements.

Prefer reusable library functionality over additional language constructs when appropriate.

### Agent-Friendly Development

Design the language to be understandable and usable by AI coding agents that have never encountered it during training.

Prioritize:

- Consistent and predictable syntax.
- Clearly defined semantics.
- Minimal ambiguity.
- Helpful and actionable compiler diagnostics.
- Comprehensive, searchable documentation.
- Readable source code.
- Deterministic formatting conventions.
- Small, meaningful Git diffs.
- Straightforward compilation, testing, and debugging workflows.

Consider how syntax and formatting decisions affect automated source-code editing.

For example, avoid designs that unnecessarily encourage multiple unrelated statements on the same line or cause large formatting changes after small edits.

Do not assume that shorter source code necessarily means simpler programming.

### Safety and Reliability

Prefer language designs that prevent common programming errors.

Consider static type checking, predictable runtime behavior, and explicit handling of invalid operations.

Determine the specific mechanisms from the requirements and document the reasoning behind them.

Avoid undefined or surprising behavior wherever practical.

### Performance

FoxLang should eventually be suitable for performance-sensitive applications.

For the initial implementation, use an existing C compiler as the native-code backend.

Do not attempt to outperform mature compilers or optimize specifically for the example programs.

Prioritize correctness, simplicity, and maintainability.

Performance optimization should be driven by evidence from future applications and benchmarks.

### Evolutionary Design

Treat the initial language as an experimental foundation rather than a finished design.

Future programs should reveal missing capabilities and motivate language improvements.

Record significant design decisions and their rationale.

Do not introduce features merely because they are common in other programming languages.

## 3. Repository Organization

Organize the repository so that the language specification, compiler implementation, standard library, example programs, automated tests, architectural decisions, and development documentation are clearly separated.

Each example program should have its own directory containing:

- A language-independent specification.
- Its FoxLang source code.
- Any necessary test inputs or expected outputs.

Choose clear, consistent directory and file names.

Store generated C code, executables, and other build artifacts in a separate build directory. Keep these artifacts out of version control.

Maintain a central language reference describing the complete implemented language.

Maintain Architecture Decision Records (ADRs) in a dedicated documentation directory.

Provide a root README explaining the project, its structure, and how to build, run, and test it.

Use Git throughout development.

## 4. Phase 1: Specify the Example Programs

Before designing any FoxLang syntax, write precise, language-independent specifications for the following eight programs.

The programs are arranged to introduce progressively more demanding programming concepts.

Each specification must define:

- The purpose of the program.
- Its exact behavior.
- Inputs and outputs.
- Relevant edge cases.
- Acceptance criteria.
- The programming capabilities implied by its requirements.

Do not prescribe how these capabilities must be expressed in FoxLang.

### Program 1: Hello World

Write a program that prints the exact text:

**Hello, World!**

The output must end with a newline.

This establishes the simplest possible executable program and text output.

### Program 2: Basic Arithmetic

Write a program that initializes two integer values, 17 and 5, and calculates:

- Their sum.
- Their difference.
- Their product.
- Their integer quotient.
- Their remainder.

Print the five results in that order, one per line.

Expected values: 22, 12, 85, 3, and 2.

This introduces storing values and evaluating arithmetic expressions.

### Program 3: Number Classification

Write a program that classifies each of the integers -7, 0, and 8.

For each integer, determine:

- Whether it is negative, zero, or positive.
- Whether it is even or odd.

Print the two classifications for each integer on separate lines.

Use lowercase English words.

This introduces decisions based on values and logical conditions.

### Program 4: FizzBuzz

Implement the classic FizzBuzz exercise for the integers 1 through 30, inclusive.

For each number:

- Print "FizzBuzz" if divisible by both 3 and 5.
- Otherwise print "Fizz" if divisible by 3.
- Otherwise print "Buzz" if divisible by 5.
- Otherwise print the number itself.

Print one result per line.

This introduces repetition and the combination of iteration with conditional logic.

### Program 5: Greatest Common Divisor

Implement the Euclidean algorithm as reusable program logic.

Calculate the greatest common divisor for these pairs:

- 48 and 18.
- 54 and 24.
- 17 and 13.

Print the results in that order, one per line.

Expected values: 6, 6, and 1.

This introduces reusable computations with inputs and results.

### Program 6: Fibonacci

Implement the Fibonacci sequence using recursion.

Use the conventional definition in which the sequence begins with 0 and 1, and each subsequent value is the sum of the preceding two.

Print the first ten values, one per line.

Expected values: 0, 1, 1, 2, 3, 5, 8, 13, 21, and 34.

This introduces recursive computations.

### Program 7: Array Statistics

Process the integer collection:

3, 1, 4, 1, 5, 9, 2, 6.

Calculate:

- Sum.
- Minimum.
- Maximum.
- Arithmetic mean using integer division.

Print the results in that order, one per line.

Expected values: 31, 1, 9, and 3.

This introduces working with collections of values.

### Program 8: Square Calculator

Read one integer from standard input.

Calculate its square and print the result followed by a newline.

For an input of 12, the output must be 144.

Define appropriate behavior for invalid input, end-of-file, and values that cannot be represented or processed safely.

Errors must produce a meaningful diagnostic and a nonzero process exit status.

This introduces interactive input, conversion, and error handling.

### Phase Completion

Write and review all eight specifications before proceeding.

Keep the specifications independent of FoxLang syntax.

Commit each completed specifications separately to Git.

## 5. Phase 2: Design the Programming Language

Design FoxLang based on the requirements identified in Phase 1.

Your task is to determine which language features, syntax, semantics, and standard library capabilities are necessary to express all eight programs cleanly and consistently.

Do not begin by copying the feature set of an established language.

Evaluate alternative designs where appropriate.

Aim for the smallest coherent language that satisfies the requirements while remaining extensible.

### Language Specification

Create a comprehensive language reference.

It must be sufficiently precise and complete for:

1. A human programmer unfamiliar with FoxLang to write correct programs.
2. An AI coding agent with no prior knowledge of FoxLang to implement new programs.
3. A compiler developer to implement the documented language.
4. A developer to understand why a program is valid or invalid.

Document the syntax and semantics of every supported language feature.

Include a formal or otherwise unambiguous grammar.

Explain the standard library API and the behavior of supported operations.

Document edge cases, error behavior, and implementation limitations.

The documentation must describe the actual language, not aspirational future features.

### Native Testing Capability

The language must support a dedicated syntax for declaring and executing unit tests.

Tests must support assertions that can:

- Verify that a condition is true.
- Verify that a condition is false.
- Compare values for equality.
- Compare values for inequality.
- Explicitly report a failure with a message.

Design the syntax yourself.

Do not treat test declarations merely as ordinary application entry points.

The language must distinguish normal program execution from test execution.

Keep the testing mechanism simple and consistent with the rest of the language.

Determine which functionality belongs in the language, which belongs in the standard library, and which belongs in the test runner.

### Architecture Decision Records

Create ADRs for significant language and compiler design decisions.

Each ADR must document:

- Context and problem.
- Decision.
- Alternatives considered.
- Rationale.
- Consequences and tradeoffs.
- Current status.

Record decisions concerning the overall language philosophy, major syntax conventions, type and runtime semantics, compiler strategy, standard library boundaries, and native testing design.

Create additional ADRs whenever important architectural decisions arise.

Do not create unnecessary ADRs for trivial implementation details.

Preserve the history of decisions. Supersede previous ADRs rather than silently rewriting historical reasoning.

### Phase Completion

Review the language design against all eight program specifications.

Resolve contradictions and missing capabilities.

Commit the language reference and ADRs before implementing the compiler.

## 6. Phase 3: Write the Example Programs

Implement all eight programs in FoxLang according to their specifications.

The compiler does not exist yet.

Use the language reference as the authoritative definition of valid FoxLang code.

Keep implementations simple and idiomatic.

Do not introduce program-specific language shortcuts.

Review all eight implementations for consistency and clarity.

If writing the programs reveals a genuine deficiency in the language design, revise the language specification and record the decision before compiler development begins.

Once the programs and language specification are consistent, commit the source code.

These programs will serve as the initial executable requirements for the compiler.

## 7. Phase 4: Implement the Compiler

Implement a compiler that translates FoxLang into C and uses an existing C compiler to produce native executables.

Use Python for the initial compiler implementation.

Choose an appropriate internal architecture based on the language grammar, semantics, and requirements.

Do not implement a collection of special cases that recognizes the eight example programs.

The compiler must implement general language rules that also work for other programs.

### Compiler Requirements

The compiler must:

- Accept FoxLang source files.
- Validate syntax and semantics.
- Reject invalid programs.
- Generate correct C code for valid programs.
- Invoke a C compiler to create native executables.
- Report compilation failures clearly.
- Return appropriate process exit codes.
- Provide a straightforward command-line interface.

The generated executable must implement the specified FoxLang behavior.

### Compiler Diagnostics

Design diagnostics specifically to help humans and AI coding agents identify and correct errors.

A useful diagnostic should identify:

- What went wrong.
- Where the error occurred.
- Why the program is invalid.
- What the programmer can do to correct it, when a reliable suggestion is possible.

Provide stable diagnostic identifiers and accurate source locations.

Avoid misleading suggestions.

Diagnostics should be consistent and deterministic.

### Incremental Implementation

Implement compiler capabilities in the order required by the eight programs.

After each meaningful implementation step:

1. Compile the relevant example program.
2. Execute the generated binary.
3. Verify its output.
4. Run all previously passing tests.
5. Fix regressions.
6. Commit the completed work.

Do not postpone integration testing until the entire compiler is implemented.

## 8. Phase 5: External Compiler Verification

Develop an automated test harness using Python or another suitable tool available in the development environment.

This harness must independently verify the behavior of the FoxLang compiler.

### Valid Programs

For each of the eight examples:

- Compile the program.
- Verify successful compilation.
- Verify that the executable exists.
- Run the executable.
- Supply predefined input where necessary.
- Capture stdout, stderr, and exit status.
- Compare the results with the specification.

Verify exact output, including line endings where appropriate.

Add tests for important edge cases.

### Invalid Programs

Create intentionally invalid FoxLang programs that exercise different categories of compiler errors.

Include at least:

- Malformed syntax.
- Unknown identifiers.
- Invalid operations.
- Incorrect use of functions.
- Type inconsistencies.
- Invalid control flow.
- Incorrect use of collections.
- Duplicate declarations where prohibited.

Adapt the precise test cases to the actual language design.

For each invalid program, define the expected error category and relevant source location.

Verify automatically that:

1. The compiler rejects the program.
2. The compiler returns a nonzero exit status.
3. No successful executable is produced.
4. The diagnostic identifies the correct error category.
5. The reported source location is accurate.
6. The explanation is meaningful.
7. A correction hint is provided when appropriate.

Do not require a correction hint for errors where no reliable correction can be inferred.

### Generality

Add small additional compiler tests that combine supported language features in ways not present in the original examples.

This helps detect implementations that accidentally depend on specific example structures.

Keep the external compiler test harness independent of FoxLang's native testing framework.

Commit the tests and their fixtures.

## 9. Phase 6: Native Unit-Testing Framework

Implement the native testing capability specified in Phase 2.

The goal is to make FoxLang suitable for test-driven development without relying exclusively on external testing tools.

### Requirements

Provide a dedicated test declaration syntax and an associated test runner.

The framework must support:

- Multiple named tests.
- Boolean assertions.
- Equality and inequality assertions.
- Explicit failures with messages.
- Clear identification of failing tests.
- Useful assertion diagnostics.
- Accurate pass/fail counts.
- Correct process exit status.
- Separation of test execution from normal program execution.

Failed assertions must identify the relevant source location.

Where practical, equality failures should report the actual and expected values.

Keep the implementation minimal.

Implement reusable testing functionality in FoxLang itself wherever possible.

Only introduce compiler-specific or runtime-specific mechanisms where justified by the language design.

Avoid unnecessary test framework features such as mocking, fixtures, plugins, or parallel execution.

### Language Feature Tests

Write native FoxLang unit tests covering all implemented language features.

Test normal behavior, boundary conditions, and meaningful interactions between features.

Where behavior cannot be tested through native assertions, use the external harness.

In particular, invalid source programs must continue to be tested externally.

### Standard Library Tests

Write native tests for every implemented standard library function.

Include representative inputs, edge cases, and error behavior where applicable.

### Testing the Testing Framework

Develop a dedicated test suite for the native testing framework itself.

Verify:

- Successful assertions.
- Failed assertions.
- Different assertion categories.
- Explicit failures.
- Multiple tests in one run.
- Mixtures of passing and failing tests.
- Accurate result counts.
- Correct process exit status.
- Useful diagnostic messages.
- Correct behavior when no tests are found.

Use intentionally failing fixtures.

Verify the testing framework's behavior using the external test harness.

Do not rely solely on the framework's own assertions to establish that it works.

### Documentation

Document the testing syntax, available assertions, test discovery rules, execution commands, and interpretation of results.

Provide enough documentation for an unfamiliar AI coding agent to write and execute FoxLang unit tests independently.

Commit the framework and its tests in logical development steps.

## 10. Phase 7: Independent Program Evaluation

After the compiler, language documentation, standard library, and native testing framework are complete, evaluate whether FoxLang can be used for a new programming task.

This phase is intended to test the language's generality and the quality of its documentation.

### Independence Requirements

Use a fresh coding-agent session if the environment supports it.

The agent should receive:

- The new program specification.
- The FoxLang language documentation.
- The standard library documentation.
- The documented compiler and testing commands.

The agent should not need access to the original language-design discussions.

During this phase:

- Do not modify the compiler.
- Do not extend the language.
- Do not modify the standard library.
- Do not change the testing framework.

The program must use only previously implemented and documented capabilities.

If the task cannot be completed, document the reason instead of modifying the language to make it pass.

### Primary Task: Prime Numbers

Implement a program that prints all prime numbers from 2 through 30, inclusive.

A prime number is an integer greater than 1 with no positive divisors other than 1 and itself.

The program must implement reusable prime-number classification logic.

Expected output, one number per line:

2, 3, 5, 7, 11, 13, 17, 19, 23, 29.

Write a program specification and native unit tests before implementing the solution.

The tests must cover prime numbers, composite numbers, zero, one, and representative boundary cases.

### Alternative Task A: Factorial

If the primary task is unsuitable for a substantive, documented reason, implement a program that calculates factorials for the integers 0 through 10.

Print one result per line.

Expected values:

1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800.

Include native unit tests.

### Alternative Task B: Collatz Sequence

If neither previous task is suitable for a substantive, documented reason, implement the Collatz sequence starting at 6.

For each positive integer:

- If even, divide by 2.
- If odd, multiply by 3 and add 1.

Continue until reaching 1.

Expected sequence:

6, 3, 10, 5, 16, 8, 4, 2, 1.

Print one value per line.

Include native unit tests.

### Evaluation

Record:

- Whether the program compiled successfully.
- Whether all acceptance tests passed.
- Whether the native unit tests passed.
- Any compiler diagnostics encountered.
- Any language or documentation problems discovered.
- Whether the program could be implemented without language changes.

If a fresh agent session is unavailable, document that limitation.

Do not claim independent evaluation when the same uninterrupted agent context was used.

Commit the new program, specification, and tests.

## 11. Development Environment

Use Nix to manage development dependencies.

Create a `shell.nix` file that provides the necessary tools, including Python and a C compiler.

Additional dependencies may be introduced when justified.

The project should be usable from a Nix development shell without requiring undocumented global dependencies.

Aim for reproducible builds.

Pin dependencies where practical and document any remaining sources of nondeterminism.

Verify that the compiler and test suite can be run using the documented Nix environment.

Do not confuse a working development shell with a fully reproducible build; document the actual reproducibility guarantees.

## 12. Git Workflow

Use Git throughout the project.

Make meaningful commits after completed development steps.

In particular, commit:

- Program specifications.
- Language design and ADRs.
- Initial FoxLang programs.
- Compiler milestones.
- External compiler tests.
- Native testing framework.
- Native language and standard library tests.
- Independent program.
- Final documentation.

Prefer small, focused commits with descriptive messages.

Document the used LLM with: `Assisted-by: Codex (GPT-6 Astra High) <noreply@openai.com>`.

Run relevant tests before committing completed functionality.

Do not commit generated binaries, generated C files, caches, or temporary build artifacts.

Configure `.gitignore` accordingly.

Preserve a clear history showing how the language and compiler developed from the original requirements.

## 13. README and Documentation

Create a comprehensive but concise root README.

It must explain:

- The purpose of FoxLang.
- The evolutionary development approach.
- The current language capabilities.
- The repository organization.
- Development dependencies.
- How to enter the Nix development environment.
- How to build or invoke the compiler.
- How to compile FoxLang programs.
- How to execute compiled programs.
- How to run external compiler tests.
- How to write and run native FoxLang unit tests.
- Which example programs are included.
- Where to find individual program specifications.
- Where to find the language reference and ADRs.
- Known limitations.
- Recommended next development steps.

All documented commands must be tested before completion.

The language reference must be detailed enough to serve as the primary learning resource for a programmer or AI coding agent unfamiliar with FoxLang.

Keep the documentation synchronized with the actual implementation.

## 14. Completion Criteria

The experiment is complete when:

- All eight initial programs have precise specifications.
- FoxLang has a coherent and documented design.
- Significant architectural decisions are recorded in ADRs.
- All eight programs are implemented in FoxLang.
- A general-purpose compiler translates the supported language into C.
- All eight programs compile into native executables.
- Their behavior matches their specifications.
- Invalid programs are rejected with accurate, useful diagnostics.
- External compiler tests pass.
- Native test declarations and assertions work.
- Native tests cover all implemented language features.
- Native tests cover all implemented standard library functions.
- The testing framework's behavior is independently verified.
- The ninth program is implemented and tested without extending the language or compiler.
- The project can be built and tested using the documented Nix environment.
- The README and language documentation are complete and accurate.
- Completed work is committed to Git.
- Generated binaries and C files are excluded from version control.

Do not weaken acceptance criteria merely to report success.

If any requirement cannot be completed, report the limitation and its cause.

## 15. Final Report

At the end, provide a concise technical report covering:

1. Implemented language capabilities.
2. Compiler implementation approach.
3. Status of all example programs.
4. Number of passing and failing tests.
5. Native testing framework capabilities.
6. Important architectural decisions.
7. Results of the independent ninth program.
8. Problems encountered and unresolved limitations.
9. Recommended next experiment.

Distinguish clearly between:

- Implemented functionality.
- Verified functionality.
- Known limitations.
- Planned future improvements.

Evaluate whether the experiment demonstrates that an AI coding agent can develop a small, coherent, reusable compiled programming language from progressively more demanding programming requirements.

**The guiding principle is to discover the language through working programs, document the decisions, and verify the implementation—not to design an unnecessarily complex language in advance.**
