
const assert = require("assert");
const { camelToSnake, snakeToCamel } = require("./solution");
assert.strictEqual(camelToSnake("helloWorldFoo"), "hello_world_foo");
assert.strictEqual(camelToSnake("HelloWorld"), "hello_world");
assert.strictEqual(camelToSnake("userID"), "user_i_d");
assert.strictEqual(camelToSnake(""), "");
assert.strictEqual(camelToSnake("abc"), "abc");
assert.strictEqual(snakeToCamel("hello_world_foo"), "helloWorldFoo");
assert.strictEqual(snakeToCamel("_private_var"), "privateVar");
assert.strictEqual(snakeToCamel("a__b"), "aB");
assert.strictEqual(snakeToCamel(""), "");
assert.strictEqual(snakeToCamel("single"), "single");
console.log("OK");
