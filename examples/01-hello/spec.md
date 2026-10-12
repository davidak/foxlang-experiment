# Hello World

## Purpose

Establish executable programs and text output.

## Behavior

Print the exact text `Hello, World!` followed by one LF newline.

## Inputs and outputs

None; standard input is not read.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

No leading/trailing spaces or extra blank lines.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

An executable entry point; constant text; output.
