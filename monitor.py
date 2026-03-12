#!/usr/bin/env python3
"""
被投企业新闻监控 — 主入口
用法：python monitor.py
"""
import sys
import yaml

from database.db      import init_db, is_seen, save_article
from searchers        import baidu_news, wechat_sogou, bing_news
from searchers.filter import is_tutorial
from summarizer.kimi  import summarize
from reporter.markdown import generate


def load_companies(path="companies.yaml") -> list[str]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("companies", [])


def search_company(company: str) -> list[dict]:
    """聚合三个来源的搜索结果"""
    print(f"  百度新闻...", end=" ", flush=True)
    r1 = baidu_news.search(company)
    print(f"{len(r1)} 条")

    print(f"  微信公众号...", end=" ", flush=True)
    r2 = wechat_sogou.search(company)
    print(f"{len(r2)} 条")

    print(f"  Bing News...", end=" ", flush=True)
    r3 = bing_news.search(company)
    print(f"{len(r3)} 条")

    return r1 + r2 + r3


def main():
    print("=" * 50)
    print("  被投企业新闻监控")
    print("=" * 50)

    # 初始化数据库
    init_db()

    companies = load_companies()
    if not companies:
        print("companies.yaml 里没有企业，请先添加。")
        sys.exit(1)

    print(f"\n共监控 {len(companies)} 家企业：{', '.join(companies)}\n")

    report_data = {}  # { company: [new_articles] }

    for company in companies:
        print(f"▶ [{company}]")
        articles = search_company(company)
        # 过滤教程类文章
        before = len(articles)
        articles = [a for a in articles if not is_tutorial(a)]
        filtered = before - len(articles)
        print(f"  共获取 {before} 条，过滤教程 {filtered} 条，剩余 {len(articles)} 条，开始去重和摘要...")

        new_articles = []
        for art in articles:
            url = art.get("url", "").strip()
            if not url:
                continue
            if is_seen(url):
                continue  # 已在数据库，跳过

            # 调用 Kimi 生成摘要
            print(f"    摘要中：{art['title'][:30]}...")
            summary = summarize(art["title"], art.get("snippet", ""), company)
            art["summary"] = summary

            # 写入数据库
            save_article(
                company    = company,
                title      = art["title"],
                url        = url,
                source     = art.get("source", ""),
                snippet    = art.get("snippet", ""),
                summary    = summary,
                published_at = art.get("published_at", ""),
            )
            new_articles.append(art)

        print(f"  ✅ 新增 {len(new_articles)} 条（去重后）\n")
        report_data[company] = new_articles

    # 生成 Markdown 报告
    total_new = sum(len(v) for v in report_data.values())
    if total_new == 0:
        print("本次没有新文章，无需生成报告。")
        return

    filepath = generate(report_data)
    print(f"📄 报告已生成：{filepath}")


if __name__ == "__main__":
    main()
