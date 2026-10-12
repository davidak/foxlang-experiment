# FoxLang language reference (version 0.1)

FoxLang compiles one UTF-8 source file to a native executable through C11.
There are no imports, globals, objects, floats or implicit conversions. The
compiler automatically includes the small testing library. Programs use `.fox`.

## Getting started

```
fn square(n: int) -> int {
    return n * n;
}

fn main() {
    let value = read_int();
    print(square(value));
}

test "square of twelve" {
    assert_eq(square(12), 144);
}
```

Run `python3 fox.py build example.fox -o build/example`, then `./build/example`.
Run `python3 fox.py test example.fox` to compile and execute its tests. Test mode
never calls main. Both modes check the whole file, including test bodies.
Normal builds require `fn main()` with no parameters and no result. Test builds
need no main. Test names must be unique; zero tests reports `0 passed; 0 failed`
and succeeds. Tests run in declaration order. There is no filesystem discovery:
pass one source file per command. Put tests beside functions in that file.

## Lexical rules and formatting

Identifiers are ASCII `[A-Za-z_][A-Za-z0-9_]*`, case sensitive. Keywords are
`fn let var if else while return test true false int bool text`. Comments start
with `//` and end at a newline. Whitespace separates tokens and is otherwise
ignored. Write four-space indentation, braces, and one statement per line.
Semicolons terminate simple statements; newlines do not terminate expressions.
Integer literals are decimal digits only (leading zeros still mean decimal).
Text literals use double quotes with only `\n`, `\r`, `\t`, `\"`, `\\` escapes.
Literal newlines, control characters and NUL are forbidden inside text. Unicode
text is encoded as UTF-8; text comparisons compare bytes, without normalization.
Source locations are 1-based Unicode character columns, with a tab counting as
one character. LF and CRLF source files are accepted.

## Grammar

EBNF: `{x}` means repetition, `[x]` optional; quoted items are tokens. `IDENT`,
`INT`, and `STRING` follow the lexical rules. Keywords cannot be identifiers.

```
file       = { function | test } ;
function   = "fn" IDENT "(" [ parameter { "," parameter } ] ")"
             [ "->" scalar ] block ;
parameter  = IDENT ":" scalar ;
scalar     = "int" | "bool" | "text" ;
test       = "test" STRING block ;
block      = "{" { statement } "}" ;
if-stmt    = "if" expression block [ "else" (block | if-stmt) ] ;
statement  = ("let" | "var") IDENT "=" expression ";"
           | IDENT "=" expression ";"
           | if-stmt
           | "while" expression block
           | "return" [ expression ] ";"
           | expression ";" ;
expression = or ;
or         = and { "||" and } ;
and        = equality { "&&" equality } ;
equality   = ordering { ("==" | "!=") ordering } ;
ordering   = sum { ("<" | "<=" | ">" | ">=") sum } ;
sum        = product { ("+" | "-") product } ;
product    = unary { ("*" | "/" | "%") unary } ;
unary      = ("-" | "!") unary | postfix ;
postfix    = primary { "[" expression "]" } ;
primary    = INT | STRING | "true" | "false" | IDENT
           | IDENT "(" [ expression { "," expression } ] ")"
           | "(" expression ")"
           | "[" expression { "," expression } "]" ;
```

Calls name functions
directly; functions are not values. Only function calls can be expression
statements. Trailing commas are not accepted.

## Values, bindings, functions and control flow

`int` is signed 64-bit, range -9223372036854775808 through 9223372036854775807.
The negative minimum literal is accepted when unary minus applies directly to
the literal 9223372036854775808 (parentheses around the literal are allowed). That positive magnitude is otherwise invalid.
`bool` has exactly `true` and `false`. `text` is immutable; no concatenation,
indexing or conversion is provided. It can be passed and returned by functions.

`let` creates an immutable binding; `var` a mutable scalar binding. Types are
inferred from initializers and cannot change. All bindings are initialized.
Blocks have lexical scope. Redeclaration or shadowing of any visible local is
an error. Names of functions and standard functions cannot be local bindings.
Function and test names are independently unique. Parameters are immutable.
Functions can call later declarations, themselves, and each other. Arguments
and results are scalar values. Omitting `->` means no result (void); void is
not a value or a source type. Return expressions must be scalar values matching the result type.
Every path through a result-bearing function must return. For conservative
analysis, a loop may execute zero times even with a literal true condition.
Statements after a definitely returning statement are rejected. Void functions
may fall through or use `return;`. Return inside a test is forbidden.

`if` and `while` require bool conditions. There are no implicit truth values,
`break`, `continue` or counted-loop constructs. Arithmetic operators take int;
order comparisons take int and yield bool; equality takes two values of the
same scalar type. `!` takes bool; `&&` and `||` short circuit and take bool.
Operators of each precedence level associate left to right. Expressions,
function arguments, and array elements evaluate left to right, exactly once.
Chained comparisons are not special syntax (`1 < 2 < 3` is a type error).

Division truncates toward zero; remainder has the dividend's sign. Overflow
in addition, subtraction, multiplication or negation, division/remainder by
zero, and minimum-int divided or remaindered by -1 terminate with a source
location, stable runtime identifier, meaningful stderr and exit status 2.
No wrapped signed arithmetic is permitted. Recursion depth and available
memory are limited by the host; exhaustion is not reliably diagnosed.

## Collections

A nonempty `[1, 2, 3]` literal creates a fixed-length integer array. Elements
must all be int. Arrays are immutable local values, introduced with `let`;
array aliases, mutable arrays, nested arrays, array parameters/results and
array equality are not supported. Access `values[index]` requires an int and
checks `0 <= index < len(values)` at runtime. Out-of-bounds access exits 2.
`len` accepts any array expression and returns its length as int. An array
literal is evaluated once even when used with len or indexed directly.

## Standard library

See [stdlib.md](stdlib.md) for complete signatures and failures. All standard
names are reserved in the function namespace. `print` prints int, bool or text
with one LF; `read_int()` strictly reads one integer from stdin through EOF.
There is no recoverable I/O result type yet; invalid input and I/O failure
terminate with status 2 and stderr. `len` is the only collection operation.

## Native tests

`test "descriptive name" { ... }` is a dedicated declaration, not an entry
point. It has a fresh local scope and may call program functions. Standard
assertions are available in functions as well as tests:

```
test "assertion examples" {
    assert_true(2 < 3);
    assert_false(2 > 3);
    assert_eq(2 + 3, 5);
    assert_ne("fox", "wolf");
    assert(true, "custom explanation");
    // fail("explanation"); // deliberately fail the current test
}
```

A failed assertion aborts the current test; subsequent tests still run. The
runner prints `PASS name` or `FAIL name` per test and finishes with
`N passed; M failed` on stdout. Failure details on stderr identify the name,
assertion call's location, and message. Equality/inequality failures show both
values. Status is 0 if all pass, 1 if any assertion fails. A runtime error
(such as overflow) exits 2 immediately, without a final summary. Assertions
executed in normal mode exit 1 on failure. The location of a user-written
assertion helper is the assertion inside that helper; automatic library
wrappers preserve their caller's location. Test names cannot be empty or
contain control characters. Normal mode emits no test result output.

## Diagnostics, CLI and limits

`python3 fox.py build FILE [-o build/program]` writes C beside the executable
as `OUTPUT.c`, then invokes `cc` (or the single executable named by `CC`).
`python3 fox.py test FILE [-o build/tests]` builds and runs tests. Parent
output directories are created. Compilation errors exit 1; command-line
usage errors exit 2; test mode forwards the executable's exit status.
Generated files belong under build. Stale executable/C outputs at the chosen
output path are removed before compilation so a failure cannot appear as a
successful rebuild. Do not choose a source file as an output path.

Diagnostics have `path:line:column: error[ID]: explanation`, with optional
`hint:`. E001 lexical, E002 syntax, E100 unknown name, E101 duplicate name,
E102 type/operation, E103 call/arity, E104 binding mutation, E105 control flow,
E106 collection, E107 entry point, E108 integer literal range; E900 file or
backend failure. Runtime IDs: R001 overflow, R002 division by zero, R003
bounds, R004 invalid input/range/EOF, R005 I/O. The first compiler error is
reported deterministically. Runtime errors point to the operator or call.

This implementation is intentionally single-file and uses a GCC-compatible
C11 backend (checked overflow builtins). No optimizer, package manager,
formatter, debugger integration or editor server is provided. Host stack,
memory and filesystem failures remain host limitations. No claim of binary
reproducibility or real-time suitability is made.
