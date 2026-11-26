def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks