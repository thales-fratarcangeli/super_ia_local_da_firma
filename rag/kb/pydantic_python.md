## Pydantic v2: campos e validadores
Restrições: `Field(min_length=3, max_length=20)`, `Field(ge=13, le=120)`, `Literal["member", "admin"]`, opcional `Optional[int] = Field(default=None, ge=13, le=120)`. Validador de campo: `@field_validator("username")` seguido de `@classmethod`, `def check(cls, v): ...; return v` (devolva o valor, possivelmente normalizado). Falha: levante `ValueError` dentro do validador; o erro externo é `pydantic.ValidationError`. Em v2 não existem `@validator` nem `orm_mode`: use `field_validator` e `model_config = ConfigDict(from_attributes=True)`.

## Pydantic v2: atualização parcial
Para PATCH com campos opcionais use `body.model_dump(exclude_unset=True)` e aplique só o que veio. `model_validate(obj)` converte um objeto ORM quando `from_attributes=True`.

## Texto: slug e acentos
Para remover acentos: `unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()`. Para juntar sequências de separadores em um só hífen use `re.sub(r"[^a-z0-9]+", "-", s)`: o `+` é essencial, senão cada símbolo vira um hífen. Depois `.strip("-")`.

## Percent-decoding sem urllib
`%C3%A7` representa 2 bytes de UTF-8. Decodifique acumulando os bytes (`bytearray`) e só no final faça `.decode("utf-8")`; decodificar byte a byte para caractere quebra letras multibyte. `+` vira espaço antes de decodificar `%XX`. Separe chave/valor com `partition("=")` para dividir no primeiro `=`.

## sqlite3
Sempre consultas parametrizadas: `cur.execute("... WHERE id=?", (id,))`, nunca f-string. `cur.lastrowid` é o id inserido; `cur.rowcount` diz quantas linhas mudaram (use para devolver True/False em update/delete). Faça `commit()` após escrever. Converta 0/1 para `bool` ao devolver.

## LRU cache com OrderedDict
`collections.OrderedDict` com `move_to_end(k)` ao acessar e `popitem(last=False)` ao estourar a capacidade dá LRU com operações O(1).

## Desempate determinístico com heapq
Para devolver itens em ordem com desempate alfabético use `heapq` (`heappush`/`heappop`) ou `sorted` com chave composta.

## Relógio injetado para testar tempo
Quando o enunciado dá `clock=time.monotonic` como parâmetro, guarde-o e use sempre `self.clock()` para ler o tempo; nunca chame `time.time()` direto. Isso permite testes com relógio falso.

## Não alterar a entrada
Quando pedirem para não alterar a lista recebida, trabalhe sobre `sorted(entrada)` ou uma cópia; nunca ordene nem modifique o argumento original.

## Estrutura pedida pelo enunciado
Se o enunciado diz "classe X" com métodos, implemente `class X` com esses métodos (não uma função que devolve closures). Se pede função, implemente função. Siga os nomes e assinaturas exatamente e não acrescente validações que não foram pedidas.

## Checklist de entrega
Antes de responder, releia a especificação e confira cada regra: todo caso de erro citado (ValueError, 401, 422...), valores padrão, ordenação, nomes exatos de funções/classes/arquivos e formato do retorno.
