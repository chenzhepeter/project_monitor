"""过滤教程、使用指南等非新闻类文章"""

# 教程类关键词（出现在标题中即判定为教程）
_TUTORIAL_KEYWORDS = [
    "怎么", "如何", "怎样", "教程", "入门", "使用方法", "使用指南",
    "操作指南", "操作步骤", "安装方法", "安装教程", "注册方法",
    "下载方法", "下载教程", "设置方法", "配置方法", "快速上手",
    "新手教程", "零基础", "步骤", "攻略", "技巧",
    "how to", "tutorial", "guide", "setup", "install",
]

# 教程类来源域名（这些站点主要发布 how-to 内容）
_TUTORIAL_DOMAINS = [
    "pconline.com.cn",   # 太平洋科技的 /x/ 路径多为教程
    "zol.com.cn",
    "jb51.net",
    "php.cn",
    "cnblogs.com",
]


def is_tutorial(article: dict) -> bool:
    """返回 True 表示是教程/指南，应被过滤掉"""
    title = article.get("title", "").lower()
    url   = article.get("url", "").lower()

    for kw in _TUTORIAL_KEYWORDS:
        if kw in title:
            return True

    for domain in _TUTORIAL_DOMAINS:
        if domain in url and "/x/" in url:   # 太平洋科技 /x/ 路径全是教程
            return True

    return False
