import fitz
from pathlib import Path
from .base import Document

class PDFConnector:
    def fetch_local(self, path: str) -> list[Document]:
        docs = []
        try:
            with fitz.open(path) as pdf:
                for i, page in enumerate(pdf):
                    text = page.get_text()
                    if text.strip():
                        filename = Path(path).stem
                        docs.append(Document(
                            text=text,
                            source=f"pdf://{path}",
                            title=filename,
                            page=i + 1,
                            source_type="pdf"
                        ))
        except Exception as e:
            raise ValueError(f"Failed to read PDF {path}: {e}")
        return docs
    
    def fetch_multiple(self, paths: list[str]) -> list[Document]:
        docs = []
        for path in paths:
            docs.extend(self.fetch_local(path))
        return docs
