int popcount(unsigned int x) { int c = 0; while (x) { c += x & 1u; x >>= 1; } return c; }
unsigned int reverse_bits(unsigned int x) { unsigned int r = 0; for (int i = 0; i < 32; i++) { r = (r << 1) | (x & 1u); x >>= 1; } return r; }
int is_power_of_two(unsigned int x) { return x != 0 && (x & (x - 1)) == 0; }
