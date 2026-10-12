# Prime numbers from 2 through 30

The program shall run without input and classify every integer from 2 through
30 inclusive. It shall print each prime in increasing order, exactly once.
Each number shall use decimal digits followed by one LF byte. There shall be
no spaces, headings, blank lines or other output. Successful execution shall
exit with status 0 and leave standard error empty.

The exact standard output shall be:

```text
2
3
5
7
11
13
17
19
23
29
```

The final `29` shall also be followed by LF; the complete output is 26 bytes.

## Reusable classification contract

A reusable classification operation shall accept a signed 64-bit integer and
return a Boolean. It shall return true precisely when the input is at least 2
and has no positive divisors other than 1 and itself. All negative integers,
zero and one shall return false. Classification shall produce no output.
Arithmetic used in classification shall not overflow for any accepted input.
There is no performance guarantee for very large primes.

The command-line program shall use this operation to select its output.

## Native acceptance cases

Tests shall exercise the reusable operation directly, independently of program
output, and cover:

- Negative values: the signed 64-bit minimum, -30, -3, -2 and -1.
- Zero and one, each explicitly classified as nonprime.
- The smallest prime, 2, and the smallest odd prime, 3.
- Every even composite from 4 through 30.
- Odd nonsquare composites 15, 21 and 27.
- Prime squares 4, 9, 25, 49 and 121, checking inclusive divisor boundaries.
- Every prime in the requested output interval.
- Interval boundaries and their neighbors: 28, 29, 30, 31 and 32.
- Larger known primes 97, 997 and 2147483647.
- Larger composites 99, 1001 and 2147483646.
- Signed 64-bit upper endpoints 9223372036854775806 and
  9223372036854775807, both composite.

The specification and native tests shall be committed before implementation.
Before the classification operation exists, the native tests are expected to
be rejected at compilation for their unresolved operation reference. Following
implementation, all native tests and a separate exact-byte output comparison
shall pass.
