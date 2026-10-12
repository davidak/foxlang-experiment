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
