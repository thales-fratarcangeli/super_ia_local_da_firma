# Baseline qwen3:8b cru — 0/21 testes (1515 s de geração, 3534 tokens)

Causa-raiz dos 20 falhos: um único bug em models.py.
1. `User.tasks = relationship("Task")` sem FK entre users e tasks -> SQLAlchemy NoForeignKeysError; todos os mappers quebram.
2. `models.py` importa `Base` de `app.main` (import circular) e usa `SessionLocal` como type hint.
3. Header Authorization declarado como obrigatório -> 422 em vez de 401 (teste test_protected_requires_token).
4. Spec pedia hash bcrypt / `password` nunca no retorno: coluna se chama `password` (hash não verificado ainda).
5. Resposta ficou sem fence final no último arquivo (auth.py truncado em `raise HTTP`) -> parser original perderia o arquivo.
Padrão: modelo gerou código "plausível", sem nunca executá-lo. Um loop de execução + correção ataca 1-3 direto.
