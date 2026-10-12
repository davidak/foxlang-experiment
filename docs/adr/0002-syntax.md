# 0002: Explicit delimiters and local declarations

Status: Accepted

## Context

Agents need predictable edits and readable diffs.

## Decision

Braces, semicolons, explicit parameter/result types, inferred local types, let/var distinction; conventional precedence.

## Alternatives

Significant indentation; implicit declarations; type inference across functions.

## Rationale

Local edits stay local and interfaces remain searchable.

## Consequences

Some punctuation and explicit types; one statement per line is a convention.
