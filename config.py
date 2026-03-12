import os
from dotenv import load_dotenv

load_dotenv()

KIMI_API_KEY = os.getenv("KIMI_API_KEY")
KIMI_MODEL   = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
KIMI_BASE_URL = "https://api.moonshot.cn/v1"

DB_PATH     = os.path.join(os.path.dirname(__file__), "data", "news.db")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")

# 每个企业每个来源最多抓取的文章数
MAX_ARTICLES_PER_SOURCE = 5

# 请求间隔（秒），避免被封
REQUEST_DELAY = 1.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}
