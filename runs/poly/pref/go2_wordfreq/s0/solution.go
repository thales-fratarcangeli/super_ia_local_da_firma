package solution

import (
	"strings"
	"unicode"
)

func WordFreq(text string) map[string]int {
	out := map[string]int{}
	for _, w := range strings.FieldsFunc(text, func(r rune) bool { return !unicode.IsLetter(r) && !unicode.IsDigit(r) }) {
		out[strings.ToLower(w)]++
	}
	return out
}
