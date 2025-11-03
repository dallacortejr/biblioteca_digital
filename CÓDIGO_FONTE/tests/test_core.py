from library_manager.core import find_documents
def test_find(tmp_path):
    d = tmp_path / "docs"
    d.mkdir()
    f = d / "a.pdf"
    f.write_text("x")
    res = find_documents(str(tmp_path))
    assert any("a.pdf" in p for p in res)
