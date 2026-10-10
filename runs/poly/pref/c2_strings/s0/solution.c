#include <ctype.h>
#include <string.h>
void trim_in_place(char *s) {
    size_t n = strlen(s), i = 0;
    while (i < n && isspace((unsigned char)s[i])) i++;
    while (n > i && isspace((unsigned char)s[n - 1])) n--;
    memmove(s, s + i, n - i);
    s[n - i] = '\0';
}
int count_words(const char *s) {
    int c = 0, in = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) in = 0;
        else if (!in) { in = 1; c++; }
    }
    return c;
}
