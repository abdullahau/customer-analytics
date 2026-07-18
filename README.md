# Customer-Base Analytics

A research library of **probability models of buyer behavior** — parsimonious stochastic models that treat observed buying as the visible output of a latent behavioral process. Two traditions sit side by side here:

- the **Fader–Hardie** tradition, modelling *one firm's customer base* to project future purchasing, retention, and **customer lifetime value (CLV)** — the bulk of what is written so far;
- the **Ehrenberg–Bass** tradition (Ehrenberg, Goodhardt, Chatfield, Bass, Uncles, Sharp), modelling *a whole category of competing brands* with the **NBD** and **NBD-Dirichlet**, and the empirical laws that follow from them. See [The Ehrenberg-Bass tradition](#the-ehrenbergbass-tradition-and-the-nbd-dirichlet) — source material is in the repo, essays are not yet written.

Each topic is a self-contained [Quarto](https://quarto.org) essay (mathematical exposition + executable Python) published to GitHub Pages: [**https://abdullahau.github.io/customer-analytics/**](https://abdullahau.github.io/customer-analytics/){.uri}

> **New here?** Read [The big idea](#the-big-idea-probability-models-for-buyer-behavior) for the one-page mental model, skim [the taxonomy](#dimension-1--the-firmcustomer-relationship-2×2-taxonomy) to see how the models relate, then jump to [Getting started](#getting-started) to run the code.

------------------------------------------------------------------------

## The big idea: probability models for buyer behavior {#the-big-idea-probability-models-for-buyer-behavior}

We only ever get a *"foggy window"* onto a customer's true tendencies: someone who bought twice last year is not necessarily a "two per year" buyer. So instead of extrapolating the observed numbers, we model the **latent process** that generated them. Two ingredients:

1.  **An individual-level model** for one customer's behavior given latent traits θ — e.g. Poisson (how many purchases), exponential/geometric (how long until they lapse), Bernoulli (buy vs. not).
2.  **A mixing distribution** (gamma, beta, …) describing how θ is spread across the customer base — i.e. **heterogeneity**.

Combining the two gives a **mixture model** for a randomly-chosen customer; Bayes' theorem then turns any customer's observed history into forward-looking inferences — **P(alive), expected future transactions, residual CLV** — typically from nothing more than **RFM** (recency, frequency, monetary value), which are the *sufficient statistics* for these models. Formally: `past = f(θ)` and `future = f(θ)`, in contrast to the regression / data-mining `future = f(past)` approach.

A recurring lesson from this literature is that many "dynamics" people try to model (a slowing aggregate purchase rate, retention rates that *rise* with tenure) are **not** individual-level effects at all — they are **sorting effects** that fall out of heterogeneity: the low-θ customers survive longer and come to dominate the surviving population ("the ruse of heterogeneity"). Don't "fix" them with ad-hoc time trends.

## Dimension 1 — the firm–customer relationship (2×2 taxonomy)

Two questions classify any customer base (Schmittlein, Morrison & Colombo 1987; Fader & Hardie 2009) and **determine which model is even admissible**:

- **Is churn observed?** *Contractual* (the customer cancels / fails to renew — we see it) vs. *non-contractual* (the customer just silently stops — "silent attrition", and we must infer whether they are dead or merely dormant).
- **Can transactions happen anytime?** *Continuous* vs. *discrete* (only at fixed epochs).

The contractual/non-contractual boundary is **fundamental — a model built for one side must never be applied to the other.**

|   | **Non-contractual** (churn latent) | **Contractual** (churn observed) |
|-------------------|-----------------------------|------------------------|
| **Continuous** (any time) | grocery, hotel, mail-order → **Pareto/NBD, BG/NBD, NBD, NBD/OTB** | credit card, mobile, utilities → **exponential-gamma, Weibull-gamma** |
| **Discrete** (fixed epochs) | event attendance, charity drives, refills → **BG/BB** | magazine/SaaS subs, insurance, gym → **sBG, BdW** |

In **non-contractual** settings the modelling challenge is telling a dead customer apart from one in a long hiatus; in **contractual** settings churn is known, so the focus shifts to **duration / retention** and projecting the survivor curve.

## Dimension 2 — the building blocks (counting / timing / choice)

Every model is assembled from — and usually **integrates** — three process types, each an individual-level model paired with a heterogeneity distribution:

| Block | Question | Individual model → with heterogeneity |
|------------------|------------------|------------------------------------|
| **Counting** | how many? | Poisson → **NBD** (gamma); Bernoulli → **beta-Binomial** (beta); zero-truncated NBD as `k→0` → **LSD** (one parameter, buyers only) |
| **Timing** | when / how long alive? | exponential → **Pareto / exp-gamma**; geometric → **sBG**; Weibull → **Weibull-gamma / BdW** |
| **Choice** | whether / which / how much? | Bernoulli/binomial (buy-vs-not, one-time-buyer); multinomial → **Dirichlet-multinomial** (which brand, among *g*); spend → **Gamma-Gamma** |

**Integrated models** combine the blocks to solve jointly for the latent parameters:

- **Counting + Timing** — a purchasing process *and* an "alive/death" process: **Pareto/NBD** (Poisson-gamma buying + exponential-gamma dropout), **BG/NBD** (dropout after a purchase, beta-geometric), **BG/BB** (their discrete analog). Also "stickiness" (# visits × duration/visit) and new-product **trial timing + repeat counting** (depth-of-repeat).
- **Counting + Counting** — purchase *volume* (# transactions × units/transaction); page views (# visits × pages/visit).
- **Counting + Choice** — brand purchasing (category incidence × brand choice), "conversion" (# visits × buy/not-buy), and the **NBD/OTB** one-time-buyer split.

Layer a **spend sub-model** (Gamma-Gamma) on a purchasing model and you get monetary value → **CLV = margin × revenue/transaction × DET** (discounted expected transactions). Roll **acquisition + retention + spend** together and you get firm-level **customer-based corporate valuation (CBCV)**.

## The recurring math (one screen)

The same handful of moves reappears in every essay:

- **Mixture = individual model integrated over heterogeneity.** Each closed form comes from `∫ P(data | θ) g(θ) dθ`: Poisson × gamma → **NBD**; geometric × beta → **sBG**; binomial × beta → **beta-Binomial**; exponential × gamma → **exponential-gamma/Pareto**.
- **Forward recursions** make the models spreadsheet-cheap. NBD: `P(X=x) = (r+x−1)/(x(α+1)) · P(X=x−1)`, from `P(X=0)=(α/(α+1))ʳ`. sBG: `P(T=t) = (β+t−2)/(α+β+t−1) · P(T=t−1)`, from `P(T=1)=α/(α+β)`.
- **Estimation** is by **maximum likelihood** on the frequency counts (often just Excel Solver), or **Bayesian** (Stan / BridgeStan) for the `-stan` essays. A third option, standard in the Ehrenberg literature and not yet used here, is **"mean and zeros"**: fit the NBD from just the observed mean `m` and the observed proportion of non-buyers `p₀` by solving `p₀ = (1+a)^(−m/a)`. It is **≥90% efficient** for typical purchase data (vs. under 50% for method of moments) and needs only the two numbers panel tabulations actually report.
- **Time scaling.** Under stationarity `m` is proportional to the period length `T` while the heterogeneity exponent `k` is **invariant** to it — `k` describes how customers differ in the long run, which doesn't depend on how long you look. That single fact turns one base period into a prediction of **penetration growth** at every other period length: `b_T = 1 − (1+aT)^(−k)`, `w_T = Tm/b_T`.
- **Individual-level inference via Bayes.** The posterior `g(θ | data) ∝ P(data | θ) g(θ)` yields P(alive), expected future transactions, and — for spend/response — **regression-to-the-mean**: the best estimate is a precision-weighted blend of the customer's own history and the population mean.
- **Goodness of fit** via the χ² statistic `Σ (fᵢ − npᵢ)² / npᵢ` against the observed histogram.
- **CLV** discounts expected future transactions (DET) and multiplies by margin × revenue/transaction; **iso-value curves** trace equal-CLV contours across the recency/frequency plane.

## What the source literature establishes

The claims above are not stylistic preferences — they were argued and measured. The numbers below are drawn from the [per-folder reading notes](#reading-map-source-material) under `references/papers/`; each links to the folder that documents it.

**Simple models win *out of sample*, and in-sample fit does not predict it.** [`retention/`](references/papers/retention/retention-summary.md) replicates a data-mining textbook's sidebar titled *"Parametric approaches do not work"*: fitted on 7 years of survival data, a quadratic reaches **R² = 0.998** and then misses year-12 survival by **+92%** (linear −81%, exponential −30%). The 2-parameter sBG, fitted to the same 7 years, is off by **+4%** and **+2%** on the two segments. The regressions also fail *logically* — the quadratic's survivor function starts rising, the linear one goes negative. Separately, in [`purchasing/`](references/papers/purchasing/purchasing-summary.md), the 3-parameter NBD/OTB passes a χ² fit test (24.8 vs critical 26.3) on data where a much richer integrated model fails badly (51.6 vs critical 6.0).

**Complexity relocates misspecification rather than removing it.** Three independent instances across the corpus: a rich integrated model concludes purchase timing is Erlang-5 when the exponential was fine — the extra structure was **counterbalancing a different mis-specified component**; an inventory covariate silently absorbs the "dead period" that Erlang-2's non-zero mode would have modelled, inflating its elasticity ~2×; and a plain exponential-gamma trial model fitted to <18 weeks of data **mistakes promotion effects for heterogeneity**, returning a heterogeneity parameter ~50× its full-sample value. Added parameters do not sit idle — whichever is flexible enough will soak up the error.

**Aggregate fit can hide process error.** In [`new-product/`](references/papers/new-product/new-product-summary.md), a stationary covariates model tracks cumulative sales acceptably inside its calibration window while its *"percent triers repeating"* diagnostic diverges from actuals **within that same window**; its week-52 forecast is 23% high. The fix is to validate on decomposed diagnostics (trial / first repeat / additional repeat), not on the total.

**Recency and frequency interact non-monotonically.** The iso-value curves in [`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md) **bend backwards**: past a certain point, *more* prior purchases with *old* recency means *less* future value, because a formerly frequent buyer's silence is strong evidence of death while a light buyer's identical silence is unremarkable. A matched pair in the CDNOW data gives **DET 4.6 for the light buyer against 1.9 for the heavy one**. No monotone-in-frequency scoring model can represent this.

**The zero class is small per head and large in aggregate.** Also CDNOW: the 12,054 customers with no repeat purchase are worth about **$4.40 each** — yet collectively about **5% of the cohort's entire future value**, more than most of the other 27 RFM cells.

**A repeat-buying rate is not a retention rate.** Substituting one for the other into `rᵗ` is the specific error behind the two badly-wrong valuations in the founding CBCV paper (Amazon and eBay, undervalued **83%** and **88%**) — and it is endemic: J.D. Power's annual *"Customer Retention Study"* computes a repurchase rate; widely-taught HBS cases apply contractual CLV formulas to a catalogue retailer and a hotel chain. See [`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md) and [`valuation/`](references/papers/valuation/valuation-summary.md).

**Constant retention rates bias customer-base valuations by 25–50%.** Cohort-level retention *rises* with tenure; company-reported retention looks flat only because it averages across cohorts of different maturity. At a constant 0.833 the residual value of a customer is a flat $343 forever; the heterogeneous model gives **$288 → $394 → $568** at first, second and fifth renewal.

**Elasticity is not impact.** [`valuation/`](references/papers/valuation/valuation-summary.md) — retention has by far the highest elasticity to shareholder value (≈4.4 for Netflix), but it barely moves year to year, whereas the *number of customers* has low elasticity (0.9) and swings hard. Combining elasticity with observed variation: retention contributed **+27%**, customer count **−57%**. If modelling effort is finite, spend it on the **acquisition** sub-model.

**More data can make things worse.** In [`methods/`](references/papers/methods/methods-summary.md), a 3-million-member credit-card panel used *without* selection correction produces holdout MAPE of **481–860%** — dramatically worse than ignoring the panel entirely. Granular data is not automatically an improvement over coarse but representative data.

## The Ehrenberg–Bass tradition and the NBD-Dirichlet {#the-ehrenbergbass-tradition-and-the-nbd-dirichlet}

> **Status: source material collected, essays not yet written.** This section describes what the literature says and where the work will live. Nothing in `notebooks/` implements it yet.

Everything above models **one firm's customer base** from a transaction log. The Ehrenberg–Bass tradition asks a different question of different data: given a **whole product category** — instant coffee, toothpaste, retail chains — how do the competing brands' buyers overlap, and is any given brand's loyalty *normal for its size*? The inputs are panel/audit **aggregates** (category penetration and buying rate; each brand's share and penetration), not per-customer RFM.

### The model

The **NBD-Dirichlet** ("the Dirichlet", Goodhardt, Ehrenberg & Chatfield 1984) is a *counting + choice* model — the same two building blocks used elsewhere in this repo, composed differently:

| Layer | Assumption | Result |
|---|---|---|
| Category incidence | Poisson purchases, rate μ; μ ~ gamma | **NBD** with mean `MT`, exponent `K` |
| Brand choice | multinomial choice vector `p`; `p` ~ **Dirichlet(α₁…α_g)** | Dirichlet-multinomial given `n` |
| Link | choice and rate independent across consumers | the full mixture |

It needs only `g + 2` numbers: the `αⱼ`, plus `M` and `K`. With `S = Σαⱼ`, brand share is `μⱼ = αⱼ/S`. The two structural parameters are both **diversity measures**: `K` for how much people differ in *how often* they buy the category, `S` for how much they differ in *which brand* they pick (small `S` → polarized; large `S` → everyone alike).

The **additivity property** makes it computable: any group of brands merges into a "super-brand" with `α = Σ`. Brand `j` versus "all others" therefore collapses to a **beta-binomial**, and every output is `Σₙ Pₙ × (beta-binomial term)` with the tail truncated.

### What it produces: brand performance measures

The deliverable is a table of **"theoreticals"** to set against the **"observeds"** — penetration `b`, purchase frequency `w`, category purchases per brand buyer `w_p`, **share of category requirements**, **100% loyal (sole) buyers**, **average portfolio size**, brand-pair **duplication** `b_{j|k}`, **repeat rate** `ρ = (αⱼ+1)/(S+1)`, and **polarization** `φ = 1/(S+1)` — which gives the compact identity

```
ρ = μ + φ − φμ
```

i.e. a brand's repeat rate is just its market share, standardized by a single category-wide loyalty constant. The 1984 paper's toothpaste fit recovers all eight brands' penetrations to within about ±1 percentage point from market shares alone.

### The empirical laws — predictions, not separate theories

- **Double Jeopardy.** Small brands suffer twice: fewer buyers *and* slightly lower `w`, SCR and repeat rate. A sorting consequence of share, not evidence of a weak brand. It doesn't actually need the Dirichlet — it follows algebraically from two other empirical facts (buyers of any brand buy the *category* at about the same rate; and buying X is near-independent of buying Y), giving `w_X(1−b_X) = w_Y(1−b_Y) = constant`. The `(1−b)` factor absorbs the strong trend in `w` over long periods and stays ≈1 over short ones, so period length is handled without appearing in the equation. Short, purely algebraic, and the cleanest demonstration of "heterogeneity, not individual dynamics" in either tradition.
- **Duplication of Purchase.** `b_{j|k} ≈ D · bⱼ` with `D` near-constant across brand pairs — buyers are shared in proportion to penetration, not according to positioning.
- **Penetration is the growth lever.** Since `m = b × w` and `w` barely varies across brands, share differences are almost entirely *penetration* differences. Planning to grow by making existing buyers buy more is, in Ehrenberg's phrase, "aiming at something altogether unusual or unlikely, like making pigs fly." This is the mathematical basis of Byron Sharp's *How Brands Grow*.
- **Markets are largely unsegmented.** The Dirichlet is precisely the "independence except for the constraint `Σp = 1`" distribution — so its close fit across 40+ categories *is* the quantitative evidence for non-segmentation.

### The methodological stance

Ehrenberg's *Data Reduction* is the companion argument about method, and it is as much the point as the model. Its thesis is that analysing **one** dataset well is the wrong unit of work: results are only useful insofar as they generalise, so the job is to reduce each dataset to a summary usable in the *next* analysis. A good summary is **succinct**, **complete** (the data can be reconstructed from it, within stated approximation), and **usable**.

That reframing has teeth, and several of its consequences apply to every essay here, not just the Dirichlet ones:

- **Two significant figures** — defined as "digits that vary from one number to another". Rounding costs 1–2% of the observed variation and is often what makes the pattern visible at all.
- **Observed vs Theoretical, side by side.** Not a fit statistic in a caption but paired O/T columns, so the reader sees *where* the model succeeds and fails. This is how the *Repeat-Buying* market audit is built.
- **Always state the range of conditions** a result has been checked over — product-fields, countries, period lengths, sub-groups. A model without one is a curve fit.
- **Report residual scatter, not R².** Correlations measure residual variance *relative to* each dataset's own total variance, so they can't be compared across datasets: equal scatter can give wildly different `r`, and equal `r` can hide different relationships.
- **Models as interpretative norms.** "Is 53% repeat-buying high, low, or normal for a 19%-share brand?" — Ehrenberg's worked example takes one reading through three successively better norms and reverses the conclusion twice.
- **A regression fitted to one dataset generally cannot hold for another** — both least-squares lines pass through *that* dataset's means, and two straight lines share only one point. So among the many equations that fit acceptably (fit discriminates between them poorly), choose the one that also holds elsewhere.

This is a genuine counterpoint to regression and data-mining practice, and it sharpens the parsimony principle stated above rather than merely echoing it. There is also a real tension with this repo's current practice worth naming: Ehrenberg's own estimation is deliberately crude — mean-and-zeros, lookup tables, Excel Solver — on the grounds that estimator efficiency is almost never the binding constraint whereas generalisation always is. He isn't arguing that Stan is wrong; he's arguing it's usually not where the effort should go.

### The source material, and reading notes

All of it sits in [`references/papers/brand-choice/`](references/papers/brand-choice/):

| Item | |
|---|---|
| Goodhardt, Ehrenberg & Chatfield, *The Dirichlet* | JRSS-A 147(5), 1984, 621–655 — read before the RSS, with the discussion |
| Rungie & Goodhardt, *Calculation of Theoretical Brand Performance Measures…* | Marketing Bulletin 15, 2004, Technical Note 2 — the algebra for every BPM |
| Ehrenberg, ***Repeat-Buying: Facts, Theory and Applications*** | Griffin / OUP, 1988 (1st ed. North-Holland 1972). The NBD/LSD theory; Ch. 13 and App. C on the Dirichlet are new to the 1988 edition |
| Ehrenberg, ***Data Reduction*** | Wiley, 1975 (preface 1974, corrected reprint 1978). The methodological companion |
| **[`Repeat-Buying — reading notes`](references/papers/brand-choice/repeat-buying-summary.md)** | chapter-by-chapter reading notes: the formulae, estimators, empirical laws and documented failure boundaries |
| **[`Data Reduction — reading notes`](references/papers/brand-choice/data-reduction-summary.md)** | reading notes on the method: empirical generalisation, layout rules, the regression critique |

A third-party Python port of the R `NBDdirichlet` package is in
[`references/implementations/NBDdirichlet-main/`](references/implementations/NBDdirichlet-main/)
(MIT; derived from Feiming Chen's R package). It is a useful reference but **not yet
verified** — its `S` estimate disagrees with both the R package and the 1984 paper on
the paper's own toothpaste example, and `Appendix C` of *Repeat-Buying* is the
authority to check it against.

Still to be created: `lib/models/Dirichlet.py`, the essays under
`notebooks/models/brand-choice/`, and the toothpaste worked example under `data/`.

## The model catalogue

Rendered pages are linked from [`index.qmd`](index.qmd); sources live under [`notebooks/`](notebooks/), organized by purpose.

| Essay (`notebooks/…`) | Taxonomy cell | Building blocks | The idea |
|-----------------|-----------------|-----------------|---------------------|
| `models/purchasing/nbd-overview` | non-contractual, cont. | counting | Poisson buying + gamma heterogeneity; no death. Baseline for `E[X(t)]`. |
| `models/purchasing/nbd-otb` | non-contractual, cont. | counting + choice | NBD plus a "one-time buyer" spike-at-zero segment. |
| `models/purchasing/bg-nbd` (+ `-stan`) | non-contractual, cont. | counting + timing | Dropout *after a purchase* (beta-geometric). Easy MLE (even Excel). P(alive), `E[Y(t)｜x,tₓ,T]`. |
| `models/purchasing/pareto-nbd` | non-contractual, cont. | counting + timing | Dropout at *any* time (exponential-gamma). The original SMC model; harder to estimate. |
| `models/purchasing/bg-bb` | non-contractual, disc. | counting + timing | Discrete analog of Pareto/NBD (beta-Bernoulli buying + beta-geometric death); donation incidence. |
| `models/retention/beta-geometric` (sBG) | contractual, disc. | timing | Constant individual retention + beta heterogeneity; aggregate retention *rises* with tenure. |
| `models/retention/beta-discrete-weibull` (BdW) | contractual, disc. | timing | sBG generalized to allow duration dependence (Weibull). |
| `models/retention/subscription-retention` | contractual, disc. | timing | Discrete-time contractual retention applied; plus the interactive `sBG-Model.py` (marimo). |
| `models/acquisition/depth-of-repeat` | new-product | timing + counting | Decompose new-product sales into **trial** `R(0)` + **repeat** `R(J)` by depth-of-repeat. |
| `models/acquisition/finite-mixture-bg-sales-forecast` | new-product | timing (mixture) | Unit-sales forecast via a beta-geometric finite mixture. |
| `models/acquisition/dynamic-changepoint-new-product` | new-product | timing (non-stationary) | Buying-rate **changepoints** decay as a product moves "new" → "established" (Kiwi Bubbles). |
| `models/spend/gamma-gamma` | spend | choice / amount | Spend per transaction; gamma-gamma with regression-to-the-mean on `mₓ`. |
| `models/clv/rfm-and-clv` | integrated | counting + timing + spend | **CLV = margin × rev/txn × DET** (Pareto/NBD + gamma-gamma); iso-value curves. |
| `valuation/cbcv-subscription-based` | contractual (firm) | acquisition + retention + spend | Roll sub-models into a DCF → firm value; fit to public ADD/LOSS/END/REV (DISH, SiriusXM). |

**Which paper each essay implements** — the reading notes carry the derivations, the published parameter values to check a fit against, and the authors' own stated limitations:

| Essay | Source paper | Reading notes |
|---|---|---|
| `purchasing/nbd-otb` | Fader & Hardie, *A note on an integrated model of customer buying behavior* (2002) — with `nbd_otb.xls` | [`purchasing/`](references/papers/purchasing/purchasing-summary.md) §1 |
| `retention/beta-geometric`, `sBG-Model.py` | Fader & Hardie, *How to Project Customer Retention* (2007) — Appendix B is the Excel recipe | [`retention/`](references/papers/retention/retention-summary.md) |
| `retention/beta-discrete-weibull` | Fader & Hardie, *BdW* — motivated in the sBG paper's extensions section | [`retention/`](references/papers/retention/retention-summary.md) §6 |
| `acquisition/depth-of-repeat` | Eskin (1973) + the 2004 ART Forum tutorial and its four Excel workbooks | [`new-product/`](references/papers/new-product/new-product-summary.md) §1, §4 |
| `acquisition/dynamic-changepoint-new-product` | Fader, Hardie & Huang, *A Dynamic Changepoint Model* (2004) — Kiwi Bubbles | [`new-product/`](references/papers/new-product/new-product-summary.md) §3 |
| `spend/gamma-gamma` | Fader, Hardie & Lee (2005) §"Adding Monetary Value"; Colombo & Jiang (1999) | [`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md) §1.4 |
| `clv/rfm-and-clv` | Fader, Hardie & Lee, *RFM and CLV: Iso-Value Curves* (2005) — CDNOW `r=.55, α=10.58, s=.61, β=11.67` | [`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md) §1 |
| `valuation/cbcv-subscription-based` | McCarthy, Fader & Hardie, *Valuing Subscription-Based Businesses* (2017) | [`valuation/`](references/papers/valuation/valuation-summary.md) §3 |
| `analyses/estimating-purchasing-concentration` | Schmittlein, Cooper & Morrison (1993) on model-based "80/20" concentration | [`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md) §1.2 |

`purchasing/nbd-overview`, `bg-nbd`, `pareto-nbd` and `bg-bb` trace to Ehrenberg (1959), Fader–Hardie–Lee (2005a), Schmittlein–Morrison–Colombo (1987) and Fader–Hardie–Shang (2010) respectively — all four are catalogued with their variants in [`foundations/`](references/papers/foundations/foundations-summary.md) §1.3–1.4 and [`valuation/`](references/papers/valuation/valuation-summary.md) §6.

**Descriptive analyses** (`notebooks/analyses/`) — the customer-base audit and buyer-behavior summaries (RFM, purchasing concentration / Lorenz, CAC) that precede and motivate the models (see below). **Data prep** (`notebooks/data-prep/`) builds the CDNOW dataset used throughout.

**Repeat purchasing — non-contractual** (`notebooks/models/purchasing/`) 
- **NBD overview** — the Poisson-gamma counting model; foundation for everything. 
- **NBD/OTB** — NBD with a "one-time buyer" (spike-at-zero) segment. 
- **BG/NBD** (+ a **Stan/Bayesian** version) — the easy-to-estimate alternative to Pareto/NBD; dropout modeled as beta-geometric after each purchase. 
- **Pareto/NBD** — the original "counting your customers" model (exponential-gamma dropout at any time). 
- **BG/BB** — the discrete-time analog (beta-Bernoulli buying + beta-geometric death), e.g. annual donation incidence.

**Retention — contractual, discrete-time** (`notebooks/models/retention/`) 
- **Beta-geometric (sBG)** — constant individual retention prob. + beta heterogeneity; explains why *aggregate* retention rises with tenure. Plus an interactive [marimo](https://marimo.io) app, `sBG-Model.py`. 
- **Beta-discrete-Weibull (BdW)** — generalizes sBG to allow duration dependence. 
- **Subscription retention** — discrete-time contractual retention applied.

**Acquisition & new-product forecasting** (`notebooks/models/acquisition/`) 
- **Depth-of-repeat** — decompose new-product sales into **trial** + **repeat** (by depth-of-repeat level). 
- **Finite-mixture BG sales forecast** — unit-sales forecasting via a beta-geometric finite mixture. 
- **Dynamic changepoint** — a multiple-event timing model whose buying-rate *changepoints* evolve as the product moves from "new" to "established" (Fader–Hardie–Huang; the "Kiwi Bubbles" test market).

**Spend & CLV** (`notebooks/models/spend/`, `notebooks/models/clv/`) 
- **Gamma-Gamma** — monetary value / spend-per-transaction (with regression-to-the-mean). 
- **RFM & CLV** — iso-value curves linking recency/frequency/monetary to CLV.

**Valuation** (`notebooks/valuation/`) 
— **CBCV** for subscription businesses (DISH / SiriusXM style): fit acquisition + retention + spend sub-models to publicly-disclosed customer data and roll them into firm value.

------------------------------------------------------------------------

## Summarizing Buyer Behavior

Before any model, we *describe* the customer base. Using transactions log data and marketing spend data we calculate:

1.  Monthly sales over time
2.  Total customers acquired
3.  Customer acquisition cost (CAC)
4.  Distribution of spend per purchase
5.  Initial versus repeat sales volume
6.  Initial versus repeat average order value (AOV)
7.  Sales and AOV by source
8.  First-purchase profitability
9.  Cohorted sales (the “C3”)
10. Revenue retention curves
11. Cumulative spend per customer
12. Distribution of total spend by customer
13. Customer concentration (“Pareto”) chart

What the analysis summarize:

1.  Growth
2.  Unit costs
3.  Unit profitability (unit economic performance)
4.  Retention
5.  Heterogeneity (customers, time)
6.  Yield on CAC
7.  CLV / CAC
8.  Monthly/Annual Recurring Revenue (MRR/ARR)
9.  Average Revenue Per User (ARPU)
10. Logo churn
11. Revenue Churn
12. Weekly/Monthly/Annual Active Users (DAU/MAU/AAU)
13. Gross Margin
14. Contribution Margin
15. Payback Period
16. Magic Number: Net new ARR divided by sales & marketing spend
17. Rule of 40: Growth rate plus profit margin should exceed 40%

## Models to Implement

**Ehrenberg–Bass branch** (source material collected, nothing implemented):

- NBD-Dirichlet (category-level brand choice) + brand performance measures
- Duplication of Purchase / Double Jeopardy benchmark tables
- **Conditional trend analysis** — repeat-buying split by *previous* purchase level. Distinguishes a real loyalty failure (heavy buyers below norm) from an excess of occasional buyers (light buyers below norm, heavy on norm) — opposite implications, identical in the aggregate
- **NBD penetration-growth curves** — project `b` and `w` across period lengths from one base period, via `k`-invariance
- **LSD** repeat-buying formulae (the one-parameter `q` shortcuts)
- **"Mean and zeros" estimation** — fit the NBD from just `m` and `p₀`; ≥90% efficient on typical purchase data and the same method used to fit the Dirichlet's `K`

**Gaps identified while reading the Fader–Hardie source papers** (each has a documented method and public data):

- **Noncontractual CBCV** (McCarthy & Fader 2018) — the natural destination for the repo's Pareto/NBD machinery; Overstock and Wayfair disclosures are public. Currently only the *subscription* case is implemented
- **Trial-model component factorial** (Fader–Hardie–Zeithammer 2003) — 8 models × 44 calibration lengths, plus the **indexed parameter-stability plot** (divide each estimate by its full-sample value and trace it against calibration length). The technique generalizes to every model here and would answer "how much data before this fit is trustworthy?"
- **Separate initial vs repeat retention curves** — every retention model in the repo pools all customers, yet reacquired customers demonstrably behave differently. Matters increasingly as a customer base matures
- **Bootstrap valuation intervals** — the CBCV essays produce point estimates only; resampling model residuals yields a valuation *distribution*, which is what makes "is this stock mispriced?" answerable
- **Corporate drag** (Damodaran 2018) — non-user costs deducted from user-based value; absent from all the marketing CBCV papers and large enough to change the answer by a factor
- **Maximum proxy likelihood / data fusion** (McCarthy & Oblander) — combine aggregate disclosures with panel data under selection correction; a good fit for the existing Stan/BridgeStan setup
- **Time-varying covariates in NBD-type models** (Gupta 1991) — nothing in `notebooks/` currently does this; note the integrated hazard must accumulate over *all* intervening periods, not just the purchase week

**Process models:**

- Weibull-Gamma acquisition model
- Exponential-Gamma retention model
- Point process transaction model
- Simulating order flow dynamics
- Acquisition process
- Purchase process
- Spend process

------------------------------------------------------------------------

## Getting started {#getting-started}

Prerequisites: [**uv**](https://docs.astral.sh/uv/) (Python 3.14 is pinned via `.python-version`).

``` bash
git clone https://github.com/abdullahau/customer-analytics
cd customer-analytics
uv sync                       # create the .venv and install deps + the local `utils`/`models` packages

# Render the whole site (all essays) to docs/ :
uv run quarto render

# ...or work on a single essay:
uv run quarto render notebooks/models/purchasing/bg-nbd.qmd
uv run quarto preview notebooks/models/spend/gamma-gamma.qmd   # live preview
```

A full render executes every notebook, including the Stan/Bayesian fits, so it is slow. See [CLAUDE.md](CLAUDE.md) for the repository layout, the Quarto/rendering model, and coding conventions.

### Repository structure (short)

| Path | What |
|-----------------------|-------------------------------------------------|
| `notebooks/` | the essays — `analyses/`, `models/{acquisition,retention,purchasing,spend,clv}/`, `valuation/`, `data-prep/` |
| `lib/utils`, `lib/models` | importable Python helpers (`from utils import …`) — RFM builder, data loaders, Stan/BridgeStan wrappers, plotting |
| `stan/src`, `stan/implementations` | first-party Stan models; third-party reference implementations |
| `data/` | CDNOW, donation incidence, panel data (Kiwi Bubbles), CBCV (DISH/SIRI), retention, CAC |
| `assets/`, `docs/` | shared Quarto style; rendered HTML output (GitHub Pages) |
| `references/` | source papers, tutorials, spreadsheets & figures (see the reading map below) |

## Reading map (source material) {#reading-map-source-material}

Everything lives under [`references/`](references/), organized so a file sits near what it teaches:

- **`references/papers/`** — journal articles, grouped by model family. **Every folder carries a `<folder>-summary.md`** with section-by-section reading notes — the formulae, the empirical results, the load-bearing quotes, and how each paper maps onto this repo. Start there rather than with the PDFs.
  - **[`foundations/`](references/papers/foundations/foundations-summary.md)** — Fader & Hardie *Probability Models for Customer-Base Analysis* (2009): the source of the 2×2 taxonomy, the `past = f(θ)` framing, and the RFM-sufficiency result. Plus Ascarza, Fader & Hardie *Marketing Models for the Customer-Centric Firm* (2017) — a map of the wider field (acquisition targeting, churn campaigns, cross-sell, uplift modelling) that this repo deliberately does *not* cover.
  - **[`purchasing/`](references/papers/purchasing/purchasing-summary.md)** — the **NBD/OTB** note (2002), where a 3-parameter spreadsheet model beats a far richer integrated one on the same data; Gupta *Stochastic Models of Interpurchase Time* (1991), the recipe for time-varying covariates in NBD-type models (and the integrated-hazard subtlety they require).
  - **[`retention/`](references/papers/retention/retention-summary.md)** — *How to Project Customer Retention* (2007): the sBG, its forward recursion, its closed-form retention rate `r_t = (β+t−1)/(α+β+t−1)`, and a complete Excel recipe in Appendix B.
  - **[`new-product/`](references/papers/new-product/new-product-summary.md)** — Eskin *Depth of Repeat* (1973), the origin of the trial/repeat decomposition; *Forecasting New Product Trial* (2003), an 8-model factorial establishing which components actually matter; Fader–Hardie–Huang *Dynamic Changepoint* (2004), whose nesting structure formally connects new-product nonstationarity to the stationary NBD; the 2004 ART Forum tutorial and its Excel workbooks.
  - **[`spend-clv/`](references/papers/spend-clv/spend-clv-summary.md)** — Fader–Hardie–Lee *RFM and CLV: Iso-Value Curves* (2005); *Simple probability models for computing CLV and CE* (2015), the DEL/DERL/DET/DERT formula set for all four taxonomy cells; *Reconciling and Clarifying CLV Formulas* (2012), which resolves the three competing textbook CLV formulas.
  - **[`valuation/`](references/papers/valuation/valuation-summary.md)** — the CBCV line read in order, each paper correcting the last: Gupta–Lehmann–Stuart *Valuing Customers* (2004) → Schulze–Skiera–Wiesel *leverage effect* (2012) → McCarthy–Fader–Hardie *subscription CBCV* (2017) → McCarthy–Fader *noncontractual CBCV* (2018). Plus Damodaran *Valuing Users* (2018), the same problem from the finance side, and Reutterer's annotated bibliography of Pareto/NBD variants.
  - **[`methods/`](references/papers/methods/methods-summary.md)** — McCarthy & Oblander *Scalable Data Fusion with Selection Correction*: fusing sparse company disclosures with a 3-million-member credit-card panel, correcting for panel selection, and separating **initial from repeat** acquisition and churn.
  - **[`brand-choice/`](references/papers/brand-choice/)** — the whole Ehrenberg–Bass branch, papers **and** books: Goodhardt, Ehrenberg & Chatfield *The Dirichlet* (JRSS-A 1984, with the RSS discussion); Rungie & Goodhardt *Calculation of Theoretical Brand Performance Measures…* (Marketing Bulletin 2004); Ehrenberg *Repeat-Buying* (1988) and *Data Reduction* (Wiley 1975) — plus chapter-by-chapter reading notes for both books ([Repeat-Buying](references/papers/brand-choice/repeat-buying-summary.md), [Data Reduction](references/papers/brand-choice/data-reduction-summary.md)).
- **`references/tutorials/`** — Fader–Hardie teaching material (handout **+** its Excel spreadsheets, kept together): `applied-probability-models[-art12]/` (the counting/timing/choice build-up), `intro-probability-models/`, `workshop-cba/`, `panel-data/` (analyzing buyer behavior), `depth-of-repeat/`, `sbg-estimation/`, `customer-base-audit/` (TCBA companion).
- **`references/case-studies/`** — data-rich bundles: `cdnow/` (the BG/NBD & Pareto/NBD workhorse dataset + notes) and `cbcv/` (DISH & SiriusXM acquisition/retention spreadsheets).
- **`references/implementations/`** — third-party code: `pymc-marketing/`, `pareto-nbd-pydata/`, `NBDdirichlet-main/` (Python port of the R NBD-Dirichlet package; unverified — see above).
- **`references/figures/`** — images embedded in the essays; **`references/spreadsheets/`** — standalone reference sheets (e.g. the CLV taxonomy); **`references/learning/`** — tangential background (Bayesian methods, time-series decomposition, great-tables).

## Overview

![Price-Implied Expectations through Unit-Economics Simulation](references/figures/Price-Implied-Expectations-through-Unit-Economics-Simulation.png)

![Workflow — Lifetimes Library CLV Model](references/figures/Workflow-Lifetimes-Library-CLV-Model.png)

![CBCV Infographic](references/figures/CBCV-Infographic.png)

## Reference

- [Ehrenberg-Bass Institute](https://www.marketingscience.info/) — the Dirichlet / empirical-generalisation tradition
- [Bruce Hardie](https://www.brucehardie.com/) — notes, papers, datasets
- [Peter Fader](https://www.petefader.com/)
- [Ian Frankenburg](https://ian-frankenburg.com/)
- [Theta (Fader & McCarthy)](https://thetaclv.com/) — customer-based corporate valuation
- [PyMC-Marketing](https://www.pymc-marketing.io/en/stable/) — CLV models
- [lifetimes (Python package)](https://github.com/CamDavidsonPilon/lifetimes)
- [Journal of Empirical Generalisations in Marketing Science](https://www.empgens.com/)