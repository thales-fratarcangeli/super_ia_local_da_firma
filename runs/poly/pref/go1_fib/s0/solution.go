package solution

import "errors"

func Fib(n int) (int, error) {
	if n < 0 {
		return 0, errors.New("negative")
	}
	if n > 92 {
		return 0, errors.New("overflow")
	}
	a, b := 0, 1
	for i := 0; i < n; i++ {
		a, b = b, a+b
	}
	return a, nil
}
