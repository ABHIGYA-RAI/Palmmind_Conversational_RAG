from app.services.chunking import chunk_text

def test_short_text_is_one_chunk() -> None:
    assert chunk_text("hello world") == ["hello world"]


def test_empty_text_gives_no_chunks() -> None:
    assert chunk_text("   ") == []


def test_chunks_respect_size_and_overlap() -> None:
    text = "a" * 2000
    chunks = chunk_text(text, size=800, overlap=150)
    assert all(len(c) <= 800 for c in chunks)
    assert chunks[0][-150:] == chunks[1][:150]