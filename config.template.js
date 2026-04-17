// Copy this file to config.js and fill in your values.
// config.js is gitignored — it will never be pushed to GitHub.
// ANTHROPIC_KEY goes in the terminal when starting proxy.py, not here.

window.CONFIG = {
  PROXY_URL:     'http://localhost:5001',    // local proxy — run proxy.py first
  GITHUB_TOKEN:  'ghp_...',                 // github.com → Settings → Developer Settings → PAT (repo scope)
  GITHUB_REPO:   'tkandhati/AI-Engineer',
  PLAN_START:    '2025-04-01'               // your 18-month plan start date (YYYY-MM-DD)
};
