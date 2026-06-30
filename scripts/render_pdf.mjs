#!/usr/bin/env node
/** Render a printable local HTML file through Chrome using Playwright. */

import { createRequire } from "node:module";
import { access } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [input, output, title] = process.argv.slice(2);
if (!input || !output || !title) {
  console.error("Usage: render_pdf.mjs <input.html> <output.pdf> <document title>");
  process.exit(2);
}

async function existing(path) {
  if (!path) return false;
  try {
    await access(path, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function chromePath() {
  if (await existing(process.env.PDF_CHROME_PATH)) return process.env.PDF_CHROME_PATH;
  const candidates = process.platform === "win32"
    ? [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
      ]
    : ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"];
  for (const candidate of candidates) {
    if (await existing(candidate)) return candidate;
  }
  return undefined;
}

const executablePath = await chromePath();
const browser = await chromium.launch({
  executablePath,
  headless: true,
  args: ["--font-render-hinting=medium"],
});

try {
  const page = await browser.newPage();
  await page.emulateMedia({ media: "print" });
  await page.goto(pathToFileURL(resolve(input)).href, { waitUntil: "load" });
  await page.pdf({
    path: resolve(output),
    format: "A4",
    printBackground: true,
    displayHeaderFooter: true,
    margin: { top: "17mm", right: "15mm", bottom: "16mm", left: "15mm" },
    headerTemplate: `<div style="width:100%; padding:0 15mm; color:#78716c; font:7.5pt Arial, sans-serif;">${title}</div>`,
    footerTemplate: '<div style="width:100%; padding:0 15mm; color:#78716c; font:7.5pt Arial, sans-serif; text-align:center;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    outline: true,
    preferCSSPageSize: true,
  });
} finally {
  await browser.close();
}
