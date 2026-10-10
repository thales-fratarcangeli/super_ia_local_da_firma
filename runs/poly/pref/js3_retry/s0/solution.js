async function retry(fn, { retries = 3, delayMs = 0 } = {}) {
  if (retries < 1) throw new RangeError("retries");
  let last;
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fn(attempt);
    } catch (e) {
      last = e;
      if (attempt < retries && delayMs > 0) await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw last;
}
module.exports = { retry };
