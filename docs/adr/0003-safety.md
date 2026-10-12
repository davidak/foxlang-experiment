# 0003: Checked scalar semantics and fixed arrays

Status: Accepted

## Context

C signed overflow and unchecked indexing would undermine reliability.

## Decision

Signed 64-bit checked arithmetic, strict bool conditions, no coercion, no shadowing; immutable fixed integer arrays.

## Alternatives

Wrapping integers; arbitrary precision; mutable dynamic arrays; exceptions.

## Rationale

Enough for current workloads with explicit failure and predictable cost.

## Consequences

Fatal runtime errors; host stack exhaustion remains unhandled. Arrays cannot cross function boundaries in v0.1.
