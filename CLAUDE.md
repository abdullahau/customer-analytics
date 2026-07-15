# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this project is

A personal research library of **customer-base analytics** models — the
"buy-till-you-die" (BTYD) / probability-modelling tradition of Fader, Hardie,
and related work (Theta CLV, PyMC-Marketing, the `lifetimes` package).

Each topic is written as a self-contained **Quarto document** (`.qmd`) that mixes
mathematical exposition (LaTeX/MathJax) with executable Python. Rendered HTML is
published to GitHub Pages: <https://abdullahau.github.io/customer-analytics/>.
The site's landing page is [index.qmd](index.qmd) at the repo root.

This is a documentation/notebook project, **not** an installable app. It *is*
now a small installable package (`utils`/`models` under `lib/`, see below), but
there is no test suite, no CLI, and no server. The "product" is the rendered
essays and the reusable helper code they share.

## Repository layout

| Path | Purpose |
|------|---------|
| `_quarto.yml` | Quarto **project** config: `output-dir: docs`, `execute-dir: project`, the render list, and the shared HTML `format:` block (theme, fonts, toc, css, mathjax) applied to every document. |
| `index.qmd` | Landing page for the published site; hand-maintained list of all pages, grouped by category. |
| `notebooks/` | **The analysis documents** — the primary content, organised by purpose (see the tree below). Some `.qmd` have a same-named `.ipynb` working draft alongside them. |
| `lib/utils/` | Shared, importable Python helpers (`from utils import ...`) — RFM builder, CDNOW/Donation data loaders, Stan/BridgeStan wrappers, plotting templates, KDE bandwidth, model-selection criteria. |
| `lib/models/` | Object-oriented model implementations (`from models import ...`: `BGBB`, `ParetoNBD`, `SbbGB`, ...). **Mostly scaffolding/WIP** — several files are empty or stubbed. Not currently imported by any essay. |
| `assets/quarto-style/` | Shared `style.css` / `custom.scss` referenced **once** by `_quarto.yml`. |
| `stan/src/` | First-party Stan source (`.stan`), compiled binaries, and BridgeStan `.so` for the Bayesian fits (BG/NBD, Pareto/NBD). Referenced from code as `stan_file="stan/src/..."`. |
| `stan/implementations/` | Third-party reference implementations — clones and notebooks (Aaron Goodman Pareto/NBD, clv-master, etc.) — read-only. |
| `data/` | Input datasets (CDNOW, kiwibubbles/panel data, donation incidence, madrigal, CBCV, CAC, retention). |
| `docs/` | **Rendered HTML output** served by GitHub Pages. Generated artifacts — do not hand-edit. Mirrors the `notebooks/` source tree, so page URLs include that path. |
| `references/` | Source papers, images, and third-party notebooks the essays are built from (large; read-only reference). Essays embed its images via root-relative `/references/...` paths. |
| `Projects/` | Background PDFs and spreadsheets (Fader/Hardie tutorials, CBCV papers). |
| `excel-models/` | Spreadsheet implementations mirrored by some essays. |

### The `notebooks/` tree (purpose-driven)

```
notebooks/
├── analyses/            # descriptive / diagnostic essays on a real customer base
│   ├── customer-base-audit
│   ├── buyer-behavior-summary-panel-data
│   ├── buyer-behavior-summary-transaction-log
│   ├── customer-acquisition-cost
│   ├── rfm-summary
│   └── estimating-purchasing-concentration
├── models/             # the probability models
│   ├── acquisition/    # depth-of-repeat, finite-mixture-bg-sales-forecast, dynamic-changepoint-new-product
│   ├── retention/      # beta-geometric, beta-discrete-weibull, subscription-retention
│   │                   #   + sBG-Model.py (marimo interactive app) with its layouts/ dir

│   ├── purchasing/     # nbd-overview, nbd-otb, bg-nbd, bg-nbd-stan, bg-bb, pareto-nbd (WIP)
│   ├── spend/          # gamma-gamma
│   └── clv/            # rfm-and-clv
├── valuation/          # cbcv-subscription-based  (customer-based corporate valuation)
└── data-prep/          # cdnow-dataset
```

## How rendering / publishing works

- `_quarto.yml` defines a Quarto **project** (`type: default`, `output-dir: docs`).
  Individual `.qmd` files carry only their `title` (plus the rare per-doc
  override, e.g. `bg-nbd-stan`); all shared `format:` options live in `_quarto.yml`.
- **`execute-dir: project`** makes every document's code run with the working
  directory set to the **repo root**. So root-relative paths in *code cells*
  resolve regardless of how deep the `.qmd` sits: `pd.read_csv("data/...")`,
  `stan_file="stan/src/bg-nbd"`, and `from utils import ...` all work.
- **Markdown resource paths must be project-root-relative** (leading `/`), because
  they are resolved relative to the *document*, not the CWD. Embedded images use
  `![](/references/...)`. The stylesheet is set once in `_quarto.yml`
  (`css: assets/quarto-style/style.css`).
- Documents use the Jupyter engine (`jupyter: python3`) and execute against the
  project's `.venv`.
- Render from the repo root with `uv run quarto render` (whole project) or
  `uv run quarto render notebooks/models/purchasing/bg-nbd.qmd` (single doc).
  Output HTML lands under `docs/` mirroring the source path; **page URLs therefore
  include the `notebooks/...` path** — update `index.qmd` links when files move.

> When adding a new document: put it under the right `notebooks/` subfolder, give
> it a minimal front matter (`title:` only), use `/references/...` for any images,
> and add its link to `index.qmd` under the matching category.

## The Python helpers (`lib/`)

- `utils` and `models` are installed as top-level packages via the
  `[tool.hatch.build.targets.wheel] packages = ["lib/utils", "lib/models"]` entry
  in `pyproject.toml`. `uv sync` installs the project editable, so
  `from utils import ...` / `from models import ...` resolve from anywhere.
- Data loaders (`CDNOW`, `Donation`) locate files via a `__file__`-relative path
  (`lib/utils/../../data/...`). If you move `lib/utils/`, fix that depth.
- Reusable logic belongs in `lib/utils/` (importable, exported via
  `lib/utils/__init__.py`) — keep document code focused on exposition.

## Environment & tooling

- Package/env manager: **uv** (`pyproject.toml` + `uv.lock`), Python **3.14**.
  Bootstrap a fresh checkout with `uv sync`; run Python via `uv run python ...`.
- Core stack: polars & pandas, numpy/scipy, matplotlib/seaborn, **altair** and
  **great-tables** (primary output/visual libraries), statsmodels, arviz,
  **BridgeStan** + **cmdstanpy** for Bayesian fits, `lifetimes`.
- Linting/formatting: **ruff** (line length 88; config in `pyproject.toml`).
  Type checking: **ty** (configured for the `.venv`).

## Conventions & expectations

- **polars-first** for new data work (most helpers and newer essays use polars);
  some older essays use pandas.
- Visual output prefers **altair** charts and **great-tables** tables; match the
  existing `assets/quarto-style` look rather than introducing new styling.
- Math is written in LaTeX for MathJax; keep notation consistent with the cited
  papers (Fader/Hardie conventions).
- When a `.ipynb` and a same-named `.qmd` both exist, the notebook is usually the
  working draft and the `.qmd` the publishable version — confirm which the user
  wants edited.

## What NOT to touch unless asked

- `docs/` — generated output; regenerate via Quarto, don't hand-edit.
- `references/`, `Projects/`, `excel-models/`, third-party clones under
  `stan/implementations/` — source material / third-party reference implementations.
- `.venv/`, `uv.lock` — managed by uv.
