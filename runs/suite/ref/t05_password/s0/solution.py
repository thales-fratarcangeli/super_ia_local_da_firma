import base64
import hashlib
import hmac
import os

def hash_password(password):
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return "pbkdf2$100000$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(h).decode()

def verify_password(password, stored):
    try:
        scheme, it, salt, h = stored.split("$")
        if scheme != "pbkdf2":
            return False
        calc = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt, validate=True), int(it))
        return hmac.compare_digest(calc, base64.b64decode(h, validate=True))
    except Exception:
        return False
