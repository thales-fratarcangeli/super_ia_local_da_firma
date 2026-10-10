from solution import Base, User, Project, Task, make_session

def test_relationships_and_cascade():
    s = make_session()
    u = User(name="ana")
    p = Project(name="p", owner=u)
    p.tasks.append(Task(title="t1"))
    p.tasks.append(Task(title="t2"))
    s.add(u)
    s.commit()
    assert u.projects[0].name == "p"
    assert p.owner_id == u.id
    assert all(t.project is p for t in p.tasks)
    s.delete(p)
    s.commit()
    assert s.query(Task).count() == 0
    assert s.query(User).count() == 1

def test_tables():
    assert {"users", "projects", "tasks"} <= set(Base.metadata.tables)
