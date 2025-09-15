#pragma once
#include <stdio.h>

#ifndef PLAYGROUND_ROOT
#define PLAYGROUND_ROOT "."
#endif

const char* pg_root(void);        // "playground" の絶対パス
void pg_vectors_path(char* buf, size_t n); // ".../data/vectors"
void pg_results_path(char* buf, size_t n); // ".../data/results"
