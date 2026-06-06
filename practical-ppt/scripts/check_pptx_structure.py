#!/usr/bin/env python3
import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Check PPTX structure, proof-object variety, and visual richness.")
    parser.add_argument("pptx")
    parser.add_argument("--output", default="pptx-structure-qa.json")
    parser.add_argument("--max-slide-chars", type=int, default=650)
    parser.add_argument("--max-text-boxes", type=int, default=18)
    parser.add_argument("--max-repeated-signature", type=int, default=3)
    parser.add_argument("--fail-on-review", action="store_true")
    return parser.parse_args()


def slide_number(name):
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def text_content(node):
    return "".join(t.text or "" for t in node.findall(".//a:t", NS)).strip()


def classify_slide(text, shape_counts, picture_count):
    lower = text.lower()
    if any(key in text for key in ["股权", "持股", "出资", "60%", "20%"]):
        return "ownership"
    if any(key in text for key in ["方案一", "方案二", "对比", "比较"]):
        return "comparison"
    if any(key in text for key in ["里程碑", "阶段", "时间", "第 "]) or "phase" in lower or "stage" in lower:
        return "timeline"
    if any(key in text for key in ["收入", "现金", "回款", "毛利", "royalty"]):
        return "revenue"
    if any(key in text for key in ["IP", "授权", "转让", "权属", "边界"]):
        return "rights-matrix"
    if any(key in text for key in ["流程", "机制", "牵引", "研发", "销售"]):
        return "process"
    if picture_count:
        return "image-led"
    if shape_counts.get("chevron", 0) >= 2:
        return "process"
    if shape_counts.get("ellipse", 0) >= 3:
        return "relationship"
    if shape_counts.get("rect", 0) >= 25:
        return "table-or-grid"
    return "narrative"


def main():
    args = parse_args()
    pptx_path = Path(args.pptx)
    reports = []
    all_shapes = Counter()

    with zipfile.ZipFile(pptx_path) as zf:
        slides = sorted(
            [name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=slide_number,
        )
        media_files = [name for name in zf.namelist() if name.startswith("ppt/media/")]
        for slide_name in slides:
            root = ET.fromstring(zf.read(slide_name))
            texts = [text_content(node) for node in root.findall(".//p:txBody", NS)]
            texts = [item for item in texts if item]
            joined = " ".join(texts)
            shape_counts = Counter()
            for geom in root.findall(".//p:spPr/a:prstGeom", NS):
                if geom.get("prst"):
                    shape_counts[geom.get("prst")] += 1
                    all_shapes[geom.get("prst")] += 1
            picture_count = len(root.findall(".//p:pic", NS))
            proof_type = classify_slide(joined, shape_counts, picture_count)
            signature = f"{proof_type}|tx:{min(len(texts)//4, 6)}|pic:{min(picture_count, 3)}|rect:{min(shape_counts.get('rect', 0)//10, 6)}|ell:{min(shape_counts.get('ellipse', 0)//5, 6)}"
            issues = []
            if len(joined) > args.max_slide_chars:
                issues.append(f"text density above {args.max_slide_chars} chars")
            if len(texts) > args.max_text_boxes:
                issues.append(f"text box count above {args.max_text_boxes}")
            if proof_type in {"narrative", "table-or-grid"} and len(joined) > 420 and picture_count == 0 and shape_counts.get("chevron", 0) == 0 and shape_counts.get("ellipse", 0) < 3:
                issues.append("dense slide lacks a distinctive proof object")
            reports.append(
                {
                    "slide": slide_number(slide_name),
                    "status": "review" if issues else "pass",
                    "issues": issues,
                    "chars": len(joined),
                    "textBoxes": len(texts),
                    "pictures": picture_count,
                    "proofType": proof_type,
                    "signature": signature,
                    "shapeCounts": dict(shape_counts.most_common(8)),
                    "sample": joined[:140],
                }
            )

    for index in range(len(reports) - args.max_repeated_signature + 1):
        window = reports[index : index + args.max_repeated_signature]
        signatures = [item["signature"] for item in window]
        if len(set(signatures)) == 1:
            for item in window:
                item["status"] = "review"
                item["issues"].append(f"layout signature repeats {args.max_repeated_signature} slides")

    report = {
        "input": str(pptx_path.resolve()),
        "slides": len(reports),
        "mediaFiles": len(media_files),
        "shapeTypes": dict(all_shapes.most_common(12)),
        "proofTypes": dict(Counter(item["proofType"] for item in reports)),
        "summary": {
            "pass": sum(1 for item in reports if item["status"] == "pass"),
            "review": sum(1 for item in reports if item["status"] != "pass"),
        },
        "slideReports": reports,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(output)
    if args.fail_on_review and report["summary"]["review"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
