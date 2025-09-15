#include "minunit.h"
#include <string.h>
#include "../include/p002_utils.h"

static void t_paths_contain_expected_dirs(void) {
    char buf[512];
    pg_vectors_path(buf, sizeof buf);
    mu_assert("vectors path must contain /data/vectors", strstr(buf, "/data/vectors") != NULL);

    pg_results_path(buf, sizeof buf);
    mu_assert("results path must contain /data/results", strstr(buf, "/data/results") != NULL);
}

int main(void) {
    mu_run(t_paths_contain_expected_dirs);
    mu_summary();
    return mu_failed ? 1 : 0;
}
