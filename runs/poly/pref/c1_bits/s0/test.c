
#include <assert.h>
#include <stdio.h>
#include "solution.c"
int main(void) {
    assert(popcount(0) == 0 && popcount(0xFFFFFFFFu) == 32 && popcount(0xF0F0u) == 8 && popcount(1) == 1);
    assert(reverse_bits(0) == 0 && reverse_bits(1) == 0x80000000u && reverse_bits(0xFu) == 0xF0000000u);
    assert(reverse_bits(0x80000000u) == 1 && reverse_bits(0xFFFFFFFFu) == 0xFFFFFFFFu && reverse_bits(0x12345678u) == 0x1E6A2C48u);
    assert(is_power_of_two(1) && is_power_of_two(64) && is_power_of_two(0x80000000u));
    assert(!is_power_of_two(0) && !is_power_of_two(65) && !is_power_of_two(0xFFFFFFFFu));
    puts("OK");
    return 0;
}
