#!/usr/bin/env python3
import argparse
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

EMU_PER_INCH = 914400


def parse_args():
    parser = argparse.ArgumentParser(description="Check PPTX text readability and layout risk.")
    parser.add_argument("pptx", help="Input .pptx file")
    parser.add_argument("--output", default="pptx-text-qa.json", help="Output JSON report")
    parser.add_argument("--min-font-pt", type=float, default=12.0, help="Minimum readable PPT font size")
    parser.add_argument("--min-line-height", type=float, default=1.0, help="Minimum line spacing multiple")
    parser.add_argument(
        "--allow-missing-line-spacing",
        action="store_true",
        help="Do not flag multi-line text boxes that lack explicit PPT line spacing",
    )
    parser.add_argument("--fail-on-review", action="store_true", help="Exit 2 when any slide needs review")
    return parser.parse_args()


def emu_to_in(value):
    return (int(value) if value else 0) / EMU_PER_INCH


def text_content(node):
    parts = []
    for paragraph in node.findall(".//a:p", NS):
        run_text = "".join(t.text or "" for t in paragraph.findall(".//a:t", NS))
        if run_text:
            parts.append(run_text)
    return "\n".join(parts).strip()


def run_font_sizes(node):
    sizes = []
    for run in node.findall(".//a:r", NS):
        text = "".join(t.text or "" for t in run.findall(".//a:t", NS)).strip()
        if not text:
            continue
        rpr = run.find("a:rPr", NS)
        size = rpr.get("sz") if rpr is not None else None
        if size and size.isdigit():
            sizes.append({"pt": int(size) / 100, "text": text[:80]})
    return sizes


def paragraph_line_spacing(node, fallback_font_pt):
    issues = []
    for paragraph in node.findall(".//a:p", NS):
        ppr = paragraph.find("a:pPr", NS)
        if ppr is None:
            continue
        ln_spc = ppr.find("a:lnSpc", NS)
        if ln_spc is None:
            continue
        pct = ln_spc.find("a:spcPct", NS)
        pts = ln_spc.find("a:spcPts", NS)
        para_text = "".join(t.text or "" for t in paragraph.findall(".//a:t", NS)).strip()
        if pct is not None:
            value = int(pct.get("val", "0")) / 100000
            issues.append({"kind": "pct", "value": value, "text": para_text[:80]})
        elif pts is not None:
            value_pt = int(pts.get("val", "0")) / 100
            ratio = value_pt / max(fallback_font_pt, 1)
            issues.append({"kind": "pts", "value": ratio, "points": value_pt, "text": para_text[:80]})
    return issues


def shape_bounds(shape):
    xfrm = shape.find(".//p:spPr/a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return {
        "x": emu_to_in(off.get("x")),
        "y": emu_to_in(off.get("y")),
        "w": emu_to_in(ext.get("cx")),
        "h": emu_to_in(ext.get("cy")),
    }


def weighted_len(text):
    total = 0.0
    for char in text:
        if char.isspace():
            total += 0.35
        elif ord(char) < 128:
            total += 0.55
        else:
            total += 1.0
    return total


def estimate_text_metrics(text, bounds, font_pt, line_height):
    if not text or not bounds:
        return {"lines": 0, "overflow": None}
    font_pt = max(font_pt or 12, 1)
    usable_w_pt = max((bounds["w"] - 0.08) * 72, 1)
    chars_per_line = max(1, usable_w_pt / (font_pt * 0.58))
    lines = 0
    for raw_line in re.split(r"\n+", text):
        units = max(weighted_len(raw_line), 1)
        lines += max(1, math.ceil(units / chars_per_line))
    required_h = lines * (font_pt / 72) * max(line_height, 1)
    available_h = max(bounds["h"] - 0.04, 0)
    if required_h > available_h * 1.08:
        return {
            "lines": lines,
            "overflow": {
            "text": text[:100],
            "fontPt": round(font_pt, 2),
            "estimatedLines": lines,
            "requiredHeightIn": round(required_h, 3),
            "availableHeightIn": round(available_h, 3),
            },
        }
    return {"lines": lines, "overflow": None}


def intersection(a, b):
    x1 = max(a["x"], b["x"])
    y1 = max(a["y"], b["y"])
    x2 = min(a["x"] + a["w"], b["x"] + b["w"])
    y2 = min(a["y"] + a["h"], b["y"] + b["h"])
    return max(0, x2 - x1) * max(0, y2 - y1)


def presentation_size(zf):
    root = ET.fromstring(zf.read("ppt/presentation.xml"))
    sld_sz = root.find("p:sldSz", NS)
    if sld_sz is None:
        return {"w": 13.333, "h": 7.5}
    return {"w": emu_to_in(sld_sz.get("cx")), "h": emu_to_in(sld_sz.get("cy"))}


def slide_number(name):
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def main():
    args = parse_args()
    pptx_path = Path(args.pptx)
    output = Path(args.output)

    reports = []
    with zipfile.ZipFile(pptx_path) as zf:
        size = presentation_size(zf)
        slides = sorted(
            [name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=slide_number,
        )
        for slide_name in slides:
            root = ET.fromstring(zf.read(slide_name))
            slide_no = slide_number(slide_name)
            text_boxes = []
            small_fonts = []
            bad_line_spacing = []
            missing_line_spacing = []
            estimated_overflow = []
            out_of_bounds = []

            for shape in root.findall(".//p:sp", NS):
                tx_body = shape.find("p:txBody", NS)
                if tx_body is None:
                    continue
                text = text_content(tx_body)
                if not text:
                    continue
                bounds = shape_bounds(shape)
                sizes = run_font_sizes(tx_body)
                explicit_sizes = [item["pt"] for item in sizes]
                font_pt = min(explicit_sizes) if explicit_sizes else args.min_font_pt
                max_font_pt = max(explicit_sizes) if explicit_sizes else args.min_font_pt

                for item in sizes:
                    if item["pt"] + 0.01 < args.min_font_pt:
                        small_fonts.append(item)

                line_spacing = 1.0
                for issue in paragraph_line_spacing(tx_body, max_font_pt):
                    line_spacing = min(line_spacing, issue["value"])
                    if issue["value"] + 0.01 < args.min_line_height:
                        bad_line_spacing.append(issue)

                metrics = estimate_text_metrics(text, bounds, max_font_pt, max(line_spacing, args.min_line_height))
                if metrics["overflow"]:
                    estimated_overflow.append(metrics["overflow"])
                has_explicit_line_spacing = bool(paragraph_line_spacing(tx_body, max_font_pt))
                if not args.allow_missing_line_spacing and metrics["lines"] > 1 and not has_explicit_line_spacing:
                    missing_line_spacing.append({"text": text[:100], "estimatedLines": metrics["lines"]})

                if bounds and (
                    bounds["x"] < -0.01
                    or bounds["y"] < -0.01
                    or bounds["x"] + bounds["w"] > size["w"] + 0.01
                    or bounds["y"] + bounds["h"] > size["h"] + 0.01
                ):
                    out_of_bounds.append({"text": text[:80], **{k: round(v, 3) for k, v in bounds.items()}})

                if bounds:
                    text_boxes.append({"text": text[:80], **bounds})

            overlaps = []
            for i in range(len(text_boxes)):
                for j in range(i + 1, len(text_boxes)):
                    a = text_boxes[i]
                    b = text_boxes[j]
                    area = intersection(a, b)
                    if area <= 0.005:
                        continue
                    min_area = max(0.001, min(a["w"] * a["h"], b["w"] * b["h"]))
                    ratio = area / min_area
                    if ratio > 0.18:
                        overlaps.append({"a": a["text"], "b": b["text"], "overlapRatio": round(ratio, 2)})

            issues = []
            if small_fonts:
                issues.append(f"{len(small_fonts)} text runs below {args.min_font_pt:g}pt")
            if bad_line_spacing:
                issues.append(f"{len(bad_line_spacing)} paragraphs below {args.min_line_height:g}x line spacing")
            if missing_line_spacing:
                issues.append(f"{len(missing_line_spacing)} multi-line text boxes missing explicit line spacing")
            if estimated_overflow:
                issues.append(f"{len(estimated_overflow)} text boxes have estimated overflow risk")
            if out_of_bounds:
                issues.append(f"{len(out_of_bounds)} text boxes outside slide bounds")
            if overlaps:
                issues.append(f"{len(overlaps)} likely text box overlaps")

            reports.append(
                {
                    "slide": slide_no,
                    "status": "review" if issues else "pass",
                    "issues": issues,
                    "samples": {
                        "smallFonts": small_fonts[:8],
                        "badLineSpacing": bad_line_spacing[:8],
                        "missingLineSpacing": missing_line_spacing[:8],
                        "estimatedOverflow": estimated_overflow[:8],
                        "outOfBounds": out_of_bounds[:8],
                        "overlaps": overlaps[:8],
                    },
                }
            )

    report = {
        "input": str(pptx_path.resolve()),
        "slides": len(reports),
        "minFontPt": args.min_font_pt,
        "minLineHeight": args.min_line_height,
        "summary": {
            "pass": sum(1 for item in reports if item["status"] == "pass"),
            "review": sum(1 for item in reports if item["status"] != "pass"),
        },
        "slideReports": reports,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(output)
    if args.fail_on_review and report["summary"]["review"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
