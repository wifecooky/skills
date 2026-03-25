#!/usr/bin/env node

const path = require('path');

async function main() {
  const args = process.argv.slice(2);
  const htmlPath = args[0];
  const outputPath = args[1];
  const width = parseInt(args[2]) || 1200;

  if (!htmlPath || !outputPath) {
    console.error('Usage: node capture.js <html> <png> [width]');
    process.exit(1);
  }

  let chromium;
  try {
    chromium = require('playwright').chromium;
  } catch {
    console.error('Playwright not found. Run: cd word-card && npm install && npx playwright install chromium');
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width, height: 800 });

  const fileUrl = 'file://' + path.resolve(htmlPath);
  await page.goto(fileUrl, { waitUntil: 'networkidle' });

  // Wait for D3 constellation to finish rendering
  try {
    await page.waitForFunction(() => window.__constellationReady === true, { timeout: 10000 });
  } catch {
    console.warn('WARN: D3 constellation readiness timeout — capturing anyway');
  }

  // Extra settle time for animations
  await page.waitForTimeout(800);

  // Full-page capture
  const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
  await page.setViewportSize({ width, height: bodyHeight });
  await page.waitForTimeout(300);
  await page.screenshot({
    path: path.resolve(outputPath),
    type: 'png',
    clip: { x: 0, y: 0, width, height: bodyHeight }
  });

  await browser.close();
  console.log('OK: ' + path.resolve(outputPath));
}

main().catch(err => {
  console.error(err.message);
  process.exit(1);
});
