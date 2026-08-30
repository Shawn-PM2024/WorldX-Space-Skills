#!/usr/bin/env python3
"""Prepare or score an explainable commercial-name evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from yi_cosmos_evaluator import (
    ValidationError,
    prepare_evaluation,
    render_markdown,
    score_evaluation,
)


def read_json(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_output(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser(
        "prepare",
        help="validate a request and emit mechanical facts plus judgment slots",
    )
    prepare_parser.add_argument(
        "--input",
        required=True,
        help="request JSON path, or - for stdin",
    )
    prepare_parser.add_argument("--output", help="output path; defaults to stdout")

    score_parser = subparsers.add_parser(
        "score",
        help="validate completed judgments and produce the final result",
    )
    score_parser.add_argument(
        "--input",
        required=True,
        help="completed prepared JSON path, or - for stdin",
    )
    score_parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
    )
    score_parser.add_argument("--output", help="output path; defaults to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = read_json(args.input)
        if args.command == "prepare":
            result = prepare_evaluation(payload)
            content = json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
            )
        else:
            result = score_evaluation(payload)
            if args.format == "json":
                content = json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=False,
                )
            else:
                content = render_markdown(result)
        write_output(content, args.output)
        return 0
    except (OSError, json.JSONDecodeError, ValidationError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
