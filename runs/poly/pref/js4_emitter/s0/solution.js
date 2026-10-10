class EventEmitter {
  constructor() { this.m = new Map(); }
  on(ev, fn) { if (!this.m.has(ev)) this.m.set(ev, []); this.m.get(ev).push({ fn }); return this; }
  once(ev, fn) { if (!this.m.has(ev)) this.m.set(ev, []); this.m.get(ev).push({ fn, once: true }); return this; }
  off(ev, fn) {
    const l = this.m.get(ev); if (!l) return this;
    const i = l.findIndex((x) => x.fn === fn);
    if (i >= 0) l.splice(i, 1);
    return this;
  }
  emit(ev, ...args) {
    const l = this.m.get(ev);
    if (!l || l.length === 0) return false;
    for (const x of [...l]) {
      if (x.once) { const i = l.indexOf(x); if (i >= 0) l.splice(i, 1); }
      x.fn(...args);
    }
    return true;
  }
  listenerCount(ev) { return (this.m.get(ev) || []).length; }
}
module.exports = { EventEmitter };
