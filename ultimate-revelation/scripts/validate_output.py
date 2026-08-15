#!/usr/bin/env python3
"""Validate the default Ultimate Revelation Markdown output shape."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


INSIGHT_HEADING = re.compile(r"(?m)^###\s+\d+\.\s+\S.+$")
FIELD_MARKERS = ("- 原始内容", "- 推导链", "- 边界")
EVIDENCE_LINE = re.compile(r"^\s{2,}-\s+(.+)$")
FACT_PREFIX = re.compile(r"^F\d+\s*")
TIME_LOCATOR = re.compile(r"[（(]?\d{1,2}:\d{2}(?::\d{2})?(?:[–—-]\d{1,2}:\d{2}(?::\d{2})?)?[）)]?")
PAGE_LOCATOR = re.compile(r"[（(]?(?:第\s*)?\d+\s*(?:页|段|段落)|p\.?\s*\d+[）)]?", re.IGNORECASE)
NON_CONTENT = re.compile(r"[\s，。；：、,.!！?？'\"“”‘’「」《》【】()（）\[\]—–-]+")


def _split_insights(markdown: str) -> list[str]:
    matches = list(INSIGHT_HEADING.finditer(markdown))
    return [
        markdown[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(markdown)]
        for index, match in enumerate(matches)
    ]


def _evidence_lines(block: str) -> list[str]:
    start = block.find("- 原始内容")
    end = block.find("- 推导链", start + 1)
    if start < 0 or end < 0:
        return []
    return [match.group(1).strip() for line in block[start:end].splitlines() if (match := EVIDENCE_LINE.match(line))]


def _has_source_content(line: str) -> bool:
    content = FACT_PREFIX.sub("", line)
    content = TIME_LOCATOR.sub("", content)
    content = PAGE_LOCATOR.sub("", content)
    content = NON_CONTENT.sub("", content)
    return len(content) >= 6


def validate_markdown(markdown: str) -> list[str]:
    errors: list[str] = []
    insights = _split_insights(markdown)

    if not insights:
        return ["未找到形如 '### 1. 认知结论' 的关键认知。"]
    if len(insights) > 7:
        errors.append(f"关键认知共有 {len(insights)} 条，超过 7 条上限。")

    for index, block in enumerate(insights, start=1):
        for marker in FIELD_MARKERS:
            if marker not in block:
                errors.append(f"认知 {index} 缺少字段：{marker[2:]}。")

        evidence = _evidence_lines(block)
        if not evidence:
            errors.append(f"认知 {index} 没有可读取的原始内容条目。")
        elif any(not _has_source_content(line) for line in evidence):
            errors.append(f"认知 {index} 的原始内容包含只有定位信息、没有实际内容的条目。")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_file", type=Path)
    args = parser.parse_args()

    errors = validate_markdown(args.markdown_file.read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: Ultimate Revelation output is structurally traceable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
