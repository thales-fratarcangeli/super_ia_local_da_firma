function matchRoute(pattern, path) {
  const ps = pattern.split("/").filter(Boolean);
  const xs = path.split("/").filter(Boolean);
  if (ps.length !== xs.length) return null;
  const out = {};
  for (let i = 0; i < ps.length; i++) {
    if (ps[i].startsWith(":")) out[ps[i].slice(1)] = decodeURIComponent(xs[i]);
    else if (ps[i] !== xs[i]) return null;
  }
  return out;
}
module.exports = { matchRoute };
