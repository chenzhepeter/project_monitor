"""Bing News 搜索结果抓取（HTML 页面）"""
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY


def search(company: str) -> list[dict]:
    url = "https://www.bing.com/news/search"
    params = {"q": company, "mkt": "zh-CN", "setlang": "zh-CN", "cc": "CN"}
    headers = {**HEADERS, "Accept-Language": "zh-CN,zh;q=0.9"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  [Bing News] 请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for item in soup.select("div.news-card, article.news-card, div[class*='newsitem']")[:MAX_ARTICLES_PER_SOURCE]:
        try:
            title_el = item.select_one("a.title, a[class*='title'], h2 a, h3 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link  = title_el.get("href", "")

            snippet_el = item.select_one("div.snippet, p, div[class*='snippet']")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            time_el = item.select_one("span[aria-label], div.source span, time")
            pub_time = ""
            if time_el:
                pub_time = time_el.get("aria-label") or time_el.get_text(strip=True)

            source_el = item.select_one("div.source a, span.source, div[class*='provider'] a")
            source = source_el.get_text(strip=True) if source_el else "Bing News"

            if not title or not link:
                continue

            results.append({
                "title": title, "url": link, "snippet": snippet,
                "published_at": pub_time,
                "source": f"Bing·{source}" if source != "Bing News" else "Bing News",
            })
        except Exception:
            continue

    time.sleep(REQUEST_DELAY)
    return results
