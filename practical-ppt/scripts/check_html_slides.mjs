#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

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

function parseArgs(argv) {
  const args = {
    _: [],
    selector: ".slide",
    width: 1600,
    height: 900,
    output: "qa-report.json",
    minTextPx: 16,
    minLineHeight: 1,
    allowSmallChrome: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--selector") args.selector = argv[++i];
    else if (token === "--width") args.width = Number(argv[++i]);
    else if (token === "--height") args.height = Number(argv[++i]);
    else if (token === "--output") args.output = argv[++i];
    else if (token === "--min-text-px") args.minTextPx = Number(argv[++i]);
    else if (token === "--min-line-height") args.minLineHeight = Number(argv[++i]);
    else if (token === "--allow-small-chrome") args.allowSmallChrome = true;
    else if (token === "--help" || token === "-h") args.help = true;
    else args._.push(token);
  }
  return args;
}

function usage() {
  return [
    "Usage: check_html_slides.mjs <input.html|url> [--output qa-report.json] [--selector .slide]",
    "",
    "Checks slide HTML for text overflow, overlaps, out-of-bounds elements, font-size issues, and line-height issues.",
    "",
    "Default --min-text-px is 16px, roughly equivalent to 12pt in PPT.",
  ].join("\n");
}

function toTarget(input) {
  if (/^https?:\/\//i.test(input) || input.startsWith("file://")) return input;
  return pathToFileURL(path.resolve(input)).href;
}

function intersection(a, b) {
  const x1 = Math.max(a.left, b.left);
  const y1 = Math.max(a.top, b.top);
  const x2 = Math.min(a.right, b.right);
  const y2 = Math.min(a.bottom, b.bottom);
  const width = Math.max(0, x2 - x1);
  const height = Math.max(0, y2 - y1);
  return width * height;
}

const args = parseArgs(process.argv.slice(2));
if (args.help || args._.length < 1) {
  console.log(usage());
  process.exit(args.help ? 0 : 1);
}

const input = args._[0];
const output = path.resolve(args.output);
fs.mkdirSync(path.dirname(output), { recursive: true });

const { chromium } = loadPackage("playwright");
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage({
    viewport: { width: args.width, height: args.height },
    deviceScaleFactor: 1,
  });
  await page.goto(toTarget(input), { waitUntil: "networkidle" });
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });

  const count = await page.locator(args.selector).count();
  const slides = [];

  for (let i = 0; i < count; i += 1) {
    const slide = page.locator(args.selector).nth(i);
    await slide.scrollIntoViewIfNeeded();
    const data = await slide.evaluate((root) => {
      const slideRect = root.getBoundingClientRect();
      const nodes = Array.from(
        root.querySelectorAll("h1,h2,h3,h4,p,li,td,th,span,small,strong,em,button,[data-qa-text],.txt,.text,.label,.caption,.node,.card"),
      );

      function hasDirectText(el) {
        return Array.from(el.childNodes).some(
          (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0,
        );
      }

      const candidates = nodes.filter((el) => {
          const style = getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          const text = (el.innerText || el.textContent || "").trim();
          return (
            text.length > 0 &&
            rect.width > 1 &&
            rect.height > 1 &&
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            (hasDirectText(el) || ["H1", "H2", "H3", "H4", "LI", "TD", "TH", "BUTTON"].includes(el.tagName))
          );
        });

      const indexByElement = new Map(candidates.map((el, index) => [el, index]));
      const elements = candidates.map((el, index) => {
          const style = getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          const text = (el.innerText || el.textContent || "").trim().replace(/\s+/g, " ");
          return {
            index,
            ancestors: candidates
              .filter((other) => other !== el && other.contains(el))
              .map((other) => indexByElement.get(other)),
            tag: el.tagName.toLowerCase(),
            text: text.slice(0, 80),
            fontSize: Number.parseFloat(style.fontSize) || 0,
            lineHeight: style.lineHeight === "normal" ? 0 : Number.parseFloat(style.lineHeight) || 0,
            left: rect.left - slideRect.left,
            top: rect.top - slideRect.top,
            right: rect.right - slideRect.left,
            bottom: rect.bottom - slideRect.top,
            width: rect.width,
            height: rect.height,
            overflowX: el.scrollWidth - el.clientWidth > 2,
            overflowY: el.scrollHeight - el.clientHeight > 2,
          };
        });

      const titleNode = root.querySelector("[data-title],h1,h2");
      return {
        title: (titleNode?.innerText || titleNode?.textContent || "").trim().replace(/\s+/g, " "),
        width: slideRect.width,
        height: slideRect.height,
        elements,
      };
    });

    const overflow = data.elements.filter((el) => (el.overflowX || el.overflowY) && el.text.length > 3);
    const outOfBounds = data.elements.filter(
      (el) => el.left < -1 || el.top < -1 || el.right > data.width + 1 || el.bottom > data.height + 1,
    );
    const tooSmall = data.elements.filter((el) => {
      const likelyChrome = el.text.length <= 3 || el.top < 90 || el.bottom > data.height - 45;
      return el.fontSize > 0 && el.fontSize < args.minTextPx && !(args.allowSmallChrome && likelyChrome);
    });
    const badLineHeight = data.elements.filter((el) => {
      if (!el.lineHeight || !el.fontSize) return false;
      const ratio = el.lineHeight / el.fontSize;
      return ratio + 0.01 < args.minLineHeight;
    });
    const fontSizes = [...new Set(data.elements.map((el) => Math.round(el.fontSize)).filter(Boolean))].sort((a, b) => a - b);
    const overlaps = [];

    for (let a = 0; a < data.elements.length; a += 1) {
      for (let b = a + 1; b < data.elements.length; b += 1) {
        const first = data.elements[a];
        const second = data.elements[b];
        if (first.ancestors.includes(second.index) || second.ancestors.includes(first.index)) continue;
        const area = intersection(first, second);
        if (area <= 16) continue;
        const minArea = Math.max(1, Math.min(first.width * first.height, second.width * second.height));
        if (area / minArea > 0.12) {
          overlaps.push({
            a: first.text,
            b: second.text,
            overlapRatio: Number((area / minArea).toFixed(2)),
          });
        }
      }
    }

    const issues = [];
    if (overflow.length) issues.push(`${overflow.length} text elements overflow their boxes`);
    if (outOfBounds.length) issues.push(`${outOfBounds.length} text elements are outside the slide`);
    if (tooSmall.length) issues.push(`${tooSmall.length} text elements are below ${args.minTextPx}px`);
    if (badLineHeight.length) issues.push(`${badLineHeight.length} text elements have line-height below ${args.minLineHeight}x`);
    if (fontSizes.length > 9) issues.push(`many font sizes detected: ${fontSizes.join(", ")}`);
    if (overlaps.length) issues.push(`${overlaps.length} likely text overlaps`);

    slides.push({
      slide: i + 1,
      title: data.title || "",
      canvas: { width: data.width, height: data.height },
      status: issues.length ? "review" : "pass",
      issues,
      samples: {
        overflow: overflow.slice(0, 8),
        outOfBounds: outOfBounds.slice(0, 8),
        tooSmall: tooSmall.slice(0, 8),
        badLineHeight: badLineHeight.slice(0, 8),
        overlaps: overlaps.slice(0, 8),
        fontSizes,
      },
    });
  }

  const report = {
    input: path.resolve(input),
    selector: args.selector,
    slides: count,
    generatedAt: new Date().toISOString(),
    summary: {
      pass: slides.filter((slide) => slide.status === "pass").length,
      review: slides.filter((slide) => slide.status !== "pass").length,
    },
    slideReports: slides,
  };

  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report.summary));
  console.log(output);
} finally {
  await browser.close();
}
