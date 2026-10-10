
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "solution.c"
int main(void) {
    char a[] = "  hi there \t\n"; trim_in_place(a); assert(strcmp(a, "hi there") == 0);
    char b[] = "   \t "; trim_in_place(b); assert(strcmp(b, "") == 0);
    char c[] = "ok"; trim_in_place(c); assert(strcmp(c, "ok") == 0);
    char d[] = ""; trim_in_place(d); assert(strcmp(d, "") == 0);
    char e[] = "x   y  "; trim_in_place(e); assert(strcmp(e, "x   y") == 0);
    assert(count_words(" a  bb\tccc\n") == 3);
    assert(count_words("") == 0 && count_words("   ") == 0 && count_words("one") == 1 && count_words("a b") == 2);
    puts("OK");
    return 0;
}
