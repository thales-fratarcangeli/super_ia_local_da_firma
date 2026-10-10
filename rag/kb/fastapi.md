## FastAPI: autenticação Bearer e status 401
`HTTPBearer()` com `auto_error=True` escolhe o status por conta própria, que varia entre versões do FastAPI. Para controlar: `bearer = HTTPBearer(auto_error=False)`, depender dele com `creds: HTTPAuthorizationCredentials | None = Depends(bearer)` e levantar `HTTPException(status_code=401, detail="...", headers={"WWW-Authenticate": "Bearer"})` quando faltar ou for inválido. Esquema errado (Basic) também deve resultar em 401. Não declare `Authorization: str = Header(...)` como obrigatório: header ausente vira 422, não 401.

## FastAPI: validação de query com 422
`page: int = Query(1, ge=1)` e `page_size: int = Query(10, ge=1, le=50)` fazem o FastAPI devolver 422 sozinho para valores fora do limite ou não numéricos; não valide na mão. Parâmetro opcional: `min: int | None = None`. `Literal["a","b"]` ou um Enum no parâmetro também gera 422 automático para valor inválido.

## FastAPI: status 204 e respostas
Para DELETE sem corpo: `@app.delete(..., status_code=204)` e `return Response(status_code=204)` (ou retornar None). Não devolva JSON com 204. Criação usa `status_code=201`. Use `response_model` com um schema de saída para nunca vazar campos como o hash da senha.

## FastAPI: dependências e erros
`Depends(get_db)` com generator (`yield` e `finally: db.close()`) para sessão por requisição. Erros de regra de negócio: `raise HTTPException(status_code=404|403|409, detail=...)`. Ordem usual: 404 se o recurso não existe, depois 403 se o usuário não tem permissão.

## FastAPI: testar
`from fastapi.testclient import TestClient`; `client = TestClient(app)`; `client.get(url, headers={"Authorization": "Bearer ..."})`. Em geral a variável da aplicação se chama `app` e fica no módulo pedido.
