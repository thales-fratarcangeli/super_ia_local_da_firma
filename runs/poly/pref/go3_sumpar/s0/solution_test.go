
package solution

import "testing"

func TestSumParallel(t *testing.T) {
	n := 1000000
	nums := make([]int, n)
	want := 0
	for i := range nums {
		nums[i] = i + 1
		want += i + 1
	}
	for _, w := range []int{1, 2, 4, 7, 16, 1000, 5000000} {
		if got := SumParallel(nums, w); got != want {
			t.Fatalf("workers=%d got %d want %d", w, got, want)
		}
	}
}

func TestSumParallelEdges(t *testing.T) {
	if SumParallel(nil, 4) != 0 || SumParallel([]int{}, 4) != 0 {
		t.Fatal("vazio deveria dar 0")
	}
	for _, w := range []int{0, -3, 1, 10} {
		if got := SumParallel([]int{5, -2, 10}, w); got != 13 {
			t.Fatalf("workers=%d got %d", w, got)
		}
	}
}
