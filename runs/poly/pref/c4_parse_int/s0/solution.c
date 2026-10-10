#include <limits.h>
int parse_int(const char *s, int *out) {
    int neg = 0;
    if (*s == '+' || *s == '-') { neg = (*s == '-'); s++; }
    if (*s < '0' || *s > '9') return 0;
    long long v = 0;
    for (; *s; s++) {
        if (*s < '0' || *s > '9') return 0;
        v = v * 10 + (*s - '0');
        if (v > (long long)INT_MAX + 1) return 0;
    }
    if (neg) v = -v;
    if (v > INT_MAX || v < INT_MIN) return 0;
    *out = (int)v;
    return 1;
}
