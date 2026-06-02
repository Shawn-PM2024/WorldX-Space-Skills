#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

function loadPackage(name) {
  try {
    return require(name);
  } catch (error) {
    throw new Error(
      `Cannot load ${name}. Run with NODE_PATH pointing to the bundled node_modules.\nOriginal error: ${error.message}`,
    );
  }
}

function usage() {
  return [
    "Usage: spec_to_editable_pptx.mjs <deck-spec.json> <output.pptx>",
    "",
    "Creates an editable PPTX from a slide spec. Text, shapes, and lines are native PowerPoint objects.",
  ].join("\n");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function cleanColor(value, fallback = "FFFFFF") {
  if (!value) return fallback;
  return String(value).replace(/^#/, "").toUpperCase();
}

function normalizeMargin(value) {
  if (value == null) return 0;
  if (typeof value === "number") return value;
  if (Array.isArray(value)) return value;
  return Number(value) || 0;
}

function withTheme(defaults, theme, style = {}) {
  return {
    fontFace: theme.fontFace || "Aptos",
    color: cleanColor(style.color, cleanColor(defaults.color, "111111")),
    fontSize: style.fontSize ?? defaults.fontSize ?? 18,
    bold: style.bold ?? defaults.bold ?? false,
    italic: style.italic ?? false,
    breakLine: style.breakLine ?? false,
    margin: normalizeMargin(style.margin ?? defaults.margin ?? 0),
    fit: style.fit ?? "shrink",
    valign: style.valign ?? "top",
    align: style.align ?? "left",
    breakLineOnHyphen: false,
    paraSpaceAfterPt: style.paraSpaceAfterPt ?? 0,
    breakLineOnSpace: false,
  };
}

function addText(slide, item, theme) {
  const opts = withTheme({ color: theme.text, fontSize: 18 }, theme, item.style);
  if (item.fill) opts.fill = { color: cleanColor(item.fill) };
  if (item.line) opts.line = lineOptions(item.line);
  if (item.rotate) opts.rotate = item.rotate;
  slide.addText(item.text ?? "", {
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    ...opts,
  });
}

function lineOptions(line = {}) {
  if (line === "none") return { color: "FFFFFF", transparency: 100 };
  return {
    color: cleanColor(line.color, "D9D9D9"),
    width: line.width ?? 1,
    transparency: line.transparency ?? 0,
    beginArrowType: line.beginArrowType,
    endArrowType: line.endArrowType,
    dash: line.dash,
  };
}

function fillOptions(fill) {
  if (!fill) return { color: "FFFFFF", transparency: 100 };
  if (typeof fill === "string") return { color: cleanColor(fill) };
  return {
    color: cleanColor(fill.color, "FFFFFF"),
    transparency: fill.transparency ?? 0,
  };
}

function shapeType(pptx, name = "rect") {
  const map = {
    rect: pptx.ShapeType.rect,
    roundRect: pptx.ShapeType.roundRect,
    ellipse: pptx.ShapeType.ellipse,
    arc: pptx.ShapeType.arc,
    line: pptx.ShapeType.line,
    triangle: pptx.ShapeType.triangle,
    chevron: pptx.ShapeType.chevron,
    pentagon: pptx.ShapeType.pentagon,
    parallelogram: pptx.ShapeType.parallelogram,
  };
  return map[name] || pptx.ShapeType.rect;
}

function addShape(pptx, slide, item, theme) {
  const opts = {
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    fill: fillOptions(item.fill),
    line: lineOptions(item.line),
    rotate: item.rotate,
    transparency: item.transparency,
    radius: item.radius,
  };
  slide.addShape(shapeType(pptx, item.shape), opts);
  if (item.text) {
    slide.addText(item.text, {
      x: item.x + (item.textInsetX ?? 0),
      y: item.y + (item.textInsetY ?? 0),
      w: item.w - 2 * (item.textInsetX ?? 0),
      h: item.h - 2 * (item.textInsetY ?? 0),
      ...withTheme({ color: theme.text, fontSize: 18 }, theme, item.style),
    });
  }
}

function addLine(pptx, slide, item) {
  slide.addShape(pptx.ShapeType.line, {
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    line: lineOptions(item.line),
  });
}

function addImage(slide, item, baseDir) {
  const imgPath = path.resolve(baseDir, item.path);
  slide.addImage({
    path: imgPath,
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    sizing: item.sizing,
  });
}

function applyBackground(slide, bg) {
  if (!bg) return;
  if (typeof bg === "string") {
    slide.background = { color: cleanColor(bg) };
    return;
  }
  slide.background = { color: cleanColor(bg.color, "FFFFFF") };
}

function addElement(pptx, slide, item, theme, baseDir) {
  if (item.type === "text") addText(slide, item, theme);
  else if (item.type === "shape") addShape(pptx, slide, item, theme);
  else if (item.type === "line") addLine(pptx, slide, item);
  else if (item.type === "image") addImage(slide, item, baseDir);
  else throw new Error(`Unsupported element type: ${item.type}`);
}

const [, , specPath, outPath] = process.argv;
if (!specPath || !outPath) {
  console.log(usage());
  process.exit(1);
}

const pptxgenModule = loadPackage("pptxgenjs");
const PptxGenJS = pptxgenModule.default || pptxgenModule;
const pptx = new PptxGenJS();
const spec = readJson(specPath);
const baseDir = path.dirname(path.resolve(specPath));
const theme = {
  fontFace: "Arial",
  text: "151515",
  muted: "60636B",
  accent: "D71920",
  ...spec.theme,
};

pptx.layout = spec.layout || "LAYOUT_WIDE";
pptx.author = spec.author || "practical-ppt";
pptx.company = spec.company || "practical-ppt";
pptx.subject = spec.subject || "";
pptx.title = spec.title || path.basename(outPath, ".pptx");
pptx.lang = spec.lang || "zh-CN";
pptx.theme = {
  headFontFace: theme.fontFace,
  bodyFontFace: theme.fontFace,
  lang: pptx.lang,
};

for (const [index, slideSpec] of spec.slides.entries()) {
  const slide = pptx.addSlide();
  applyBackground(slide, slideSpec.background || theme.background || "FFFFFF");
  for (const item of slideSpec.elements || []) addElement(pptx, slide, item, theme, baseDir);
  if (spec.footer && slideSpec.footer !== false) {
    const footer = spec.footer;
    if (footer.brand) {
      slide.addText(footer.brand, {
        x: footer.x ?? 0.45,
        y: footer.y ?? 7.12,
        w: footer.w ?? 3,
        h: footer.h ?? 0.16,
        fontFace: theme.fontFace,
        fontSize: footer.fontSize ?? 6.5,
        color: cleanColor(footer.color, theme.muted),
        margin: 0,
        fit: "shrink",
      });
    }
    slide.addText(String(index + 1).padStart(2, "0"), {
      x: footer.pageX ?? 12.35,
      y: footer.pageY ?? 7.12,
      w: 0.38,
      h: 0.16,
      fontFace: theme.fontFace,
      fontSize: footer.fontSize ?? 6.5,
      color: cleanColor(footer.color, theme.muted),
      margin: 0,
      align: "right",
      fit: "shrink",
    });
  }
}

const output = path.resolve(outPath);
fs.mkdirSync(path.dirname(output), { recursive: true });
await pptx.writeFile({ fileName: output });
console.log(JSON.stringify({ input: path.resolve(specPath), output, slides: spec.slides.length, editable: true }, null, 2));
