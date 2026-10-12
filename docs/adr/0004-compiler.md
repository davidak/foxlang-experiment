# 0004: Python front end and C backend

Status: Accepted

## Context

Need a small general compiler and native executables.

## Decision

Handwritten lexer, recursive-descent/precedence parser, typed semantic analysis, C11 emitter, GCC-compatible cc backend. Materialize expressions in temporaries for ordered evaluation.

## Alternatives

Parser generators; LLVM; interpreter; textual substitution.

## Rationale

No Python dependencies; inspectable generated C; distinct passes and source spans.

## Consequences

More generated temporaries; GCC overflow builtins restrict backend portability.
