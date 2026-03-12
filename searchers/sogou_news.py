"""搜狗新闻抓取"""
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY


def search(company: str) -> list[dict]:
    """
    搜索搜狗新闻，返回文章列表
    每项：{title, url, snippet, published_at, source}
    """
    url = "https://www.sogou.com/news"
    params = {"query": company, "page": 1}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  [搜狗新闻] 请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for item in soup.select(".news-list li, .vrwrap")[:MAX_ARTICLES_PER_SOURCE]:
        try:
            title_el = item.select_one("h3 a, .vr-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link  = title_el.get("href", "")
            if not link or not title:
                continue

            snippet_el = item.select_one(".news-summary, .vr-summary, p")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            time_el = item.select_one(".news-from span, .vr-meta span, .fz-mini")
            pub_time = time_el.get_text(strip=True) if time_el else ""

            results.append({
                "title"       : title,
                "url"         : link,
                "snippet"     : snippet,
                "published_at": pub_time,
                "source"      : "搜狗新闻",
            })
        except Exception:
            continue

    time.sleep(REQUEST_DELAY)
    return results
