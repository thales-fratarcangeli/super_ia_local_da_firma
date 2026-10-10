
package solution

import "testing"

func TestFib(t *testing.T) {
	cases := map[int]int{0: 0, 1: 1, 2: 1, 10: 55, 50: 12586269025, 90: 2880067194370816120, 92: 7540113804746346429}
	for n, want := range cases {
		got, err := Fib(n)
		if err != nil || got != want {
			t.Fatalf("Fib(%d) = %d, %v; want %d", n, got, err, want)
		}
	}
}

func TestFibErrors(t *testing.T) {
	for _, n := range []int{-1, -100, 93, 1000} {
		if _, err := Fib(n); err == nil {
			t.Fatalf("Fib(%d) deveria dar erro", n)
		}
	}
}
