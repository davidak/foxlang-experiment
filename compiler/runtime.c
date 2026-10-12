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
