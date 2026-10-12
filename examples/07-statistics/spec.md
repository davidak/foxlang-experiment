# Array Statistics

## Purpose

Compute aggregates from a collection.

## Behavior

Store the eight integers 3,1,4,1,5,9,2,6 as a collection. Traverse it and calculate sum, minimum, maximum and integer arithmetic mean. Print in that order.

## Inputs and outputs

None.

Successful stdout must be exactly the bytes in `expected.txt` (UTF-8, LF endings). Successful runs have empty stderr and exit status 0. Each result occupies one line.

## Edge cases

Duplicate values count separately. Initialize extrema from an actual element. Empty input is not required; the fixed collection is nonempty.

## Acceptance criteria

Run the executable with the specified input; compare stdout byte for byte with `expected.txt`, require empty stderr and status 0. Verify applicable edge cases above independently, including the reusable routine contracts. No extra output is permitted.

## Required capabilities

Homogeneous collections; indexed access; collection length; iteration; aggregate state.
