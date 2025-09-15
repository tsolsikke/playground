#include "../include/p002_utils.h"
#include <string.h>

const char* pg_root(void) { return PLAYGROUND_ROOT; }

void join3(char* buf, size_t n, const char* a, const char* b, const char* c) {
    snprintf(buf, n, "%s/%s/%s", a, b, c);
}

void pg_vectors_path(char* buf, size_t n) {
    join3(buf, n, pg_root(), "data", "vectors");
}

void pg_results_path(char* buf, size_t n) {
    join3(buf, n, pg_root(), "data", "results");
}
