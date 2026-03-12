"""微信公众号文章搜索（通过搜狗微信，带 session cookie 重试）"""
import re
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY


def search(company: str) -> list[dict]:
    session = requests.Session()
    session.headers.update(HEADERS)

    # 先访问首页获取 cookie
    try:
        session.get("https://weixin.sogou.com/", timeout=8)
    except Exception:
        pass

    url = "https://weixin.sogou.com/weixin"
    params = {"type": "2", "query": company, "page": 1, "ie": "utf8"}

    try:
        resp = session.get(url, params=params, timeout=10)
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  [微信搜狗] 请求失败: {e}")
        return []

    # 被拦截（返回验证页）时直接跳过
    if len(resp.text) < 8000 or "验证" in resp.text[:500]:
        print("  [微信搜狗] 触发验证，跳过")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for item in soup.select("ul.news-list li")[:MAX_ARTICLES_PER_SOURCE]:
        try:
            title_el = item.select_one("h3 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link  = title_el.get("href", "")
            if link.startswith("/"):
                link = "https://weixin.sogou.com" + link

            snippet_el = item.select_one("p.txt-info")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            time_el = item.select_one("date, span.s2")
            pub_time = time_el.get_text(strip=True) if time_el else ""

            account_el = item.select_one(".account")
            account = account_el.get_text(strip=True) if account_el else ""
            source  = f"微信·{account}" if account else "微信公众号"

            if not title or not link:
                continue

            results.append({
                "title": title, "url": link, "snippet": snippet,
                "published_at": pub_time, "source": source,
            })
        except Exception:
            continue

    time.sleep(REQUEST_DELAY)
    return results
