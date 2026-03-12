"""生成 Markdown 报告"""
import os
from datetime import datetime
from config import OUTPUT_DIR


def generate(results: dict[str, list[dict]]) -> str:
    """
    results: { company: [article, ...], ... }
    article: {title, url, source, snippet, summary, published_at}

    返回生成的文件路径
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now      = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M") + "_report.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    total = sum(len(v) for v in results.values())

    lines = [
        "# 被投企业新闻监控报告",
        f"",
        f"> 生成时间：{now.strftime('%Y-%m-%d %H:%M')}　　本次新增：**{total} 条**",
        "",
        "---",
        "",
    ]

    for company, articles in results.items():
        if not articles:
            continue

        lines.append(f"## {company}（{len(articles)} 条新闻）")
        lines.append("")

        for art in articles:
            title       = art.get("title", "（无标题）")
            url         = art.get("url", "")
            source      = art.get("source", "")
            pub_time    = art.get("published_at", "")
            summary     = art.get("summary") or art.get("snippet", "")

            # 标题行
            if url:
                lines.append(f"### [{title}]({url})")
            else:
                lines.append(f"### {title}")

            # 元信息
            meta_parts = []
            if source:   meta_parts.append(f"来源：{source}")
            if pub_time: meta_parts.append(f"时间：{pub_time}")
            if meta_parts:
                lines.append("- " + "　｜　".join(meta_parts))

            # 摘要
            if summary:
                lines.append(f"- **摘要**：{summary}")

            lines.append("")

        lines.append("---")
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
