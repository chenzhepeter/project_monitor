#!/usr/bin/env python3
"""
一次性微信搜索授权工具
────────────────────────
运行此脚本会打开一个真实的 Chrome 浏览器窗口。
请在浏览器里手动完成搜狗验证码，完成后按回车，
之后 monitor.py 可以在无头模式下复用 cookie。

用法：python setup_wechat.py
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CONTEXT_DIR = str(Path(__file__).parent / "data" / "wechat_browser")
TEST_URL = "https://weixin.sogou.com/weixin?type=2&query=字节跳动&page=1&ie=utf8"


def main():
    print("=" * 55)
    print("  微信搜索一次性授权工具")
    print("=" * 55)
    print("\n即将打开浏览器窗口，请：")
    print("  1. 等待页面加载")
    print("  2. 若出现验证码，请手动完成")
    print("  3. 看到搜索结果后，回到此终端按 Enter")
    print("\n按 Enter 开始...")
    input()

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=CONTEXT_DIR,
            headless=False,          # 可见窗口，方便手动操作
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.new_page()
        page.goto(TEST_URL, wait_until="domcontentloaded")

        print("\n浏览器已打开，请在浏览器里完成验证。")
        print("看到搜索结果后，回到此终端按 Enter 保存 cookie 并关闭...")
        input()

        # 验证是否已有结果
        items = page.query_selector_all("ul.news-list li")
        if items:
            print(f"\n✅ 成功！找到 {len(items)} 条微信文章，cookie 已保存。")
            print("   之后运行 python monitor.py 即可自动使用微信搜索。")
        else:
            print("\n⚠️  未检测到搜索结果，可能验证未完成。")
            print("   你仍可关闭并重试，或跳过微信搜索直接用百度新闻。")

        ctx.close()


if __name__ == "__main__":
    main()
