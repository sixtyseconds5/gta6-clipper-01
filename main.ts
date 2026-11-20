// gta6-clipper-01 — entry runner.
//
// The make.fun harness mounts this repository at MAKEFUN_BOT_DIR (default
// /bot) and expects the submission payload at MAKEFUN_OUTPUT_DIR (default
// /output). This program does exactly one job: copy VIDEO.json from the
// repository root into the output directory, creating that directory first
// if it does not exist yet. Any failure is reported on stderr and the
// process exits with code 1 so the harness marks the run as failed.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const repoRoot = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const source = join(repoRoot, "VIDEO.json");
const destination = join(outputDir, "VIDEO.json");

try {
  mkdirSync(outputDir, { recursive: true });
  copyFileSync(source, destination);
} catch (err) {
  const reason = err instanceof Error ? err.message : String(err);
  console.error(`gta6-clipper-01: could not copy ${source} to ${destination}: ${reason}`);
  process.exit(1);
}

console.log(`gta6-clipper-01: VIDEO.json written to ${destination}`);
