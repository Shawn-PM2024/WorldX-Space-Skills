#!/usr/bin/env python3
import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def slide_number(name: str) -> int:
    return int(re.search(r"slide(\d+)\.xml$", name).group(1))


def text_runs(root):
    return [node.text for node in root.findall(".//a:t", NS) if node.text]


def audit_pptx(pptx: Path):
    with zipfile.ZipFile(pptx) as zf:
        pres = ET.fromstring(zf.read("ppt/presentation.xml"))
        size_node = pres.find("p:sldSz", NS)
        size = dict(size_node.attrib) if size_node is not None else {}
        slides = sorted(
            [name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=slide_number,
        )
        media = [name for name in zf.namelist() if re.match(r"ppt/media/.+", name)]

        colors = Counter()
        fonts = Counter()
        font_sizes = Counter()
        shapes = Counter()
        slide_summaries = []

        for slide_name in slides:
            root = ET.fromstring(zf.read(slide_name))
            texts = text_runs(root)
            slide_colors = Counter()
            slide_shapes = Counter()
            for node in root.findall(".//a:srgbClr", NS):
                value = node.attrib.get("val")
                if value:
                    colors[value] += 1
                    slide_colors[value] += 1
            for node in root.findall(".//a:latin", NS):
                value = node.attrib.get("typeface")
                if value:
                    fonts[value] += 1
            for node in root.findall(".//a:rPr", NS):
                value = node.attrib.get("sz")
                if value:
                    font_sizes[str(int(value) // 100)] += 1
            for node in root.findall(".//a:prstGeom", NS):
                value = node.attrib.get("prst")
                if value:
                    shapes[value] += 1
                    slide_shapes[value] += 1
            slide_summaries.append(
                {
                    "slide": slide_number(slide_name),
                    "text_count": len(texts),
                    "text_preview": " | ".join(texts)[:700],
                    "top_colors": slide_colors.most_common(10),
                    "top_shapes": slide_shapes.most_common(10),
                }
            )

    return {
        "file": str(pptx),
        "slide_size_emu": size,
        "slide_count": len(slides),
        "media_count": len(media),
        "top_colors": colors.most_common(24),
        "top_fonts": fonts.most_common(12),
        "top_font_sizes_pt": font_sizes.most_common(16),
        "top_shapes": shapes.most_common(16),
        "slides": slide_summaries,
    }


def write_markdown(audit, out_path: Path):
    lines = [
        "# User Template Audit",
        "",
        f"- File: `{audit['file']}`",
        f"- Slides: {audit['slide_count']}",
        f"- Slide size EMU: `{audit['slide_size_emu']}`",
        f"- Media assets: {audit['media_count']}",
        "",
        "## Top Visual Tokens",
        "",
        f"- Colors: {', '.join(f'{k} ({v})' for k, v in audit['top_colors'][:12])}",
        f"- Fonts: {', '.join(f'{k} ({v})' for k, v in audit['top_fonts'][:8])}",
        f"- Font sizes pt: {', '.join(f'{k} ({v})' for k, v in audit['top_font_sizes_pt'][:10])}",
        f"- Shapes: {', '.join(f'{k} ({v})' for k, v in audit['top_shapes'][:10])}",
        "",
        "## Slide Text And Shape Samples",
        "",
    ]
    for slide in audit["slides"]:
        lines.extend(
            [
                f"### Slide {slide['slide']}",
                "",
                f"- Text count: {slide['text_count']}",
                f"- Top colors: {slide['top_colors']}",
                f"- Top shapes: {slide['top_shapes']}",
                f"- Text preview: {slide['text_preview']}",
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Audit PPTX template style tokens for practical-ppt user-template mode.")
    parser.add_argument("pptx")
    parser.add_argument("--out", default="template-audit")
    args = parser.parse_args()

    pptx = Path(args.pptx).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    audit = audit_pptx(pptx)
    (out_dir / "template-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(audit, out_dir / "template-audit.md")
    print(json.dumps({"json": str(out_dir / "template-audit.json"), "markdown": str(out_dir / "template-audit.md")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
