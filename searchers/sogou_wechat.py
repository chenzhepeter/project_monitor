"""搜狗微信公众号文章抓取"""
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY


def search(company: str) -> list[dict]:
    """
    搜索搜狗微信，返回公众号文章列表
    每项：{title, url, snippet, published_at, source}
    """
    url = "https://weixin.sogou.com/weixin"
    params = {"type": "2", "query": company, "page": 1}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  [搜狗微信] 请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for item in soup.select(".news-box .news-list li")[:MAX_ARTICLES_PER_SOURCE]:
        try:
            title_el = item.select_one("h3 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link  = title_el.get("href", "")
            if not link or not title:
                continue
            # 补全相对链接
            if link.startswith("/"):
                link = "https://weixin.sogou.com" + link

            snippet_el = item.select_one("p.txt-info")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            time_el = item.select_one("date")
            pub_time = time_el.get_text(strip=True) if time_el else ""

            account_el = item.select_one(".account")
            account = account_el.get_text(strip=True) if account_el else ""
            source_label = f"微信公众号·{account}" if account else "微信公众号"

            results.append({
                "title"       : title,
                "url"         : link,
                "snippet"     : snippet,
                "published_at": pub_time,
                "source"      : source_label,
            })
        except Exception:
            continue

    time.sleep(REQUEST_DELAY)
    return results
