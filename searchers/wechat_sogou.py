"""微信公众号文章搜索（Playwright 无头浏览器，持久化 cookie）"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from config import MAX_ARTICLES_PER_SOURCE, REQUEST_DELAY

# 持久化浏览器 context 目录（保存 cookie/localStorage，减少验证触发）
_CONTEXT_DIR = str(Path(__file__).parent.parent / "data" / "wechat_browser")


def search(company: str) -> list[dict]:
    with sync_playwright() as p:
        # launch_persistent_context 自动保存并复用 cookie
        context = p.chromium.launch_persistent_context(
            user_data_dir=_CONTEXT_DIR,
            headless=True,
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.new_page()

        try:
            url = (
                f"https://weixin.sogou.com/weixin"
                f"?type=2&query={company}&page=1&ie=utf8"
            )
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            time.sleep(2)  # 等待 JS 渲染完毕

            # 检测验证码拦截页面
            if "antispider" in page.url or "验证码" in page.inner_text("body")[:200]:
                print("  [微信] ⚠️ 需要验证码，请先运行：python setup_wechat.py")
                return []

            # 提取文章列表
            items = page.query_selector_all("ul.news-list li")
            if not items:
                # 页面可能为空或被拦截
                return []

            results = []
            for item in items[:MAX_ARTICLES_PER_SOURCE]:
                try:
                    title_el = item.query_selector("h3 a")
                    if not title_el:
                        continue
                    title = title_el.inner_text().strip()
                    link  = title_el.get_attribute("href") or ""
                    if link.startswith("/"):
                        link = "https://weixin.sogou.com" + link

                    snippet_el = item.query_selector("p.txt-info")
                    snippet = snippet_el.inner_text().strip() if snippet_el else ""

                    time_el = item.query_selector("date, span.s2")
                    pub_time = time_el.inner_text().strip() if time_el else ""

                    account_el = item.query_selector(".account")
                    account = account_el.inner_text().strip() if account_el else ""
                    source = f"微信·{account}" if account else "微信公众号"

                    if title and link:
                        results.append({
                            "title"       : title,
                            "url"         : link,
                            "snippet"     : snippet,
                            "published_at": pub_time,
                            "source"      : source,
                        })
                except Exception:
                    continue

            time.sleep(REQUEST_DELAY)
            return results

        except PWTimeout:
            print("  [微信] 超时，跳过")
            return []
        except Exception as e:
            print(f"  [微信] 错误: {e}")
            return []
        finally:
            context.close()
