#include <stdlib.h>
typedef struct Node { int v; struct Node *next; } Node;
struct Stack { Node *top; int n; };
typedef struct Stack Stack;
Stack *stack_new(void) { Stack *s = malloc(sizeof *s); if (s) { s->top = NULL; s->n = 0; } return s; }
void stack_push(Stack *s, int v) { Node *x = malloc(sizeof *x); x->v = v; x->next = s->top; s->top = x; s->n++; }
int stack_pop(Stack *s, int *out) { if (!s->top) return 0; Node *x = s->top; *out = x->v; s->top = x->next; free(x); s->n--; return 1; }
int stack_size(const Stack *s) { return s->n; }
void stack_free(Stack *s) { int t; while (stack_pop(s, &t)) {} free(s); }
