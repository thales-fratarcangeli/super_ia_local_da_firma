from solution import slugify

def test_basic():
    assert slugify("Hello World") == "hello-world"

def test_accents():
    assert slugify("Ação e Coração") == "acao-e-coracao"

def test_symbols_and_edges():
    assert slugify("  --Foo!!  Bar__baz--  ") == "foo-bar-baz"

def test_empty():
    assert slugify("!!!") == ""
