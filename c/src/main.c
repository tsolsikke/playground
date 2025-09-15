#include "../include/p002_utils.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc <= 1) {
        fprintf(stderr, "usage: play-cli <hello|io>\n");
        return 1;
    }
    if (strcmp(argv[1], "hello") == 0) {
        puts("Hello from C playground!");
        return 0;
    }
    if (strcmp(argv[1], "io") == 0) {
        char vin[512], vout[512];
        pg_vectors_path(vin, sizeof vin);
        pg_results_path(vout, sizeof vout);
        strncat(vin, "/example.txt", sizeof(vin) - strlen(vin) - 1);
        strncat(vout, "/out.txt", sizeof(vout) - strlen(vout) - 1);

        FILE* in = fopen(vin, "r");
        if (!in) { perror("open input"); return 1; }
        FILE* out = fopen(vout, "w");
        if (!out) { perror("open output"); fclose(in); return 1; }

        int ch;
        while ((ch = fgetc(in)) != EOF) fputc(ch, out);
        fclose(in); fclose(out);
        printf("copied: %s -> %s\n", vin, vout);
        return 0;
    }
    fprintf(stderr, "unknown command: %s\n", argv[1]);
    return 1;
}
