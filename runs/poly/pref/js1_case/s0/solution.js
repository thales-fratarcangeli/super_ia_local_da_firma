function camelToSnake(s) {
  return s.replace(/[A-Z]/g, (c, i) => (i === 0 ? "" : "_") + c.toLowerCase());
}
function snakeToCamel(s) {
  const parts = s.split("_").filter(Boolean);
  return parts.map((p, i) => (i === 0 ? p : p[0].toUpperCase() + p.slice(1))).join("");
}
module.exports = { camelToSnake, snakeToCamel };
