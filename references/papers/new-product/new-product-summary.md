# `new-product/` — reading summary

Four distinct works on **trial/repeat forecasting for new consumer packaged goods** — the oldest
strand in this repo (Eskin 1973) and the one that most directly confronts **nonstationarity**.

| # | Work | Year | Length |
|---|---|---|---|
| 1 | Eskin, **"Dynamic Forecasts of New Product Demand Using a Depth of Repeat Model"**, *JMR* 10 (May), 115–129 | 1973 | 15 pp. |
| 2 | Fader, Hardie & Zeithammer, **"Forecasting New Product Trial in a Controlled Test Market Environment"**, *Journal of Forecasting* 22, 391–410 | 2003 | 20 pp. |
| 3 | Fader, Hardie & Huang, **"A Dynamic Changepoint Model for New Product Sales Forecasting"**, *Marketing Science* 23(1), 50–65 | 2004 | 17 pp. |
| 4 | Fader & Hardie, **"Forecasting Repeat Buying for New Products and Services"**, 15th Annual ART Forum tutorial | 2004 | 56 slides |

**On the duplicate:** `A Dynamic Changepoint Model...pdf` and `...-v2.pdf` are the **same 2004
*Marketing Science* article** from two different sources (JSTOR scan vs INFORMS download). The v2 has
cleaner text extraction; content is identical.

Supporting files under `forecasting-repeat-buying/`: four Excel workbooks
(`dor_model_calibration.xls`, `dor_model_forecast.xls`, `artforum04_part2a/b.xls`) implementing the
tutorial's models. These drive
[`models/acquisition/depth-of-repeat`](../../../notebooks/models/acquisition/) and are mirrored under
`references/tutorials/depth-of-repeat/`.

> **Framing caveat from [../foundations/foundations-summary.md](../foundations/foundations-summary.md) §2.3:** this literature
> is **product-centric**, not customer-centric — it acquires customers *for the product*, which "is
> not the same as acquiring customers for the firm." The models are still directly usable by a
> customer-centric firm (McCarthy et al. do so in CBCV), but that was not their original purpose.

---

## 1. Eskin (1973) — the depth-of-repeat model

The origin of the depth-of-repeat decomposition still used today. Positioned explicitly as an
**"in-between" model**: simpler than Massy's STEAM, richer than Fourt–Woodlock.

### 1.1 The decomposition

Define `R_t(J)` = cumulative number of consumers repeating **at least** `J` times by period `t`. Note
the indexing convention: **`J = 0` means one purchase**, so `R(0)` is the *trial* function and `R(1)`
is the repeat function.

```
S_t = Σ_{J=0}^{∞}  R_t(J) · V_t(J)                                            (1)
```

— sales = (number of consumers at each cumulative repeat level) × (average units purchased at that
level), summed over levels.

The refinement that makes it work: **condition on when the previous purchase occurred.** `RI_{it}(J)`
= cumulative fraction who repeat a `J`th time by period `t` *given* the `(J−1)`th purchase was made in
period `i`.

```
R_t(J) = Σ_{i=1}^{t}  RI_{it}(J) · ΔR_i(J−1)                                  (2)
```

**Two reasons the tables are indexed by time-of-entry `i`** — both still relevant:

1. **Early buyers behave differently from late buyers.** Quoting Fourt & Woodlock: *"The first new
   buyers of an item are typically heavy buyers of a product class."* So "one would not wish to
   predict sales for late buyers based on aggregates dominated by early buyers." Also picks up
   marketing changes (distribution build, promotion).
2. **Exposure time differs.** Each entry cohort has a different number of periods available in which
   to repurchase — hence the characteristic **triangular shape** of the `RI` tables (available time
   = `t − i`).

### 1.2 The three behavioural assumptions

From inspecting `RI` plots for *established* products (six repeat levels, 52 weeks from entry):

- each curve rises rapidly then slowly, **mode at T = 1 week**, and does not reach a limit within 52
  weeks;
- the six curves are **roughly proportional early and parallel later**;
- the 52-week conversion proportions **increase monotonically in `J`, at a decreasing rate**.

**A1 — Geometric-Stretch function.** Consumers entering the repeat class each period = a constant `δ`
plus a fixed fraction `(1 − γ)` of the distance to the limit line `α + δT`.

- `γ` = **slope factor** (how fast the curve approaches the limit)
- `δ` = **stretch factor** (tilts the ceiling upward rather than flat)

At `δ = 0` this reduces to the Fourt–Woodlock trial equation — Eskin's move is to **apply it to every
repeat level, not just trial.**

**A2 — Parameter stability.** `γ` is the same for all repeat levels *except trial*; `δ` is the same for
all repeat levels *and* all time-of-entry cells. This is what makes higher, data-sparse repeat levels
forecastable.

**A3 — Conversion proportions.** The 52-week conversion proportion `RI_{·52}(J)` approaches a limit
`RI(∞) ≤ 1` as `J` grows. **Trial and first repeat are excluded from the continuous part of the
function**, "given their critical role in determining sales and given that they do not predict higher
values of repeat well."

**A4 — Units per transaction**, linear in `J` up to a maximum, covering all repeat levels except trial.

A useful modelling footnote: the specification implies **at most one transaction per consumer per week**
— "approximately true for our data... For estimation purposes, second purchases within a single week
are coded in the following week."

---

## 2. Fader, Hardie & Zeithammer (2003) — which trial-model components actually matter

A clean factorial experiment on model structure. The question: **do marketing covariates improve
forecasts, and can they shorten the test market?**

### 2.1 The general form and the 2×2×2 design

```
F(t) = p ∫ F(t|θ) g(θ) dθ                                                     (1)
F(t|X(t),β) = p ∫ F(t|θ, X(t), β) g(θ) dθ                                     (2)
```

Three components, each present or absent → **eight models**:

1. **structural model** `F(t|θ)` — individual time-to-trial;
2. **heterogeneity** `g(θ)` — gamma, or a point mass (= homogeneous);
3. **penetration limit** `p` — the "never triers" term, from Fourt & Woodlock's observation that
   cumulative trial approaches a ceiling below 100%. (Rationale: "one would typically expect that
   diapers will not be purchased by panellists who do not have children under 3 years old.")

Plus covariates via **proportional hazards at the individual level** — deliberately *not* the diffusion
literature's practice of bolting covariates onto the aggregate `F(t)`, which "has resulted in some
rather ad-hoc model specifications."

The with-covariates exponential cdf:

```
F(t|θ, X(t), β) = 1 − exp(−θ·A(t))

A(t) = Σ_{i=1}^{Int(t)} exp[β'x(i)]  +  [t − Int(t)]·exp[β'x(Int(t+1))]
```

Note `A(t)` **accumulates the covariate effect over every intervening week** — the same integrated-
hazard logic as [../purchasing/purchasing-summary.md](../purchasing/purchasing-summary.md) §2.2. With `β = 0`, `A(t) = t`
and everything collapses to the baseline.

**The eight models** (all exponential-based, hence "E"; "G" = gamma heterogeneity, "N" = never-triers,
"C" = covariates):

| Model | F(t) | Never-triers | Heterogeneity | Covariates |
|---|---|---|---|---|
| E | `1 − e^{−λt}` | N | N | N |
| E_N | `p[1 − e^{−λt}]` | Y | N | N |
| EG | `1 − (α/(α+t))^r` | N | Y | N |
| EG_N | `p[1 − (α/(α+t))^r]` | Y | Y | N |
| E_C | `1 − e^{−λA(t)}` | N | N | Y |
| E_NC | `p[1 − e^{−λA(t)}]` | Y | N | Y |
| EG_C | `1 − (α/(α+A(t)))^r` | N | Y | Y |
| EG_NC | `p[1 − (α/(α+A(t)))^r]` | Y | Y | Y |

**The exponential baseline is not assumed but argued for** — Appendix B (separate, at
brucehardie.com/papers/fhz_appendix_b.pdf) concludes the exponential is "the 'correct' structural
model for trial purchasing." Contrast with their pointed remark about the prior literature: *"no model
developer has provided direct evidence for his choice of structural model; the particular
distributions employed have simply been **assumed** to be correct."*

### 2.2 Design and data

IRI **BehaviorScan** controlled test markets; five datasets (A–E) from year-long tests, 1989–1996 —
shelf-stable juices, cookies, salty snacks, salad dressings. Covariates: feature/display promotion,
plus advertising and coupon as exponentially-smoothed **"adstock" carryover** variables (Broadbent
1984).

Interval-censored likelihood (only the *week* of trial is known):

```
LL = Σ_{i=1}^{t_c} nᵢ ln[F(i) − F(i−1)]  +  (N − Σ nᵢ) ln[1 − F(t_c)]
```

**`t_c` is varied from 8 to 51 weeks in one-week steps** → `8 models × 44 calibration lengths ×
5 datasets = 1,760` fits. **MAPE** is the error measure (scale-free — needed because 52-week
penetration ranges from ~6% to ~40% across datasets).

### 2.3 Findings

**The pure exponential is hopeless.** Even calibrated on 51 weeks to forecast week 52 alone, its
absolute percentage error (16%) "is still worse than that of several models with utilizing only 12
weeks of calibration data."

**By week 20, all seven remaining models are reasonable**, with little improvement after — a directly
managerial finding about when to stop waiting.

**Covariates buy you time, not accuracy.** The three models reaching their MAPE "elbow" earliest
(~week 12) are exactly those with covariates plus at least one other component: **E_NC, EG_C, EG_NC**.

**Never-triers is the component to drop.** Two independent reasons:

1. *Forecasting:* E_NC (covariates + never-triers, no heterogeneity) is consistently worse than
   EG_C/EG_NC. "While the 'never triers' component appears to help somewhat, it is more important to
   directly capture heterogeneity in trial rates."
2. *Parameter stability:* the three models with never-triers plus another component (E_NC, EG_N,
   EG_NC) show **severe, unpredictable instability even at long calibration periods**. "Clear evidence
   of the inadequacies of the 'never triers' component, and a strong indication that **using more
   bells and whistles does not necessarily lead to a better model**."

**And the gamma subsumes it anyway:** the gamma "can accommodate 'never triers' by treating them as
**'very slow but eventual' buyers** who will enter the market at a late stage (perhaps on the order of
years) which, for the standard forecasting horizon, is equivalent to never trying."

**The parameter-stability method is worth stealing.** Divide every parameter estimate by its own
52-week estimate → an index where 1.0 = perfect recovery of the full-information value. Plot against
calibration length. This detects **systematic bias and random instability separately**, and it
independently confirmed the forecasting conclusions.

**Why plain EG fails early — a diagnosis, not just a result.** With <18 weeks of data, EG is nearly the
worst model, because *"the EG model is **mistaking the unexplained covariate effects strictly as
evidence of consumer heterogeneity**, and is inferring a very distorted distribution of purchase rates
across households."* The magnitude is striking: **at 18 weeks its average `r` is about 50× its
52-week estimate.** Past week 20, "as the set of consumers entering the market becomes sufficiently
diverse, true heterogeneity effects dominate any apparent differences due to early marketing
activity," and EG becomes the best model, moving "almost precisely to the 52-week values."

This is the third instance in the corpus of **one component absorbing another's misspecification** —
cf. the Erlang-5 and inventory cases in [../purchasing/purchasing-summary.md](../purchasing/purchasing-summary.md).

### 2.4 The five principles (their §Conclusions)

1. **Exponential** is the right structural model; apparent irregularity is heterogeneity + covariates
   + noise.
2. **Heterogeneity is essential.**
3. **Never-triers is not** — a weak proxy for heterogeneity, confounded with it, and badly unstable.
4. **Covariates help most with short calibration periods** — EG_C achieves ~10% MAPE with **12 weeks**
   of data.
5. **Without covariates, don't forecast before ~20 weeks**; after that, plain EG is excellent and
   actually *surpasses* EG_C on both criteria over most longer windows.

Their own summary of the surprise: covariates "apparently do not contribute much to a model's
forecasting capabilities **if the model is well-specified in the first place** and a reasonable amount
of data is available." But — "even when the analyst wishes to rely principally on a model with
covariates, she should probably still run the pure EG model to get a quick and easy **'second
opinion'**."

**The forward-looking suggestion, still unexploited:** EG's two parameters are stable enough that
"their estimated values could be **databased to establish norms** for future products or to serve as
**empirical priors for a Bayesian analysis**," potentially enabling forecasts with <12 weeks of data
(cf. Urban & Katz 1983 on ASSESSOR).

---

## 3. Fader, Hardie & Huang (2004) — the dynamic changepoint model

The most technically ambitious paper here, and the one that squarely addresses **why stationary models
fail for new products**.

### 3.1 The motivating failure

Fit Gupta's (1991) Erlang-2/gamma with covariates (see
[../purchasing/purchasing-summary.md](../purchasing/purchasing-summary.md) §2) to 26 weeks of "Kiwi Bubbles" data (a masked
shelf-stable juice drink, 2,799 IRI BehaviorScan panelists), forecast the remaining 26.

- **Sales:** tracks well in-sample, then "quickly (and significantly) veers away" — **week-52 forecast
  23% too high.** Interpretation: interpurchase times are *lengthening* as buyers gain experience.
- **Percent triers repeating:** actual and predicted "diverge quite drastically **even in the middle
  of the calibration period**."

That second failure is the important one — **aggregate sales tracking can look acceptable while the
model is badly wrong about the underlying process.** Always check a decomposed diagnostic.

They are scrupulous about attribution: *"To be fair to Gupta (1991), he made no claims that his
stationary models were suitable for new products."*

### 3.2 Why not just do trial/repeat separately?

Three named shortcomings of the classical decomposition:

- **Separation of stages.** "Does the evolution of buying patterns begin and end with the transition
  from the trial purchase to first repeat?" Some buyers go through several "retrial" cycles.
- **"Dependence" between stages.** Standard trial/repeat models retain only the *fact* of a trial
  purchase, not *when* it happened. But early triers are heavy category buyers, so given acceptance
  they should repeat *faster* than late triers. Ignoring this "is known to result in biased
  inferences" (Gupta & Morrison 1991).
- **Parsimony.** One integrated model needs fewer parameters — here **four** (plus covariates) — and
  gives cleaner diagnostics. Notably, the model tracks trial, first repeat, and additional repeat
  well **without an explicit separate model for each**.

### 3.3 The model

Standard changepoint framework: partition the observation sequence into contiguous blocks, with the
rate parameter constant within a block and redrawn at changepoints.

Let `γⱼ` = probability of a change in buying rate following the `j`th repeat purchase. Standard
product-partition models assume `γⱼ = γ` for all `j`. **The paper's novelty is letting `γⱼ` itself
evolve:**

```
γⱼ = 1 − ψ(1 − e^{−θ(j+1)}),      j = 0, 1, 2, …        ψ ∈ [0,1],  θ > 0     (4)

P(w) = ∏_{j∈w} γⱼ · ∏_{j∉w} (1 − γⱼ)                                          (3)
```

Baseline timing is exponential with proportional-hazards covariates:

```
S(tⱼ|t_{j−1}; λⱼ) = exp[−λⱼ B(tⱼ, t_{j−1})]                                   (1)
f(tⱼ|t_{j−1}; λⱼ) = λⱼ A(τⱼ) exp[−λⱼ B(tⱼ, t_{j−1})]                          (2)
```

with `λ ~ gamma(r, α)`. **At a changepoint the consumer draws a new rate independently from the same
gamma** — Howard's (1965) "dynamic inference" principle, also used by Sabavala & Morrison (1981).

The likelihood is a **partition-probability-weighted average** over all `2^K` possible partitions of a
`K`-purchase sequence:

```
L(T_h) = Σ_s  L(T_h | w_s) · P(w_s)                                          (10)
```

(A computational note: evaluating all `2^K` partitions gets expensive; the appendix gives a method to
reduce this.)

### 3.4 The nesting structure — this is what makes the paper valuable

| Constraint | Resulting model |
|---|---|
| `γⱼ = 0 ∀j` (`θ → ∞`, `ψ = 1`) | **Gupta (1991) exp/gamma with covariates** |
| ...plus `β = 0` | **exponential-gamma** — the timing counterpart of the **NBD**; `r, α` equal the NBD fit |
| `θ → ∞` (γ constant) | **static changepoint model** |
| `ψ = 1`, `θ` finite | `γⱼ → 0`: **nonstationary → stationary transition** as the product becomes established |
| `ψ < 1` | `γⱼ → 1 − ψ > 0`: **permanent nonstationarity** |

The `ψ = 1` case is the conceptual payoff: the model *"is consistent with the notion of nonstationary
buying behavior during the early stages of a new product's life and **stationary buying behavior — as
characterized by the NBD model — once it has become established**."* It formalizes the boundary
between this literature and the Ehrenberg stationary-NBD tradition.

The `ψ < 1` case captures **"leakage" of repeat buyers** (East & Hammond 1996). And note how dropout
emerges rather than being assumed: if the gamma has an effective mode at zero (`r < 1`), a consumer
who redraws a very small `λ` has "an almost zero probability of making a repeat purchase in the
foreseeable future," thereby **"dropping out."** Hence:

> "Other researchers (e.g., Schmittlein et al. 1987) have proposed NBD-based models that incorporate a
> 'death' process. However our model is **far more flexible**, allowing for other forms of
> nonstationarity (e.g., 'speeding up' and 'slowing down' of later purchase rates) beyond a simple
> 'death' process."

### 3.5 Results — Kiwi Bubbles, 12 model specifications

Twelve models = {exponential, Erlang-2} × {no covariates, covariates} × {no / static / dynamic
changepoint}. Calibrated on 26 weeks.

| Model | Baseline | Cov | Changepoint | LL | r | α | ψ | θ |
|---|---|---|---|---|---|---|---|---|
| 1 | Exp | N | None | −3812.40 | .079 | 71.375 | (1) | (∞) |
| 2 | Exp | N | Static | −3779.19 | .049 | 26.797 | .750 | (∞) |
| 3 | Exp | N | Dynamic | −3771.98 | .047 | 24.057 | .851 | 1.144 |
| 4 | Exp | Y | None | −3733.00 | .076 | 138.239 | (1) | (∞) |
| 5 | Exp | Y | Static | −3731.28 | .066 | 97.661 | .912 | (∞) |
| **6** | **Exp** | **Y** | **Dynamic** | **−3726.56** | .061 | 80.228 | .966 | 1.367 |
| 7–12 | Erlang-2 | … | … | −3973 … −3747 | | | | |

**The exponential strictly dominates Erlang-2 at every specification** — contrary to Gupta (1991) but
"consistent with recent work on the modeling of trial purchasing for new grocery products" (i.e.
paper 2 above, and Hardie et al. 1998).

**The estimated changepoint probabilities are interpretable and behaviourally sensible** (Model 6):

- **28% chance of changing your buying rate after the trial purchase** — "entirely consistent with the
  widely held view that trial purchases are different from repeat purchases and that **trial rates are
  a poor predictor of repeat buying**."
- **10% after the first repeat.**
- Levelling off at `1 − ψ = 3.5%`.

**Forecasting (26-week holdout):**

| Model | Wk52 Index | MAPE-Tot | MAPE-TR | MAPE-FR | MAPE-AR |
|---|---|---|---|---|---|
| 1 Exp, no cov, no CP | 130.7 | 17.0 | 6.2 | 34.4 | 23.2 |
| 4 Exp, cov, no CP *(= Gupta)* | 112.7 | 5.4 | 2.1 | 22.2 | 7.1 |
| 5 Exp, cov, static CP | 104.9 | 2.5 | 2.0 | 21.7 | 5.0 |
| **6 Exp, cov, dynamic CP** | **104.7** | **2.6** | **2.0** | **4.1** | **4.3** |
| 10 Erlang-2, cov, no CP | 123.3 | 13.6 | 2.5 | 32.3 | 18.6 |

**Read the columns, not the total.** On MAPE-Tot, Models 5 and 6 are indistinguishable. The dynamic
changepoint's advantage shows up **entirely in the repeat components** — MAPE-FR drops from 21.7 to
**4.1**. This is precisely the "aggregate fit hides process error" point from §3.1, now in reverse.

Their emphasis on *additional repeat*: even though its level is low at week 26, "it is evident that
additional repeat will quickly bypass the other sales components, and will comprise the lion's share
of total sales in the period following Week 52. The ability of our model to accurately track and
forecast this key component is, perhaps, **the strongest indicator of its validity**."

And the methodological warning: *"it is dangerous to assess a forecasting model in terms of
calibration-period fit, as the absence of a positive link between a model's calibration (in-sample)
fit and out-of-sample forecasting performance is well known"* (Armstrong 2001).

**Sales are generated by simulation**, not closed form. Cumulative trial has one:

```
E[T(t)] = H · [ 1 − (α/(α + B(t,0)))^r ]
```

but `R(t)` and `S(t)` do not, so they simulate each panelist's purchase sequence (draw λ, simulate an
interpurchase time, flip for a changepoint, redraw λ if so, repeat) and **average over ~100 runs**.

---

## 4. Fader & Hardie (2004) — ART Forum tutorial

A 56-slide teaching version tying the trial/depth-of-repeat machinery to customer-base analysis. The
practical entry point: it is the source of the four Excel workbooks and hence of
[`models/acquisition/depth-of-repeat`](../../../notebooks/models/acquisition/).

**Part 1 — new product trial and repeat.**

The trial model derived from a **two-segment story**, which is a cleaner exposition than paper 2's `p`
parameter:

| Segment | Size | λ_T |
|---|---|---|
| ever triers | `p₀` | `θ_T` |
| never triers | `1 − p₀` | 0 |

```
P(trial by t) = p₀·F(t|λ_T=θ_T) + (1−p₀)·F(t|λ_T=0) = p₀(1 − e^{−θ_T t})
T(t) = N · P(trial by t)
```

Justified from the empirical regularity that cumulative penetration curves "increase at a decreasing
rate towards a penetration limit < 100%," shown across products E, F, G, K, M, N.

**Depth of repeat**, with the recursion made explicit:

```
Rⱼ(t) = Σ_{t_{j−1}}  P(jth repeat by t | (j−1)th repeat at t_{j−1})
                     × [ R_{j−1}(t_{j−1}) − R_{j−1}(t_{j−1}−1) ]
```

**The stated challenges** — which is exactly why Eskin's parameter-stability assumptions matter:

- sparse data for higher orders of repeat (`j = 3, 4, 5`);
- **no data at all** for the repeat levels you'll observe in the forecast period.

Hence: "Are there common patterns across depth-of-repeat levels that we can exploit?" The
depth-of-repeat curves plot answers yes — same shape, rising asymptote in `j`. So:

```
P(jth repeat by t | (j−1)th repeat at t_{j−1}) = pⱼ(1 − e^{−θ_AR(t − t_{j−1})})

pⱼ = p_∞ (1 − e^{−γj}),   j ≥ 2
```

Fitted by **SSE minimization in Excel** — worked example: `p_∞ = 0.7816, γ = 1.0014, θ_AR = 0.2309`,
giving `p₂ = 0.676, p₃ = 0.743, p₄ = 0.767, p₅ = 0.776`. The slides show the actual spreadsheet
formulas and the eligibility/triangular-table layout, matching Eskin's `RI` structure.

**Part 2** shifts to customer-base analysis proper — NBD, Pareto/NBD, BG/NBD, conditional expectations
— i.e. the material in [../foundations/foundations-summary.md](../foundations/foundations-summary.md) and
[../spend-clv/spend-clv-summary.md](../spend-clv/spend-clv-summary.md), taught in spreadsheet form.

---

## How these map onto the repo

- **Paper 4 + the `.xls` files are the direct source for
  [`models/acquisition/depth-of-repeat`](../../../notebooks/models/acquisition/)**; Eskin (paper 1)
  is its intellectual ancestor and supplies the `R_t(J)` / `RI_{it}(J)` notation.
- **Paper 3 is the source for
  [`models/acquisition/dynamic-changepoint-new-product`](../../../notebooks/models/acquisition/)** —
  the Kiwi Bubbles dataset lives in `data/`.
- **Paper 2 is not currently reflected in any essay** and is the most obviously reusable: the
  eight-model factorial, the 1,760-fit calibration-length sweep, and the **indexed parameter-stability
  plot** would make a strong standalone essay on *model-component selection*, and the technique
  generalizes to every model in the repo.
- **Paper 3 §3.4's nesting table** is the cleanest available bridge between the Fader–Hardie and
  Ehrenberg traditions: `ψ = 1, θ finite` says a new product's buying process **converges to the
  stationary NBD** as it becomes established. That is precisely the regime the Ehrenberg work
  ([Repeat-Buying summary](../brand-choice/repeat-buying-summary.md)) assumes, and
  it explains why Ehrenberg is explicit that his models fail for new products.
- **Three independent demonstrations of misspecification-absorption** now exist in this corpus
  (Erlang-5 for a bad component; inventory for a missing dead-period; EG's `r` inflating 50× to soak
  up unmodelled promotion). Worth collecting into one methodological note.
- **Paper 3 §3.1 and §3.5's decomposed MAPE** make the case for *always* validating on decomposed
  diagnostics (percent triers repeating, repeats per repeater, trial/first-repeat/additional-repeat)
  rather than aggregate sales — a habit the repo's other essays could adopt.
- **Paper 2's unexploited suggestion** — databasing stable EG parameters as **empirical priors across
  product launches** — is a natural fit for the repo's Stan/BridgeStan infrastructure.
