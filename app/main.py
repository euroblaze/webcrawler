from fastapi import FastAPI, HTTPException, BackgroundTasks
from .models import CrawlRequest, CrawlResponse, StatusResponse
from .utils import generate_crawl_id, crawl_and_store, DATA_DIR
from .db import set_status, get_status
from pathlib import Path

app = FastAPI()

@app.post("/crawl", response_model=CrawlResponse)
def trigger_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    crawl_id = generate_crawl_id()
    set_status(crawl_id, "in_progress")

    def background_job():
        try:
            crawl_and_store(request.url, crawl_id, request.crawl_depth, request.crawl_timeout)
            set_status(crawl_id, "completed")
        except Exception:
            set_status(crawl_id, "failed")

    background_tasks.add_task(background_job)
    return {"crawl_id": crawl_id, "status": "in_progress"}

@app.get("/status/{crawl_id}", response_model=StatusResponse)
def get_status_api(crawl_id: str):
    status = get_status(crawl_id)
    if not status:
        raise HTTPException(status_code=404, detail="Crawl ID not found")

    file_path = str(DATA_DIR / f"{crawl_id}.md") if status == "completed" else None
    return {"crawl_id": crawl_id, "status": status, "file_path": file_path}

@app.get("/result/{crawl_id}")
def get_result(crawl_id: str):
    file_path = DATA_DIR / f"{crawl_id}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Result not available")
    return file_path.read_text()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/list")
def list_results():
    return [f.name for f in DATA_DIR.glob("*.md")]
