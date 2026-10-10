## PyJWT 2.x: encode, decode e exceções
No PyJWT 2.x `jwt.encode(payload, secret, algorithm="HS256")` já devolve `str`: nunca chame `.decode()` nele. `jwt.decode(token, secret, algorithms=["HS256"])` exige o argumento `algorithms` (lista). Todas as falhas (expirado, assinatura errada, token malformado) herdam de `jwt.PyJWTError`. O claim `exp` deve ser um `datetime` com timezone UTC (`datetime.datetime.now(datetime.timezone.utc) + timedelta(...)`). O claim `sub` deve ser string.

## PyJWT: claims obrigatórios
Para tratar token sem um claim, leia com `payload["sub"]` dentro de try/except (KeyError) ou use `jwt.decode(..., options={"require": ["exp", "sub"]})`. Converta `sub` para int só depois de decodificar, tratando ValueError.

## bcrypt
`bcrypt.hashpw(password.encode(), bcrypt.gensalt())` devolve `bytes`; guarde `.decode()` em coluna de texto. `bcrypt.checkpw(password.encode(), hashed.encode())` devolve bool. Nunca guarde nem devolva a senha em texto puro; respostas da API não incluem o hash.

## PBKDF2 com hashlib
`hashlib.pbkdf2_hmac("sha256", password_bytes, salt_bytes, iterations)` devolve `bytes`. Salt aleatório: `os.urandom(16)` devolve exatamente 16 bytes; em base64 isso ocupa 24 caracteres, não 16. `base64.b64encode(x)` devolve `bytes`: use `.decode()` para montar a string. Compare hashes com `hmac.compare_digest(a, b)` (tempo constante), nunca com `==`.

## Verificar entrada malformada
Ao parsear um valor armazenado (split, base64, int), envolva tudo em `try/except Exception` e devolva `False`/`None` em vez de deixar a exceção vazar. Use `base64.b64decode(s, validate=True)` para rejeitar lixo.
