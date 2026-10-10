import re

_RE = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")

def parse_duration(text):
    if re.fullmatch(r"\d+", text):
        return int(text)
    m = _RE.fullmatch(text)
    if not text or not m:
        raise ValueError("invalid")
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s

def format_duration(seconds):
    if seconds < 0:
        raise ValueError("negative")
    if seconds == 0:
        return "0s"
    out = ""
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        q, seconds = divmod(seconds, size)
        if q:
            out += f"{q}{unit}"
    return out
