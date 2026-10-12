# Greatest Common Divisor

## Purpose

Provide reusable parameterized computation.

## Behavior

Use the Euclidean remainder algorithm to compute gcd for (48,18), (54,24), (17,13), printing the three results. Reusable logic accepts nonnegative signed 64-bit integers and returns their greatest common divisor; define gcd(0,0)=0.

## Inputs and outputs

None for the executable; reusable logic receives two nonnegative integers.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

gcd(a,0)=a; gcd(0,b)=b; equal positive inputs return that value. Negative inputs are outside the reusable routine contract.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Functions with parameters and return values; local state; loops; remainder.
