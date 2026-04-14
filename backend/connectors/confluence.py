import requests
from typing import Optional
from .base import Document
import re

class ConfluenceConnector:
    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})
    
    def fetch_space(self, space_key: str, limit: int = 100) -> list[Document]:
        docs = []
        start = 0
        
        while True:
            resp = self.session.get(
                f"{self.base_url}/rest/api/content",
                params={"spaceKey": space_key, "expand": "body.storage", "limit": limit, "start": start}
            )
            resp.raise_for_status()
            data = resp.json()
            
            for page in data.get("results", []):
                text = self._extract_text(page.get("body", {}).get("storage", {}).get("value", ""))
                if text.strip():
                    docs.append(Document(
                        text=text,
                        source=f"confluence://{page['id']}",
                        title=page.get("title", "Untitled"),
                        source_type="confluence"
                    ))
            
            if not data.get("isLastPage"):
                start += limit
            else:
                break
        
        return docs
    
    def fetch_page(self, page_id: str) -> list[Document]:
        resp = self.session.get(f"{self.base_url}/rest/api/content/{page_id}", params={"expand": "body.storage"})
        resp.raise_for_status()
        page = resp.json()
        text = self._extract_text(page.get("body", {}).get("storage", {}).get("value", ""))
        return [Document(text=text, source=f"confluence://{page_id}", title=page.get("title"), source_type="confluence")]
    
    def _extract_text(self, html_content: str) -> str:
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
