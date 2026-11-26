import io

from fastapi import APIRouter, HTTPException, UploadFile
from pypdf import PdfReader

from app.models.schemas import IngestResponse
from app.repositories.vector_store import vector_store
from app.services.chunking import chunk_text
from app.services.embeddings import embedder

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    name = file.filename or "unknown"
    data = await file.read()
    if name.lower().endswith(".pdf"):
        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    elif name.lower().endswith((".txt", ".md")):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, "Only .pdf, .txt, .md supported")
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(400, "No text extracted")
    vectors = await embedder.embed(chunks)
    await vector_store.add(name, chunks, vectors)
    return IngestResponse(filename=name, chunks=len(chunks))