# FizzBuzz

## Purpose

Combine repetition and conditional logic.

## Behavior

Visit every integer from 1 through 30 inclusive. Print FizzBuzz for multiples of both 3 and 5, otherwise Fizz for multiples of 3, otherwise Buzz for multiples of 5, otherwise the decimal integer.

## Inputs and outputs

None.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

Both endpoints are included; the combined condition takes precedence.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Iteration; changing state; comparisons; divisibility; combined logical conditions.
