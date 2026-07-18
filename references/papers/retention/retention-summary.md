# `retention/` — reading summary

One paper, but a load-bearing one: it is the canonical demonstration that **a 2-parameter
probability model with a behavioural story beats flexible curve-fitting**, and the cleanest published
statement of the sorting-effect argument.

| Work | Year | Length |
|---|---|---|
| Fader & Hardie, **"How to Project Customer Retention"**, *Journal of Interactive Marketing* 21 (Winter), 76–90 | 2007 | 15 pp. incl. two appendices |

Mirrored by [`models/retention/beta-geometric`](../../../notebooks/models/retention/) and
`sBG-Model.py`. Appendix B is a **complete cell-by-cell Excel recipe** — the source of the
spreadsheet implementations in `excel-models/`.

---

## 1. The setup: why you need to *project* the survivor function

**Definitions.** Retention rate `r_t` = proportion active at end of period `t−1` still active at end
of `t`. (Footnoted pedantry worth keeping: *"Strictly speaking, we should talk of retention and churn
**probabilities**, not rates."*)

```
S(t) = r₁ · r₂ · … · r_t = ∏_{i=1}^{t} rᵢ           (1)
r_t  = S(t) / S(t−1)                                 (2)
expected tenure = Σ_{t≥0} S(t)                       (area under the survivor function)
```

**The CLV correction.** The textbook formula with a constant retention rate `r`,

```
E(CLV) = Σ_t  m · [∏_{i=1}^{t} rᵢ] · (1/(1+d))^t
```

should be written in terms of the survivor function directly, which *"(correctly) reflects the
phenomenon of nonconstant retention rates"*:

```
E(CLV) = Σ_{t≥0}  m · S(t) / (1 + d)^t
```

**The truncation problem — the actual motivation.** With 5 years of data you can compute `Ŝ(1)…Ŝ(5)`
and hence expected tenure *over those 5 years*. But that **underestimates** true expected tenure and
CLV, "as we would be ignoring the remaining life of those customers who are active at the end of Year
5." You need `Ŝ(6), Ŝ(7), …`. The same projection is required for **residual** tenure/value of a
customer already 3 years in.

## 2. The straw man that isn't a straw man: "parametric approaches do not work"

Berry & Linoff's *Data Mining Techniques* (2004, ch. 12) has a sidebar literally titled **"Parametric
approaches do not work."** Fader & Hardie replicate it, using two customer segments ("Regular" and
"High End") observed over 12 years, calibrating on the first 7.

Observed survival (Table 1):

| Year | Regular | High End |
|---|---|---|
| 0 | 100.0 | 100.0 |
| 1 | 63.1 | 86.9 |
| 2 | 46.8 | 74.3 |
| 3 | 38.2 | 65.3 |
| 4 | 32.6 | 59.3 |
| 5 | 28.9 | 55.1 |
| 6 | 26.2 | 51.7 |
| 7 | 24.1 | 49.1 |
| 8 | 22.3 | 46.8 |
| 9 | 20.7 | 44.5 |
| 10 | 19.4 | 42.7 |
| 11 | 18.3 | 40.9 |
| 12 | 17.3 | 39.4 |

**High End regressions** (calibrated on years 0–7):

```
Linear        y = 0.925 − 0.071t              R² = 0.922
Quadratic     y = 0.997 − 0.142t + 0.010t²    R² = 0.998
Exponential   ln(y) = −0.062 − 0.102t         R² = 0.963
```

**Year-12 errors:** linear **−81%**, exponential **−30%**, quadratic **+92%**.

**Regular segment:**

```
Linear        y = 0.773 − 0.092t              R² = 0.776
Quadratic     y = 0.930 − 0.249t + 0.022t²    R² = 0.960
Exponential   ln(y) = −0.248 − 0.190t         R² = 0.915
```

Exponential *looks* fine on the plot but **underestimates Year-12 survival by 54%** — "not an
acceptable range of error." A useful reminder that eyeballing a fitted curve hides extrapolation error.

**The two failure modes, and note they are different:**

1. **Accuracy** — R² of 0.998 in-sample, 92% error out-of-sample. High in-sample fit is no guarantee
   whatsoever of extrapolation quality. This is the single most quotable result in the paper.
2. **Logical consistency** — the linear model gives `S(t) = 0` after year 14 and negative thereafter;
   the quadratic model's survivor function **starts increasing**, which is impossible. A survivor
   function is constrained to be monotone-decreasing on [0,1] and unconstrained regressions don't know
   that.

> "Of course, we could try out different arbitrary functions of time, but this would be a pure
> curve-fitting exercise at its worst. Furthermore, it is hard to imagine that there would be any
> underlying **rationale** for the equation(s) that we might settle upon."

## 3. The sBG model

**The story**, stated as a "paramorphic representation" (i.e. an *as-if* description, not a literal
claim about cognition):

- At the end of each period, a customer flips a coin: heads → cancel, tails → renew.
- For a given individual, P(heads) **does not change over time**.
- P(heads) **varies across customers**.

They pre-empt the objection to assumption 2 — that retention "should" rise with experience — with the
parsimony rule: *"rather than overcomplicate our story, we start with the simplest possible set of
assumptions and only add supposedly richer 'touches of reality' if the model does not work. As seen
shortly, **no additional assumptions will be required**."*

**Formally:**

```
Individual:   P(T = t | θ) = θ(1 − θ)^{t−1}        t = 1, 2, 3, …   (shifted geometric)
              S(t | θ)     = (1 − θ)^t

Heterogeneity: f(θ | α, β) = θ^{α−1}(1 − θ)^{β−1} / B(α, β)        α, β > 0
```

Mixing gives the **shifted-beta-geometric (sBG)**:

```
P(T = t | α, β) = B(α + 1, β + t − 1) / B(α, β)        (5)
S(t | α, β)     = B(α, β + t) / B(α, β)                (6)
```

**The beta shape taxonomy** (their Fig. 3) — useful as a manager-facing diagnostic:

| α, β | Shape | Interpretation |
|---|---|---|
| both < 1 | **U-shaped** | highly polarized — customers are either very loyal or very flighty |
| both > 1 | interior mode | fairly homogeneous churn probabilities |
| α < 1, β > 1 | **reverse-J** | most customers low-churn, a sizeable high-churn tail |
| α > 1, β < 1 | **J-shaped** | most customers high-churn |

### 3.1 The two computational shortcuts (why this fits in a spreadsheet)

You never need to evaluate a beta function. **Forward recursion:**

```
P(T = 1) = α / (α + β)
P(T = t) = [ (β + t − 2) / (α + β + t − 1) ] · P(T = t − 1),    t = 2, 3, …    (7)
```

**Closed-form aggregate retention rate** — substitute (6) into (2) and simplify:

```
r_t = (β + t − 1) / (α + β + t − 1)                                            (8)
```

Both derived step-by-step in Appendix A using only the beta–gamma identity `B(α,β) = Γ(α)Γ(β)/Γ(α+β)`
and the recursion `Γ(x+1)/Γ(x) = x`.

### 3.2 The central result

Look at (8): `r_t` is **increasing in `t`** — approaching 1 as `t → ∞` — even though every individual
has a *constant* retention probability `1 − θ`.

> "There are **no underlying time dynamics at the level of the individual customer**; the observed
> phenomenon of retention rates increasing over time is simply due to heterogeneity (i.e., the
> high-churn customers drop out early in the observation period, with the remaining customers having
> lower churn probabilities). This well-known **'ruse of heterogeneity'** (Vaupel & Yashin, 1985) is
> often overlooked by those attempting to make sense of various aggregate patterns of customer
> behavior."

This is the repo's "heterogeneity, not individual dynamics" principle in its original citation. Note
the source is demography (Vaupel & Yashin 1985, *The American Statistician*), not marketing.

## 4. Results

Fitted on years 1–7 only:

| Segment | α̂ | β̂ | E(θ) = α/(α+β) |
|---|---|---|---|
| High End | 0.668 † | 3.806 | **0.15** |
| Regular | 0.704 | 1.182 | **0.37** |

† *Caution:* the body text reports `α̂ = 0.688` for High End while Appendix B's worked Solver run
reports `α = 0.668` (LL = −1611.2). Re-estimate rather than trusting either figure when implementing.

**Year-12 extrapolation error: +4% (High End), +2% (Regular)** — against −81%/+92%/−30% for the
regressions. *"The resulting predictions are almost too good to be true."*

Two further validations:

- **Retention rate by tenure tracks well**, which is the harder test: `r_t` "does not have to
  accumulate across periods as S(t) does, and therefore it is more sensitive to period-to-period
  variations." Some unexplained "blips" (Year 2, High End) but tracking holds through Year 12.
- **The mixing distributions are interpretable.** Both segments are **reverse-J-shaped**: most
  customers low-churn with "a sizeable subsegment within each one that will tend to depart very
  quickly." The Regular distribution sits further right (E(θ) = 0.37 vs 0.15). The authors' point:
  the *mean* difference is obvious from Figs. 4–5, but the plot of `f(θ)` "provides a better idea
  about the nature of these differences at a more fine-grained level."

And the implied warning: *"there is a fairly high degree of heterogeneity within each segment;
therefore, a model that does not take these cross-customer differences into account will not perform
very well, particularly in terms of out-of-sample forecasting."* Heterogeneity is not a nicety — it
is what makes the extrapolation work.

## 5. Limits to application — read before reusing this model

**The model is for exactly one of four quadrants: discrete-time + contractual.** The paper is
unusually blunt that readers skim past this:

> "Many readers will have glanced over the words 'discrete-time' and 'contractual' without reflecting
> on their significance; however, they are very important."

| Setting | Model to use instead |
|---|---|
| Discrete-time contractual | **sBG** (this paper) |
| Continuous-time contractual | **exponential-gamma** (= Lomax = Pareto Type II) |
| Continuous-time noncontractual | **Pareto/NBD**, **BG/NBD** |
| Discrete-time noncontractual | **BG/BB** |

**sBG is also the wrong tool for a different question.** For *"which customers are at risk next
period"*, logit/data-mining churn models with time-varying covariates (service calls, usage) are
appropriate. But — and this is the same argument as in
[../foundations/foundations-summary.md](../foundations/foundations-summary.md) §1.5 — those models "cannot easily be used to
address the problem of projecting the survivor function into the future, as **we do not have future
values of the time-varying covariates**." *"It is therefore important to use the right model for the
task at hand."*

## 6. Extensions and connections

**List falloff.** Buchanan & Morrison (1988) modeled the decline in response rate across successive
mailings to a prospect list under assumptions "similar to those behind the sBG": constant individual
response probability `p`, beta-distributed across the population. Framed as beta-binomial, but *"it
could have been derived as an sBG model"* — the mailing on which a prospect responds is
shifted-geometric. So `r_t` and `S(t)` have direct list-falloff analogues.

**Covariates.** Time-invariant ones enter by making α and β functions of descriptor variables — the
**beta-logistic** model (Heckman & Willis 1977; Rao & Steckel 1995). The methodological rule stated
here is worth carrying everywhere:

> "The key is to bring in all of these factors **at the right level**; that is, at the level of the
> latent parameter of interest (in this case, θ) instead of just 'jamming' different covariate effects
> into a regression-like model."

Though they immediately add that they "question the value of such an extension given our modeling
objective."

**Relaxing memorylessness.** Both shifted-geometric and exponential are memoryless. To allow genuine
individual-level duration dependence, swap in a Weibull:

- discrete time → **beta-discrete-Weibull (BdW)**, a generalization of sBG → mirrored by
  [`models/retention/beta-discrete-weibull`](../../../notebooks/models/retention/)
- continuous time → **Weibull-gamma (WG)**, a generalization of EG

**Multiple cohorts** — a genuinely practical problem, since cohorts are defined by acquisition time
and **every newer cohort has one less period of data**. Three options:

1. **Pool** and estimate one parameter set — the recommended starting point, if you believe each
   cohort realizes a common underlying process.
2. **Separate** per cohort — but the newest cohorts have the least data and least reliable estimates.
3. **Beta-logistic with cohort dummies.**

The "more elegant solution" they flag: add a **second layer of heterogeneity**, with α and β
themselves distributed across cohorts, fitted hierarchical-Bayes, so that "cohorts with fewer data
points [can] **borrow** information about the possible values of α and β from the earlier cohorts."
Their own data show real cross-cohort differences, so this is not hypothetical. (Schweidel, Fader &
Bradlow 2006 handle it in continuous time.)

## 7. Appendix B — the Excel implementation

The likelihood for a cohort of `n` customers observed 7 periods, with `n_t` lost in period `t`:

```
LL(α, β | data) = Σ_{t=1}^{7} n_t · ln P(T = t | α, β)
                  + (n − Σ_{t=1}^{7} n_t) · ln S(7 | α, β)
```

The final term is the **right-censoring** contribution from customers still active at the end — easy
to omit and the most common implementation bug.

Worked sample data (1,000 High End customers): active at end of years 1–7 = 869, 743, 653, 593, 551,
517, 491.

Key spreadsheet cells:
- `P(T=1)` → `=B1/(B1+B2)`
- `P(T=t)` → `=($B$2+A7-2)/($B$1+$B$2+A7-1)*B6`, filled down (the recursion (7))
- `S(1) = 1 − P(T=1)`; thereafter `S(t) = S(t−1) − P(T=t)`
- Solver: maximize LL by changing α, β subject to both ≥ 0.0001

**Their own advice on optimization hygiene**, which applies to every MLE in this repo: *"To be sure
that we actually have reached the maximum of the log-likelihood function, it is good practice to redo
the optimization process using a completely different set of starting values."* (Starting from 1.0,
1.0 gives LL = −2115.5; from 0.01, 0.01 gives LL = −2741.7; both should converge to LL = −1611.2.)

A subtle footnote on notation, worth preserving in teaching material: `P(data | α, β)` and
`L(α, β | data)` are numerically identical but conceptually opposite — the first is a function of the
data for fixed parameters, the second a function of the parameters for fixed data.

---

## How this maps onto the repo

- **Source paper for [`models/retention/beta-geometric`](../../../notebooks/models/retention/)** and
  the marimo `sBG-Model.py` app; Appendix B is the Excel model.
- **§2 is the best available argument for the whole repo's approach** — a concrete, replicable case
  where R² = 0.998 in-sample yields +92% error out-of-sample. Worth putting early in `index.qmd` or
  the landing exposition.
- **§3.2 (`r_t = (β+t−1)/(α+β+t−1)` rising while individual θ is constant)** is the mathematical core
  of the "ruse of heterogeneity" claim in `CLAUDE.md`. Cite Vaupel & Yashin (1985) for the phrase.
- **§6's multiple-cohort discussion** is the natural bridge to
  [`models/retention/subscription-retention`](../../../notebooks/models/retention/) and to the
  cohort machinery in [../valuation/valuation-summary.md](../valuation/valuation-summary.md) — CBCV models must handle
  many cohorts of unequal maturity, and the hierarchical-Bayes "borrowing" idea is how.
- **§5's quadrant table** duplicates [../foundations/foundations-summary.md](../foundations/foundations-summary.md) §1.2;
  the addition here is the explicit *"use the right model for the task"* separation between
  **projecting** retention (probability model) and **predicting who churns next** (covariate model).
- The **beta-shape taxonomy** (§3) is a good candidate for an interactive figure — it is currently
  the clearest manager-facing output the sBG produces beyond the forecast itself.
