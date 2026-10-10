
package solution

import "testing"

func TestLRU(t *testing.T) {
	c := NewLRU(2)
	c.Put("a", 1)
	c.Put("b", 2)
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Fatal("a")
	}
	c.Put("c", 3)
	if _, ok := c.Get("b"); ok {
		t.Fatal("b deveria ter sido removido")
	}
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Fatal("a deveria continuar")
	}
	if c.Len() != 2 {
		t.Fatalf("len %d", c.Len())
	}
}

func TestLRUUpdateRefreshes(t *testing.T) {
	c := NewLRU(2)
	c.Put("a", 1)
	c.Put("b", 2)
	c.Put("a", 10)
	c.Put("c", 3)
	if v, ok := c.Get("a"); !ok || v != 10 {
		t.Fatal("a=10")
	}
	if _, ok := c.Get("b"); ok {
		t.Fatal("b removido")
	}
	z := NewLRU(0)
	z.Put("x", 1)
	z.Put("y", 2)
	if z.Len() != 1 {
		t.Fatal("capacidade 0 vira 1")
	}
}

func TestLRUBig(t *testing.T) {
	c := NewLRU(1000)
	for i := 0; i < 200000; i++ {
		c.Put(string(rune('a'+i%26))+string(rune('a'+(i/26)%26))+string(rune('a'+(i/676)%26)), i)
	}
	if c.Len() > 1000 {
		t.Fatal("estourou")
	}
}
