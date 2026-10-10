from solution import Base, Post, Tag, make_session, tag_post

def test_many_to_many_both_sides():
    s = make_session()
    p1, p2 = Post(title="a"), Post(title="b")
    s.add_all([p1, p2]); s.commit()
    tag_post(s, p1, ["python", "sql"])
    tag_post(s, p2, ["python"])
    s.commit()
    assert sorted(t.name for t in p1.tags) == ["python", "sql"]
    py = s.query(Tag).filter_by(name="python").one()
    assert sorted(p.title for p in py.posts) == ["a", "b"]

def test_reuse_and_no_duplicate_association():
    s = make_session()
    p = Post(title="x"); s.add(p); s.commit()
    tag_post(s, p, ["a", "a", "b"])
    tag_post(s, p, ["a"])
    s.commit()
    assert s.query(Tag).count() == 2
    assert sorted(t.name for t in p.tags) == ["a", "b"]

def test_table_exists():
    assert "post_tags" in Base.metadata.tables
