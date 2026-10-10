# Tarefa: API de gerenciamento de tarefas

Implemente uma API em Python com **FastAPI + SQLAlchemy 2.0 + SQLite + PyJWT + bcrypt**.

## Estrutura obrigatória
- `app/main.py` deve expor a variável `app` (instância FastAPI).
- O banco vem da variável de ambiente `DATABASE_URL` (padrão `sqlite:///./app.db`), lida na importação.
  As tabelas devem ser criadas automaticamente na importação de `app.main`.
- Segredo JWT vem de `JWT_SECRET` (padrão `dev-secret`). Algoritmo HS256, expiração de 60 minutos.
- Você pode dividir em quantos módulos quiser dentro de `app/` (models, schemas, auth, routers...).

## Autenticação
- `POST /auth/register` body JSON `{"username": str, "password": str, "role": "member"|"admin"}` (`role` opcional, padrão `member`).
  - 201 com `{"id", "username", "role"}` (nunca devolver a senha/hash).
  - 409 se o username já existe. 422 se o password tiver menos de 6 caracteres ou role inválido.
  - A senha deve ser guardada com hash bcrypt.
- `POST /auth/login` body JSON `{"username", "password"}`.
  - 200 com `{"access_token": str, "token_type": "bearer"}`. 401 se credenciais inválidas.
- Todas as demais rotas exigem header `Authorization: Bearer <token>`; sem token ou token inválido/expirado => 401.

## Projetos
- `POST /projects` body `{"name": str}` (nome não vazio, senão 422) => 201 `{"id", "name", "owner_id"}`.
- `GET /projects` => `{"items": [...], "total": int, "page": int, "page_size": int}`.
  - Query: `page` (padrão 1, mínimo 1), `page_size` (padrão 10, mínimo 1, máximo 50) — valores inválidos => 422.
  - `member` vê só os próprios projetos; `admin` vê todos. Ordenar por `id` crescente.
- `GET /projects/{id}` => 200; 404 se não existe; 403 se não é dono e não é admin.
- `DELETE /projects/{id}` => 204; mesmas regras de 404/403; apaga também as tarefas do projeto.

## Tarefas
- `POST /projects/{project_id}/tasks` body `{"title": str, "description": str|null, "status": "todo"|"doing"|"done"}`
  (`description` opcional, `status` padrão `todo`; título vazio ou status inválido => 422)
  => 201 `{"id", "project_id", "title", "description", "status"}`. Mesmas regras de 404/403 do projeto.
- `GET /projects/{project_id}/tasks` => `{"items", "total", "page", "page_size"}` com os mesmos parâmetros de
  paginação e filtro opcional `?status=todo|doing|done` (status inválido => 422). Ordenar por `id` crescente.
- `PATCH /tasks/{task_id}` body parcial (qualquer subconjunto de `title`, `description`, `status`) => 200 com a tarefa.
  404 se não existe; 403 se o projeto da tarefa não é do usuário e ele não é admin.
- `DELETE /tasks/{task_id}` => 204; mesmas regras de 404/403.

## Entrega
Responda com **todos os arquivos** necessários, cada um no formato:

### FILE: caminho/do/arquivo.py
```python
codigo
```

Não escreva testes. Não explique nada fora dos blocos de arquivo.
