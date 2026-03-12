"""使用 Kimi API 生成新闻摘要（OpenAI 兼容接口）"""
from openai import OpenAI
from config import KIMI_API_KEY, KIMI_MODEL, KIMI_BASE_URL

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=KIMI_API_KEY, base_url=KIMI_BASE_URL)
    return _client


def summarize(title: str, snippet: str, company: str) -> str:
    """
    调用 Kimi API，生成 80~120 字的中文摘要。
    失败时返回原始 snippet（不影响主流程）。
    """
    if not KIMI_API_KEY:
        return snippet

    content = f"标题：{title}\n内容摘要：{snippet}"
    prompt = (
        f"以下是关于企业「{company}」的一篇新闻，请用 80~120 字的中文给出简洁客观的摘要，"
        f"重点说明事件背景、核心内容和潜在影响，不要有多余的评论或开场白。\n\n{content}"
    )

    try:
        resp = _get_client().chat.completions.create(
            model=KIMI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [Kimi] 摘要生成失败: {e}")
        return snippet
