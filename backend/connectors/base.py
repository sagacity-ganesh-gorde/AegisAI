from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class Document:
    text: str
    source: str
    title: Optional[str] = None
    page: Optional[int] = None
    source_type: Optional[str] = None

def chunk_documents(documents: list[Document], chunk_size: int = 500, overlap: int = 50) -> tuple[list[str], list[str]]:
    all_chunks = []
    all_sources = []
    
    for doc in documents:
        text = doc.text.strip()
        if not text:
            continue
        
        tokens = text.split()
        if len(tokens) <= chunk_size:
            all_chunks.append(text)
            all_sources.append(doc.source)
            continue
        
        for i in range(0, len(tokens) - chunk_size + 1, chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            all_chunks.append(" ".join(chunk_tokens))
            source_info = f"{doc.source}"
            if doc.page is not None:
                source_info += f" (page {doc.page})"
            if doc.title:
                source_info = f"{doc.title} — {source_info}"
            all_sources.append(source_info)
    
    return all_chunks, all_sources
