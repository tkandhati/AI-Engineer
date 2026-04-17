# Technical Design — AI Engineer Daily

## What it is
Single-page personal tool. Fetches AI news + papers on load, passes them to Claude with the user's 18-month plan context, and returns a synthesized brief + 5 tailored lab recommendations. Tracks learning via Claude-generated quiz questions after each lab.

## Files
| File | Purpose |
|---|---|
| `index.html` | Everything — markup, styles, logic in one file |
| `config.js` | Local secrets (gitignored, never pushed) |
| `config.template.js` | Template to copy → `config.js` |
| `learning_journal/YYYY-MM-DD.md` | Daily entry auto-committed to GitHub |
| `progress_summary.md` | Running score ledger, auto-updated |

## Data flow on page load
```
fetchHN() + fetchArxiv()  →  parallel fetch
         ↓
analyze(hn, arxiv)        →  Claude call with plan context
         ↓
{ brief, labs[5] }        →  stored in localStorage + rendered
```
Cached by date. One Claude call per day unless manually refreshed.

## Lab lifecycle
```
todo → [Start] → inprogress → [Mark done] → done → [quiz loads] → submitted
```
- `inprogress` labs survive page refresh and daily reset
- `todo` labs replaced on daily reset; `done` labs preserved
- `doneIds` prevents repeating completed labs

## Claude calls
| When | Input | Output |
|---|---|---|
| Page load (daily) | HN stories + arXiv papers + plan context | Brief paragraph + 5 labs |
| Lab marked done | Lab title + steps + user history | 4 quiz questions |
| Quiz submitted | Questions + user answers | Score (0-100), feedback, dimension delta |
| Weekly eval | Labs done this week | 4-5 sentence synthesis |

Model: `claude-sonnet-4-6`. Header required: `anthropic-dangerous-direct-browser-access: true`.

## State (localStorage key: `aigrow_v5`)
```js
{
  scores: { rag, eval, finetune, inference, k8s, obs, voice, design }, // 0–100 each
  labs: [{ id, title, dim, status, why, infra, platforms, steps, quiz, eval }],
  doneIds: [],        // all-time completed lab IDs
  weekDoneIds: [],    // this week only, resets on week boundary
  weekStart: 'ISO',
  streak: N,
  lastActive: 'ISO',
  brief: { date, content },
  labsDate: 'ISO',   // date labs were last generated
  lastSync: 'ISO',
  lastWeekEval: 'ISO'
}
```

## GitHub sync
Uses GitHub Contents API (`PUT /repos/{owner}/{repo}/contents/{path}`). Called after quiz submission and weekly eval. Writes two files: `learning_journal/YYYY-MM-DD.md` and `progress_summary.md`. Requires `repo` scope PAT in `config.js`.

## Dimensions
`rag`, `eval`, `finetune`, `inference`, `k8s`, `obs`, `voice`, `design`

## Compute platforms
`colab`, `kaggle`, `runpod`, `vastai`, `lambda`, `local`, `kind`, `ollama` — defined in `PLAT` dict with name, cost string, URL.

## To add a new data source
Add an async fetch function returning `string[]` (one bullet per item). Add it to `Promise.allSettled([fetchHN(), fetchArxiv(), yourFn()])` in `init()` and `refreshLabs()`. Pass the results into `analyze()` and update the prompt.

## To change the plan context
Edit the `ctx()` function. It builds the system prompt context string from `CONFIG.PLAN_START`, `S.scores`, and hardcoded career details.
