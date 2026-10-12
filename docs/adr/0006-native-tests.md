# 0006: Tests as declarations with isolated assertion failures

Status: Accepted

## Context

Tests must be distinct from main and independently verifiable.

## Decision

Named test declarations; CLI test mode; sequential C runner using setjmp/longjmp to abort assertions and continue. Runtime faults remain fatal. Preserve call locations through standard wrappers.

## Alternatives

Ordinary main-based tests; subprocess per test; language exceptions.

## Rationale

Minimal runner with useful counts; no general exception feature introduced.

## Consequences

A runtime fault stops the suite; no cleanup/resource ownership exists in v0.1 so assertion unwinding has no resource protocol.
