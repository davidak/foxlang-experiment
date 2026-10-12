# Basic Arithmetic

## Purpose

Evaluate integer arithmetic on stored values.

## Behavior

Initialize values 17 and 5. Compute sum, difference (first minus second), product, integer quotient (first divided by second), and remainder. Print in that order.

## Inputs and outputs

None.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

The quotient is integral; all inputs and results fit signed 64-bit integers.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Named stored integer values; five arithmetic operations; numeric output.
