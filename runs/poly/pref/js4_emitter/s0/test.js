
const assert = require("assert");
const { EventEmitter } = require("./solution");
const e = new EventEmitter();
const log = [];
assert.strictEqual(e.on("x", (a, b) => log.push(["1", a, b])), e);
e.on("x", () => log.push(["2"]));
assert.strictEqual(e.emit("x", 10, 20), true);
assert.deepStrictEqual(log, [["1", 10, 20], ["2"]]);
assert.strictEqual(e.emit("nada"), false);
assert.strictEqual(e.listenerCount("x"), 2);

const f = new EventEmitter(); let n = 0;
f.once("o", () => n++);
f.emit("o"); f.emit("o");
assert.strictEqual(n, 1); assert.strictEqual(f.listenerCount("o"), 0);

const g = new EventEmitter(); let m = 0; const h = () => m++;
g.on("a", h); g.on("a", h);
g.off("a", h);
assert.strictEqual(g.listenerCount("a"), 1);
g.once("b", h); g.off("b", h); g.emit("b");
assert.strictEqual(m, 0);

const k = new EventEmitter(); const order = [];
const self = () => { order.push("self"); k.off("z", self); };
k.on("z", self); k.on("z", () => order.push("other"));
k.emit("z"); k.emit("z");
assert.deepStrictEqual(order, ["self", "other", "other"]);
console.log("OK");
