# Number Classification

## Purpose

Make decisions from integer values.

## Behavior

For each of -7, 0, 8, in order, print its sign classification, then its parity classification. Sign words are negative, zero, positive; parity words are even, odd.

## Inputs and outputs

None.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

Zero is even. Negative odd numbers remain odd. All words are lowercase.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Comparisons; conditional decisions; remainder; repeated classification logic.
