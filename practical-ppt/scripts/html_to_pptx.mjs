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
      `Cannot load ${name}. Run with NODE_PATH pointing to the bundled node_modules, for example:\n` +
        `NODE_PATH="/path/to/node_modules" node scripts/html_to_pptx.mjs deck.html deck.pptx\n` +
        `Original error: ${error.message}`,
    );
  }
}

function parseArgs(argv) {
  const args = { _: [], selector: ".slide", width: 1600, height: 900, tmpDir: "" };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--selector") args.selector = argv[++i];
    else if (token === "--width") args.width = Number(argv[++i]);
    else if (token === "--height") args.height = Number(argv[++i]);
    else if (token === "--tmp-dir") args.tmpDir = argv[++i];
    else if (token === "--help" || token === "-h") args.help = true;
    else args._.push(token);
  }
  return args;
}

function usage() {
  return [
    "Usage: html_to_pptx.mjs <input.html|url> <output.pptx> [--selector .slide] [--width 1600] [--height 900]",
    "",
    "Each selected slide element is captured as a full-slide PNG and inserted into a 16:9 PPTX.",
  ].join("\n");
}

function toTarget(input) {
  if (/^https?:\/\//i.test(input) || input.startsWith("file://")) return input;
  return pathToFileURL(path.resolve(input)).href;
}

const args = parseArgs(process.argv.slice(2));
if (args.help || args._.length < 2) {
  console.log(usage());
  process.exit(args.help ? 0 : 1);
}

const input = args._[0];
const output = path.resolve(args._[1]);
const outDir = path.dirname(output);
const tmpDir = path.resolve(args.tmpDir || path.join(outDir, `${path.basename(output, ".pptx")}-slides`));
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(tmpDir, { recursive: true });

const { chromium } = loadPackage("playwright");
const pptxgenModule = loadPackage("pptxgenjs");
const PptxGenJS = pptxgenModule.default || pptxgenModule;

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

  const locator = page.locator(args.selector);
  const count = await locator.count();
  if (count === 0) {
    throw new Error(`No slide elements found for selector: ${args.selector}`);
  }

  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "practical-ppt";
  pptx.subject = `Rendered from ${input}`;
  pptx.title = path.basename(output, ".pptx");
  pptx.company = "practical-ppt";
  pptx.lang = "zh-CN";

  for (let i = 0; i < count; i += 1) {
    const slideNode = locator.nth(i);
    await slideNode.scrollIntoViewIfNeeded();
    const box = await slideNode.boundingBox();
    if (!box || box.width < 10 || box.height < 10) {
      throw new Error(`Slide ${i + 1} has an invalid bounding box.`);
    }

    const imagePath = path.join(tmpDir, `slide-${String(i + 1).padStart(3, "0")}.png`);
    await slideNode.screenshot({ path: imagePath, type: "png" });

    const pptSlide = pptx.addSlide();
    pptSlide.background = { color: "FFFFFF" };
    pptSlide.addImage({ path: imagePath, x: 0, y: 0, w: 13.333333, h: 7.5 });
  }

  await pptx.writeFile({ fileName: output });
  console.log(JSON.stringify({ input: path.resolve(input), output, slides: count, screenshots: tmpDir }, null, 2));
} finally {
  await browser.close();
}
