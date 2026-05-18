"""文档正文清洗（水印与噪声），供 RAG 与知识库解析共用。"""
import re


def clean_text(text: str) -> str:
    if not text:
        return text

    watermark_keywords = [
        "机密",
        "保密",
        "内部资料",
        "内部使用",
        "草稿",
        "Draft",
        "COPY",
        "副本",
        "Confidential",
        "Private",
        "Internal",
        "仅供参考",
        "请勿外传",
        "版权所有",
        "©",
        "®",
    ]

    cleaned_text = text
    for keyword in watermark_keywords:
        cleaned_text = cleaned_text.replace(keyword, "")

    lines = cleaned_text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 2:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"(.)\1{3,}", r"\1", cleaned_text)
    return cleaned_text
