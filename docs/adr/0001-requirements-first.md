# 0001: Small requirements-driven core

Status: Accepted

## Context

Eight concrete programs need a deliberately bounded foundation.

## Decision

Implement scalar values, local state, functions, recursion, decisions, loops, immutable integer arrays, I/O and tests.

## Alternatives

A broad systems language; eight special-purpose translators.

## Rationale

Each feature maps to an executable requirement; ordinary functions compose.

## Consequences

No modules, heap API, floats, structs or performance claims.
