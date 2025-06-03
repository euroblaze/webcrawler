import logging
import bleach
from pathlib import Path
import os
from crawl4ai import crawl_url

DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
LOG_FILE = DATA_DIR / "crawl4ai.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

COUNTER_FILE = DATA_DIR / "crawl_id.counter"
if not COUNTER_FILE.exists():
    COUNTER_FILE.write_text("0")

def generate_crawl_id() -> str:
    try:
        current = int(COUNTER_FILE.read_text()) + 1
        COUNTER_FILE.write_text(str(current))
        return f"{current:06d}"
    except Exception as e:
        logging.error(f"Failed to generate crawl ID: {e}")
        raise

def save_markdown(crawl_id: str, content: str):
    file_path = DATA_DIR / f"{crawl_id}.md"
    try:
        file_path.write_text(content)
    except Exception as e:
        logging.error(f"Failed to save file {file_path}: {e}")
        raise
    return file_path

def crawl_and_store(url: str, crawl_id: str, crawl_depth: int = None, crawl_timeout: int = None):
    import configparser
    import time
    config = configparser.ConfigParser()
    config.read(DATA_DIR / "../crawl.config")
    default_depth = int(config.get("settings", "crawl_depth", fallback="2"))
    default_timeout = int(config.get("settings", "crawl_timeout", fallback="10"))

    depth = crawl_depth if crawl_depth is not None else default_depth
    timeout = crawl_timeout if crawl_timeout is not None else default_timeout

    start_time = time.time()
    try:
        raw_content = crawl_url(url, return_format="markdown", max_depth=depth, timeout=timeout)
    except Exception as e:
        logging.error(f"Crawl failed for {crawl_id} with error: {e}")
        raise
    duration = time.time() - start_time
    logging.info(f"Crawl completed for {crawl_id} in {duration:.2f} seconds with timeout={timeout}s")

    sanitized_content = bleach.clean(
        raw_content,
        tags=["p", "a", "ul", "li", "strong", "em", "code"],
        attributes={"a": ["href"]},
        strip=True
    )
    return save_markdown(crawl_id, sanitized_content)
