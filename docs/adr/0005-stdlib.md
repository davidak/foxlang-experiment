# 0005: Narrow host boundary

Status: Accepted

## Context

I/O, conversion and test execution require host mechanisms.

## Decision

Builtins for print/read_int/len/assert/assert_eq/assert_ne; implement assert_true/assert_false/fail in FoxLang. Strict read-to-EOF conversion.

## Alternatives

General foreign function interface; line-oriented permissive conversion; entire framework in Python.

## Rationale

Small documented API; consistent checked errors; reusable logic remains in the language.

## Consequences

No recoverable input errors or broad standard library; interactive input requires EOF.
