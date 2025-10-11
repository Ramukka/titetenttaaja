#!/usr/bin/env node
/**
 * Synchronises shared JSON exams into the Tauri frontend (src/tentit).
 */

const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const sourceDir = path.resolve(projectRoot, "..", "tentit");
const targetDir = path.resolve(projectRoot, "src", "tentit");

if (!fs.existsSync(sourceDir)) {
  console.error(
    `Lähdekansiota ei löytynyt: ${sourceDir}. Varmista, että tentit/ on olemassa projektin juuressa.`
  );
  process.exit(1);
}

fs.rmSync(targetDir, { recursive: true, force: true });
fs.mkdirSync(targetDir, { recursive: true });
fs.cpSync(sourceDir, targetDir, { recursive: true });

console.log(`Tentit päivitetty Tauri-frontille (${targetDir}).`);
