# src/ingest.py
from datetime import datetime
from hashlib import sha1
from tempfile import NamedTemporaryFile
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

from src.helper import process_documents
from src.pinecone_vectorstore import get_vectorstore


def _hash_bytes(data: bytes) -> str:
    return sha1(data).hexdigest()[:12]


def _upsert_chunks(chunks: List[Document], doc_id: str, filename: str) -> dict:
    vs = get_vectorstore()
    try:
        vs.delete(filter={"doc_id": doc_id})
    except Exception as e:
        if "namespace not found" not in str(e).lower():
            pass 

    ids = []
    for i, ch in enumerate(chunks):
        page = ch.metadata.get("page", 0)
        ch.metadata.update({
            "doc_id": doc_id,
            "source": filename,
            "ingested_at": datetime.utcnow().isoformat(),
            "chunk_index": i,
        })
        ids.append(f"{doc_id}:{page}:{i}")

    vs.add_documents(chunks, ids=ids)
    return {"doc_id": doc_id, "chunks": len(chunks)}


def ingest_pdf_bytes(file_bytes: bytes, filename: str) -> dict:
    """Ingest a single PDF given as bytes."""
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    raw_docs = loader.load()
    for d in raw_docs:
        d.metadata.update({"source": filename})

    chunks = process_documents(raw_docs)
    doc_id = _hash_bytes(file_bytes)
    return _upsert_chunks(chunks, doc_id, filename)


def ingest_folder(folder: str = "Docs/") -> dict:
    """Re-index all PDFs in a folder."""
    from pathlib import Path
    p = Path(folder)
    if not p.exists():
        return {"error": f"Folder not found: {folder}"}

    total = 0
    indexed = 0
    for pdf in p.glob("*.pdf"):
        total += 1
        data = pdf.read_bytes()
        try:
            ingest_pdf_bytes(data, pdf.name)
            indexed += 1
        except Exception as e:
            print(f"[ingest_folder] Failed on {pdf.name}: {e}")

    return {"files": total, "indexed": indexed}
