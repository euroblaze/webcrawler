from pydantic import BaseModel, HttpUrl
from typing import Optional

class CrawlRequest(BaseModel):
    url: HttpUrl
    crawl_depth: Optional[int] = None
    crawl_timeout: Optional[int] = None

class CrawlResponse(BaseModel):
    crawl_id: str
    status: str

class StatusResponse(BaseModel):
    crawl_id: str
    status: str
    file_path: Optional[str] = None
