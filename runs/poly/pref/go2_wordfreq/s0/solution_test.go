
package solution

import (
	"reflect"
	"testing"
)

func TestWordFreq(t *testing.T) {
	got := WordFreq("Olá, olá! Mundo mundo; MUNDO")
	want := map[string]int{"olá": 2, "mundo": 3}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v want %v", got, want)
	}
	got = WordFreq("a1 b-2 a1,B_2")
	want = map[string]int{"a1": 2, "b": 2, "2": 2}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v want %v", got, want)
	}
}

func TestWordFreqEmpty(t *testing.T) {
	for _, s := range []string{"", "  ,.;! "} {
		m := WordFreq(s)
		if m == nil || len(m) != 0 {
			t.Fatalf("%q: esperava mapa vazio não nulo, got %v", s, m)
		}
	}
}
