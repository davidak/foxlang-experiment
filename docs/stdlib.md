# Standard library

Names are automatically available; no imports are needed. `T` below is a
signature notation for any one scalar type, not a language generic feature.

| Function | Result | Behavior |
| --- | --- | --- |
| `print(value: T)` | void | Decimal int, lowercase bool, or UTF-8 text; appends LF. I/O failure R005. |
| `read_int()` | int | Reads stdin through EOF; ASCII whitespace around one optional sign and decimal digits. Empty input, extra tokens, non-ASCII bytes, malformed or out-of-range integer: R004; read failure R005. |
| `len(values: integer array)` | int | Fixed array length; argument is evaluated. |
| `assert(value: bool, message: text)` | void | On false, abort current test with message; in normal execution exits 1. |
| `assert_eq(actual: T, expected: T)` | void | Require same scalar type and equality; show both values on failure. |
| `assert_ne(actual: T, expected: T)` | void | Require same scalar type and inequality; show both values on failure. |
| `assert_true(value: bool)` | void | Reusable FoxLang wrapper around assert. |
| `assert_false(value: bool)` | void | Reusable FoxLang wrapper around assert. |
| `fail(message: text)` | void | Reusable FoxLang wrapper that unconditionally fails. |

Only `assert_true`, `assert_false`, and `fail` are written in FoxLang, in
`stdlib/testing.fox`. The compiler/runtime implement host I/O, array length,
polymorphic comparisons, source locations and aborting a test. These require
facilities the small language cannot express. Failure paths are verified by
the external harness, which is independent of these assertions.
