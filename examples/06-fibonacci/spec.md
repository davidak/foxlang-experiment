# Fibonacci

## Purpose

Exercise recursive computation.

## Behavior

Use recursive computation with F(0)=0, F(1)=1 and F(n)=F(n-1)+F(n-2). Print F(0) through F(9) inclusive.

## Inputs and outputs

None; reusable computation accepts integers 0 through 9.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

Both base cases must terminate; behavior outside the reusable routine contract is not required.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Recursion; branching; function calls in arithmetic; iteration.
