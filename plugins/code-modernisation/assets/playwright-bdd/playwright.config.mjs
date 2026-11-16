// Copy into the isolated project only when an existing suitable config is absent.
// Author feature scenarios and steps from this project's observed behavior.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const root = path.dirname(fileURLToPath(import.meta.url));
const baseURL = process.env.MODERNIZE_BASE_URL;
const executablePath = process.env.MODERNIZE_BROWSER_EXECUTABLE;
if (!baseURL || !executablePath) throw new Error('Supply the reviewed local URL and installed Chromium executable.');

// Replace this placeholder with the discovered local startup command. Review its
// effects and readiness route. Auth, external services and fixture setup remain
// project-owned; use a project adapter when this local webServer shape is unsuitable.
const startupCommand = 'REPLACE_WITH_THE_REVIEWED_LOCAL_STARTUP_COMMAND';
if (startupCommand.startsWith('REPLACE_')) throw new Error('Adapt startupCommand to the project before running.');

export default defineConfig({
  testDir: defineBddConfig({
    features: 'features/**/*.feature',
    steps: 'steps/**/*.ts',
    outputDir: '.features-gen',
    missingSteps: 'fail-on-gen',
  }),
  forbidOnly: true,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 15_000,
  globalTimeout: 120_000,
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  use: {
    baseURL, headless: true, launchOptions: { executablePath },
    trace: 'retain-on-failure', screenshot: 'only-on-failure', video: 'off',
  },
  webServer: {
    command: startupCommand, cwd: root, url: baseURL,
    reuseExistingServer: false, timeout: 15_000,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5_000 },
    stdout: 'pipe', stderr: 'pipe',
  },
});
