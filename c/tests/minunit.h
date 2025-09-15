#pragma once
#include <stdio.h>

static int mu_tests = 0, mu_failed = 0;

#define mu_assert(msg, test) do { if (!(test)) { \
  printf("  ✗ %s\n", msg); mu_failed++; return; } } while (0)

#define mu_run(test) do { \
  mu_tests++; \
  printf("- %s ... ", #test); fflush(stdout); \
  test(); \
  if (!mu_failed) printf("ok\n"); \
} while (0)

#define mu_summary() do { \
  if (mu_failed) { \
    printf("\nFAILED: %d/%d tests failed\n", mu_failed, mu_tests); \
  } else { \
    printf("\nSUCCESS: %d tests passed\n", mu_tests); \
  } \
} while (0)
