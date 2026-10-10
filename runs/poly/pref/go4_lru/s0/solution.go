package solution

import "container/list"

type entry struct {
	key string
	val int
}

type LRU struct {
	cap int
	l   *list.List
	m   map[string]*list.Element
}

func NewLRU(capacity int) *LRU {
	if capacity <= 0 {
		capacity = 1
	}
	return &LRU{cap: capacity, l: list.New(), m: map[string]*list.Element{}}
}

func (c *LRU) Get(key string) (int, bool) {
	if e, ok := c.m[key]; ok {
		c.l.MoveToFront(e)
		return e.Value.(*entry).val, true
	}
	return 0, false
}

func (c *LRU) Put(key string, value int) {
	if e, ok := c.m[key]; ok {
		e.Value.(*entry).val = value
		c.l.MoveToFront(e)
		return
	}
	c.m[key] = c.l.PushFront(&entry{key, value})
	if c.l.Len() > c.cap {
		last := c.l.Back()
		c.l.Remove(last)
		delete(c.m, last.Value.(*entry).key)
	}
}

func (c *LRU) Len() int { return c.l.Len() }
