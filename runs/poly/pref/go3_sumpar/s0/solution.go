package solution

import "sync"

func SumParallel(nums []int, workers int) int {
	if workers <= 0 {
		workers = 1
	}
	if workers > len(nums) {
		workers = len(nums)
	}
	if len(nums) == 0 {
		return 0
	}
	parts := make([]int, workers)
	var wg sync.WaitGroup
	size := (len(nums) + workers - 1) / workers
	for w := 0; w < workers; w++ {
		lo, hi := w*size, (w+1)*size
		if hi > len(nums) {
			hi = len(nums)
		}
		if lo >= hi {
			continue
		}
		wg.Add(1)
		go func(w, lo, hi int) {
			defer wg.Done()
			s := 0
			for _, v := range nums[lo:hi] {
				s += v
			}
			parts[w] = s
		}(w, lo, hi)
	}
	wg.Wait()
	total := 0
	for _, p := range parts {
		total += p
	}
	return total
}
