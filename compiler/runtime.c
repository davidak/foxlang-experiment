/* FoxLang runtime: included once in each generated translation unit. */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <inttypes.h>
#include <string.h>

static void rt_error(const char *loc, const char *id, const char *message) {
    fprintf(stderr, "%s: error[%s]: %s\n", loc, id, message);
    exit(2);
}

static void rt_print_text(const char *value, const char *loc) {
    if (printf("%s\n", value) < 0 || fflush(stdout) == EOF)
        rt_error(loc, "R005", "could not write standard output");
}

static void rt_print_int(int64_t value, const char *loc) {
    if (printf("%" PRId64 "\n", value) < 0 || fflush(stdout) == EOF)
        rt_error(loc, "R005", "could not write standard output");
}

static void rt_print_bool(bool value, const char *loc) {
    rt_print_text(value ? "true" : "false", loc);
}

static int64_t rt_add(int64_t a, int64_t b, const char *loc) {
    int64_t result;
    if (__builtin_add_overflow(a, b, &result)) rt_error(loc, "R001", "integer addition overflow");
    return result;
}

static int64_t rt_sub(int64_t a, int64_t b, const char *loc) {
    int64_t result;
    if (__builtin_sub_overflow(a, b, &result)) rt_error(loc, "R001", "integer subtraction/negation overflow");
    return result;
}

static int64_t rt_mul(int64_t a, int64_t b, const char *loc) {
    int64_t result;
    if (__builtin_mul_overflow(a, b, &result)) rt_error(loc, "R001", "integer multiplication overflow");
    return result;
}

static void rt_divisor(int64_t a, int64_t b, const char *loc) {
    if (b == 0) rt_error(loc, "R002", "division or remainder by zero");
    if (a == INT64_MIN && b == -1) rt_error(loc, "R001", "integer division/remainder overflow");
}

static int64_t rt_div(int64_t a, int64_t b, const char *loc) {
    rt_divisor(a, b, loc);
    return a / b;
}

static int64_t rt_rem(int64_t a, int64_t b, const char *loc) {
    rt_divisor(a, b, loc);
    return a % b;
}

static int64_t rt_index(int64_t index, int64_t length, const char *loc) {
    if (index < 0 || index >= length) rt_error(loc, "R003", "array index outside bounds");
    return index;
}

static bool rt_space(int c) {
    return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\v' || c == '\f';
}

static int64_t rt_read_int(const char *loc) {
    /* Streaming conversion: constant memory, no locale or permissive strtol. */
    int c;
    do { c = getchar(); } while (rt_space(c));
    bool negative = c == '-';
    if (c == '-' || c == '+') c = getchar();
    uint64_t limit = negative ? UINT64_C(9223372036854775808) : INT64_MAX;
    uint64_t value = 0;
    bool digits = false;
    while (c >= '0' && c <= '9') {
        digits = true;
        unsigned digit = (unsigned)(c - '0');
        if (value > (limit - digit) / 10)
            rt_error(loc, "R004", "input integer outside signed 64-bit range");
        value = value * 10 + digit;
        c = getchar();
    }
    while (rt_space(c)) c = getchar();
    if (ferror(stdin)) rt_error(loc, "R005", "could not read standard input");
    if (!digits || c != EOF)
        rt_error(loc, "R004", "expected exactly one signed decimal integer before EOF");
    if (negative && value == UINT64_C(9223372036854775808)) return INT64_MIN;
    return negative ? -(int64_t)value : (int64_t)value;
}

#include <setjmp.h>
#include <signal.h>
static jmp_buf rt_jump;
static bool rt_testing = false;
static const char *rt_test_name = "<program>";

static void rt_start(void) {
#ifdef SIGPIPE
    signal(SIGPIPE, SIG_IGN);
#endif
}

static void rt_failure_prefix(const char *loc) {
    fprintf(stderr, "%s: assertion failed in %s: ", loc, rt_test_name);
}

static void rt_abort_assertion(void) {
    if (rt_testing) longjmp(rt_jump, 1);
    exit(1);
}

static void rt_assert(bool condition, const char *message, const char *loc) {
    if (condition) return;
    rt_failure_prefix(loc);
    fprintf(stderr, "%s\n", message);
    rt_abort_assertion();
}

static void rt_compare_int(int64_t actual, int64_t expected, bool equal, const char *loc) {
    if ((actual == expected) == equal) return;
    rt_failure_prefix(loc);
    fprintf(stderr, "expected %s; actual=%" PRId64 ", expected=%" PRId64 "\n",
        equal ? "equality" : "inequality", actual, expected);
    rt_abort_assertion();
}

static void rt_compare_bool(bool actual, bool expected, bool equal, const char *loc) {
    if ((actual == expected) == equal) return;
    rt_failure_prefix(loc);
    fprintf(stderr, "expected %s; actual=%s, expected=%s\n", equal ? "equality" : "inequality",
        actual ? "true" : "false", expected ? "true" : "false");
    rt_abort_assertion();
}

static void rt_compare_text(const char *actual, const char *expected, bool equal, const char *loc) {
    if ((strcmp(actual, expected) == 0) == equal) return;
    rt_failure_prefix(loc);
    fprintf(stderr, "expected %s; actual=\"%s\", expected=\"%s\"\n",
        equal ? "equality" : "inequality", actual, expected);
    rt_abort_assertion();
}
