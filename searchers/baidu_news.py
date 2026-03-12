"""百度新闻抓取（解析嵌入 HTML 注释中的 JSON 数据）"""
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY


def search(company: str) -> list[dict]:
    url = "https://www.baidu.com/s"
    params = {
        "tn": "news", "rtt": "1", "word": company,
        "cl": "2", "ct": "1", "ie": "utf-8",
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  [百度新闻] 请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for item in soup.select("div.result-op[tpl='news-normal'], div.result-op[tpl='news-single']"):
        if len(results) >= MAX_ARTICLES_PER_SOURCE:
            break
        try:
            # 数据藏在 <!--s-data:{...}--> HTML 注释里
            comment = item.find(string=lambda t: isinstance(t, str) and '"titleUrl"' in t)
            if comment:
                data = json.loads(re.search(r'\{.*\}', comment, re.DOTALL).group())
                title    = re.sub(r'<.*?>', '', data.get("title", "")).strip()
                link     = data.get("titleUrl", "")
                snippet  = data.get("summary", "")
                pub_time = data.get("dispTime", "")
                source   = data.get("sourceName", "百度新闻")
            else:
                # 降级：直接解析 HTML
                a = item.select_one("h3 a")
                if not a:
                    continue
                title   = a.get_text(strip=True)
                link    = a.get("href", "")
                snippet = ""
                pub_time = ""
                source  = "百度新闻"

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
