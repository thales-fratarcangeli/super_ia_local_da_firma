## SQLAlchemy 2.0: modelos
`class Base(DeclarativeBase): pass`; colunas com `id: Mapped[int] = mapped_column(primary_key=True)`; textos `Mapped[str]`; opcional `Mapped[str | None]`. Chave estrangeira: `mapped_column(ForeignKey("users.id"))`. Cada `relationship()` entre duas tabelas exige uma ForeignKey real entre elas; sem FK ocorre NoForeignKeysError e todos os mapeamentos quebram.

## SQLAlchemy: relações bidirecionais e cascade
Use `back_populates` nos dois lados: `projects: Mapped[list["Project"]] = relationship(back_populates="owner")` e `owner: Mapped["User"] = relationship(back_populates="projects")`. Para que apagar o pai com `session.delete(parent)` apague os filhos, defina no lado "um": `relationship(back_populates="project", cascade="all, delete-orphan")`. `ondelete="CASCADE"` na FK sozinho não basta para o ORM no SQLite.

## SQLAlchemy: sessão e engine
`sessionmaker(bind=engine)` devolve uma fábrica, não uma sessão: chame-a (`SessionLocal()`) ou use `Session(engine)` para obter o objeto com `.add()`, `.commit()`, `.query()`. Criar tabelas: `Base.metadata.create_all(engine)`. SQLite em memória: `create_engine("sqlite://")`; para usar de várias threads (FastAPI) passe `connect_args={"check_same_thread": False}`.

## SQLAlchemy: consultas 2.0
`session.get(Model, pk)` devolve o objeto ou None. `session.scalars(select(Model).where(Model.x == v)).all()`. Contagem: `session.scalar(select(func.count()).select_from(stmt.subquery()))`. Paginação: `.order_by(Model.id).offset((page-1)*size).limit(size)`.

## Organização para evitar import circular
Coloque `Base`, `engine`, `SessionLocal` e `get_db` em um módulo próprio (ex.: `database.py`). Os modelos importam de lá; o `main` importa modelos e database; os modelos nunca importam do `main`.
