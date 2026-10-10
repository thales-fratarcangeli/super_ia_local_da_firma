
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "solution.c"
static int ok(const char *s, int want) { int v = 12345; int r = parse_int(s, &v); return r == 1 && v == want; }
static int bad(const char *s) { int v = 777; int r = parse_int(s, &v); return r == 0 && v == 777; }
int main(void) {
    assert(ok("0", 0) && ok("42", 42) && ok("-42", -42) && ok("+7", 7) && ok("007", 7));
    assert(ok("2147483647", INT_MAX) && ok("-2147483648", INT_MIN));
    assert(bad("2147483648") && bad("-2147483649") && bad("99999999999999999999"));
    assert(bad("") && bad("+") && bad("-") && bad("12a") && bad(" 1") && bad("1 ") && bad("--1") && bad("1.5") && bad("a"));
    puts("OK");
    return 0;
}
