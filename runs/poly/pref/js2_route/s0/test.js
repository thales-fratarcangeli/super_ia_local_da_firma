
const assert = require("assert");
const { matchRoute } = require("./solution");
assert.deepStrictEqual(matchRoute("/users/:id", "/users/42"), { id: "42" });
assert.deepStrictEqual(matchRoute("/a/:x/b/:y", "/a/1/b/2/"), { x: "1", y: "2" });
assert.strictEqual(matchRoute("/users/:id", "/users"), null);
assert.strictEqual(matchRoute("/users/:id", "/users/1/extra"), null);
assert.strictEqual(matchRoute("/users/:id", "/posts/1"), null);
assert.deepStrictEqual(matchRoute("/", "/"), {});
assert.strictEqual(matchRoute("/", "/x"), null);
assert.deepStrictEqual(matchRoute("/files/:name", "/files/a%20b"), { name: "a b" });
assert.deepStrictEqual(matchRoute("//a//:v/", "/a/9"), { v: "9" });
assert.strictEqual(matchRoute("/a/:v", "/a//"), null);
console.log("OK");
