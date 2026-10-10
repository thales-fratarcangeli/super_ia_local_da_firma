
#include <assert.h>
#include <stdio.h>
#include "solution.c"
int main(void) {
    Stack *s = stack_new();
    int v = -1;
    assert(s && stack_size(s) == 0 && stack_pop(s, &v) == 0 && v == -1);
    for (int i = 0; i < 100000; i++) stack_push(s, i);
    assert(stack_size(s) == 100000);
    for (int i = 99999; i >= 0; i--) { assert(stack_pop(s, &v) == 1 && v == i); }
    assert(stack_size(s) == 0 && stack_pop(s, &v) == 0);
    stack_push(s, 7); stack_push(s, 8);
    assert(stack_pop(s, &v) == 1 && v == 8 && stack_size(s) == 1);
    stack_free(s);
    puts("OK");
    return 0;
}
