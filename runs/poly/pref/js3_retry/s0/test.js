
const assert = require("assert");
const { retry } = require("./solution");
(async () => {
  let calls = 0;
  const r = await retry(async (a) => { calls++; if (a < 3) throw new Error("e" + a); return "ok" + a; }, { retries: 5 });
  assert.strictEqual(r, "ok3"); assert.strictEqual(calls, 3);

  calls = 0;
  await assert.rejects(() => retry(() => { calls++; throw new Error("e" + calls); }, { retries: 2 }), (e) => e.message === "e2");
  assert.strictEqual(calls, 2);

  assert.strictEqual(await retry(() => 42), 42);   // função síncrona

  const t0 = Date.now();
  calls = 0;
  await retry((a) => { calls++; if (a < 3) throw new Error("x"); return 1; }, { retries: 3, delayMs: 60 });
  assert.ok(Date.now() - t0 >= 100, "deveria esperar entre tentativas");

  await assert.rejects(() => retry(() => 1, { retries: 0 }), RangeError);
  console.log("OK");
})().catch((e) => { console.error(e); process.exit(1); });
