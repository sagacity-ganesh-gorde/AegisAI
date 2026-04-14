from notion_client import Client
from .base import Document
from typing import Optional

class NotionConnector:
    def __init__(self, token: str):
        self.client = Client(auth=token)
    
    def fetch_database(self, database_id: str, filter_props: Optional[dict] = None) -> list[Document]:
        docs = []
        query = {"database_id": database_id}
        if filter_props:
            query["filter"] = filter_props
        
        results = self.client.databases.query(**query)
        for page in results.get("results", []):
            docs.extend(self._page_to_documents(page))
        
        while results.get("has_more"):
            results = self.client.databases.query(
                **query,
                start_cursor=results.get("next_cursor")
            )
            for page in results.get("results", []):
                docs.extend(self._page_to_documents(page))
        
        return docs
    
    def fetch_page(self, page_id: str) -> list[Document]:
        page = self.client.pages.retrieve(page_id)
        return self._page_to_documents(page)
    
    def _page_to_documents(self, page: dict) -> list[Document]:
        page_id = page["id"]
        title = self._extract_title(page)
        
        try:
            blocks = self.client.blocks.children.list(page_id)
            text = self._extract_blocks_text(blocks.get("results", []))
        except Exception:
            text = ""
        
        if not text.strip():
            return []
        
        return [Document(
            text=text,
            source=f"notion://{page_id}",
            title=title,
            source_type="notion"
        )]
    
    def _extract_title(self, page: dict) -> str:
        props = page.get("properties", {})
        for prop_name, prop_value in props.items():
            if prop_value.get("type") == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "Untitled")
        return "Untitled"
    
    def _extract_blocks_text(self, blocks: list[dict]) -> str:
        texts = []
        for block in blocks:
            block_type = block.get("type", "")
            if block_type in ("paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "quote"):
                content = block.get(block_type, {})
                rich_text = content.get("rich_text", [])
                block_text = " ".join(t.get("plain_text", "") for t in rich_text)
                if block_text:
                    texts.append(block_text)
        return "\n".join(texts)
