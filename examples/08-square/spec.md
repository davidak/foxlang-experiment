# Square Calculator

## Purpose

Read, validate and safely process input.

## Behavior

Read all standard input to EOF. Accept exactly one optionally signed decimal integer, optionally surrounded by ASCII whitespace (space, tab, CR, LF, vertical tab, form feed). Print its square as decimal followed by LF. Input must fit signed 64-bit integers and the square must fit that range.

## Inputs and outputs

A byte stream. Example input: 12 followed by LF.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

Empty/whitespace-only input, malformed tokens, multiple tokens, non-ASCII bytes and integers outside [-9223372036854775808,9223372036854775807] fail. Inputs outside [-3037000499,3037000499] fail because the square overflows. Errors emit a meaningful diagnostic on stderr, no stdout, and nonzero status. Reading until EOF is intentional; an interactive user must send EOF.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Standard input; strict conversion; checked arithmetic; runtime diagnostics; failure exit status.
