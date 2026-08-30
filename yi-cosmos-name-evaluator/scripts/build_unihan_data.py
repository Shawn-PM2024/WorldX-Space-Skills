#!/usr/bin/env python3
"""Build the compact, deterministic Unihan runtime dataset."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

DEFAULT_VERSION = "17.0.0"
DEFAULT_URL = "https://www.unicode.org/Public/17.0.0/ucd/Unihan.zip"
VARIANT_PATTERN = re.compile(r"U\+([0-9A-F]{4,6})")


def read_source(source: str) -> tuple[bytes, str]:
    candidate = Path(source)
    if candidate.exists():
        return candidate.read_bytes(), str(candidate.resolve())
    with urllib.request.urlopen(source, timeout=60) as response:
        return response.read(), source


def parse_unihan(archive: bytes) -> dict[str, dict]:
    records: dict[str, dict] = defaultdict(dict)
    properties = {
        "kTotalStrokes",
        "kTraditionalVariant",
        "kSimplifiedVariant",
        "kDefinition",
        "kMandarin",
    }

    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for member in sorted(bundle.namelist()):
            if not member.endswith(".txt"):
                continue
            with bundle.open(member) as stream:
                for raw_line in stream:
                    if raw_line.startswith(b"#") or raw_line.strip() == b"":
                        continue
                    line = raw_line.decode("utf-8").rstrip("\n")
                    try:
                        codepoint, prop, value = line.split("\t", 2)
                    except ValueError:
                        continue
                    if prop not in properties:
                        continue
                    character = chr(int(codepoint, 0))
                    record = records[character]
                    if prop == "kTotalStrokes":
                        record["strokes"] = sorted(
                            {int(token) for token in value.split()}
                        )
                    elif prop == "kTraditionalVariant":
                        record["traditional"] = sorted(
                            {
                                chr(int(match, 16))
                                for match in VARIANT_PATTERN.findall(value)
                            },
                            key=ord,
                        )
                    elif prop == "kSimplifiedVariant":
                        record["simplified"] = sorted(
                            {
                                chr(int(match, 16))
                                for match in VARIANT_PATTERN.findall(value)
                            },
                            key=ord,
                        )
                    elif prop == "kDefinition":
                        record["definition"] = value
                    elif prop == "kMandarin":
                        record["mandarin"] = value

    return {character: records[character] for character in sorted(records, key=ord)}


def write_dataset(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    with (
        output_path.open("wb") as raw_output,
        gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_output, mtime=0
        ) as compressed,
    ):
        compressed.write(encoded)


def main() -> int:
    script_root = Path(__file__).resolve().parents[1]
    default_output = script_root / "references" / "data" / "unihan-17.0.0.json.gz"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_URL, help="Unihan.zip path or URL")
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--output", type=Path, default=default_output)
    args = parser.parse_args()

    archive, _source_label = read_source(args.source)
    characters = parse_unihan(archive)
    payload = {
        "metadata": {
            "unicode_version": args.version,
            "source": DEFAULT_URL,
            "source_sha256": hashlib.sha256(archive).hexdigest(),
            "character_count": len(characters),
            "properties": [
                "kDefinition",
                "kMandarin",
                "kSimplifiedVariant",
                "kTotalStrokes",
                "kTraditionalVariant",
            ],
        },
        "characters": characters,
    }
    write_dataset(payload, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "character_count": len(characters),
                "source_sha256": payload["metadata"]["source_sha256"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
