# `purchasing/` — reading summary

Two papers on **counting/timing models for repeat purchasing**, and they sit on opposite sides of a
methodological argument. Fader & Hardie show a 3-parameter spreadsheet model beating a rich
integrated one; Gupta shows how to bolt time-varying marketing covariates onto the same family.
Read together they bracket the "how much texture does the model need?" question.

| # | Work | Year | Length |
|---|---|---|---|
| 1 | Fader & Hardie, **"A note on an integrated model of customer buying behavior"**, *European Journal of Operational Research* 139, 682–687 | 2002 | 6 pp. |
| 2 | Sunil Gupta, **"Stochastic Models of Interpurchase Time with Time-Dependent Covariates"**, *Journal of Marketing Research* 28 (Feb), 1–15 | 1991 | 15 pp. |

Supporting files: `integrated-model-nbd-otb/nbd_otb.xls` — Hardie's own spreadsheet implementation of
paper 1's analysis (also at brucehardie.com/pmnotes.html). Mirrored by the
[`models/purchasing/nbd-otb`](../../../notebooks/models/purchasing/) essay.

---

## 1. Fader & Hardie (2002) — the **NBD/OTB** model

A "Short Communication" written as a rebuttal to Wu & Chen (2000), who built an integrated model
compounding **in-store decisions + interpurchase-time regularity + repeat buying + attrition +
in-store marketing conditions**, applied it to tea purchase data, and beat a set of benchmarks.

Fader & Hardie's counter: a **three-parameter** model, estimable "entirely within a standard
spreadsheet environment," fits the same data **better** and answers the managerial questions Wu &
Chen posed but never actually answered.

### 1.1 The model

The motivating observation: sometimes a dataset has "a larger-than-expected proportion of people
making one and only one purchase." Behavioural stories offered — *tourists who will never visit the
store again*, or people *"merely responding to a particular promotion but [with] no intent of ever
repurchasing."* Modeling these with a plain NBD is inappropriate because the NBD "does not allow for
buyers to come in and out of the sample in this manner."

Let ω be the unknown proportion who are **one-time buyers** (they buy once, then leave the market
forever); the remaining `1 − ω` are ordinary NBD buyers.

```
P(X = x) = ω·δ_{x,1} + (1 − ω)·P_NBD(X = x),     x = 0, 1, 2, …

P_NBD(X = x) = [Γ(r+x) / (Γ(r)·x!)] · (α/(α+1))^r · (1/(α+1))^x
```

`δ_{x,1}` is the Kronecker delta — a **spike at one**, not at zero. Moments:

```
E(X)   = ω + (1 − ω)·r/α
var(X) = (1 − ω)[r/α + r/α²] + ω(1 − ω)·(r − α)²/α²
```

Collapses to the NBD at `ω = 0`; at `ω = 1` gives `E(X) = 1, var(X) = 0`.

**Estimation.** Plain MLE on the frequency counts — `f_x` = number of individuals with `x` purchases:

```
LL(r, α, ω | data) = Σ_{x=0}^{x̄} f_x · ln P(X = x | r, α, ω),   subject to 0 ≤ ω ≤ 1
```

Note this needs **only the histogram**, which the authors flag as a deliberate virtue: Wu & Chen
published a frequency table but not the covariates needed to replicate their model, and *"many other
actual case studies also share a similar limitation in terms of data availability. A 'histogram-only'
model is a useful contribution."*

### 1.2 Two results worth carrying forward

**(a) The Period-2 connection — NBD/OTB becomes "NBD with spike-at-zero."** If Period 1 purchasing is
NBD/OTB with one-time-buyer fraction ω, then purchasing in a **non-overlapping Period 2** of the same
length follows Morrison's (1969) **NBD-with-spike-at-zero**, with ω as the spike size — because by
construction none of the Period-1 one-time buyers ever purchase again. A clean, testable
out-of-sample implication.

**(b) The conditional expectation, and why `x = 1` is special.** For `x ≠ 1` the customer is
demonstrably not a one-time buyer, so the standard NBD result applies: `E(X₂|X₁=x) = (r+x)/(α+1)`.
For `x = 1` the customer is *either* a one-time buyer (expect 0) *or* a regular buyer who happened to
buy once. By Bayes:

```
P(OTB | x = 1) = ω / [ ω + (1 − ω)·P_NBD(X = 1) ]
```

giving the full expression

```
E(X₂ | X₁ = x) = (r + x)/(α + 1) · { 1 −  ω·δ_{x,1} / [ ω + (1−ω)·(r/(α+1))·(α/(α+1))^r ] }
```

Plotted against `x`, this is **linear everywhere except at `x = 1`, where it dips sharply**. Against
the 45° line it shows classic **regression to the mean** — and the authors are careful to note that
apart from the `x = 1` group, regression is toward the mean of the **NBD** (`r/α`), *not* the mean of
the NBD/OTB.

### 1.3 The empirical result

Ten Ren tea, 1,366 specialty-store customers, 48 weeks, 4,788 total purchases.

| | NBD/OTB | NBD |
|---|---|---|
| r | 0.507 | 0.590 |
| α | 0.122 | 0.168 |
| ω | **0.203** | 0 (constrained) |
| LL | **−3077.7** | −3194.0 |

Goodness of fit (right-censored at `x = 19` so expected frequencies ≥ 5):

- **NBD/OTB: χ² = 24.8** vs critical `χ²₀.₀₅,₁₆ = 26.3` → **passes.**
- **Wu & Chen's integrated model: χ² = 51.6** vs critical `χ²₀.₀₅,₂ = 6.0` → **fails badly.**
- Theil's U: 0.0465 (NBD/OTB) vs 0.0649 (integrated).

> "These top-line results are nothing short of remarkable. The added complexity of the behavioral
> process put forth by those authors seems difficult to justify when such a capable alternative model
> is readily available."

**The managerial answers** Wu & Chen asked for but didn't deliver:

- Fraction buying at least once over `t` time units (1 unit = 48 weeks):
  `ω + (1 − ω)[1 − (α/(α+t))^r]`. Over 2 years (2.17 units): **81.9% buy at least once, 24.8% of
  them one-time buyers.**
- **The headline diagnostic:** 437 of 1,366 panelists (32.0%) were *observed* to buy exactly once,
  but `ω = 20.3%` are *truly* one-time buyers. So **over a third of the observed one-time buyers are
  still in the market** and will buy again. This is precisely the inference a descriptive tabulation
  cannot make.
- Ongoing sales: `4788 − 277 = 4511` purchases per 48-week period, ≈ 94 units/week.
- Also available "with such ease": a **Lorenz curve** for 80:20 concentration — connecting directly
  to [`analyses/estimating-purchasing-concentration`](../../../notebooks/analyses/).

### 1.4 The methodological argument (the real point of the paper)

On why the simple model won — a genuinely useful diagnostic hypothesis:

> Wu & Chen "go to great lengths to relax the typical assumption of memoryless exponential
> interpurchase times; they indicate that a more regular **Erlang-5** process is warranted by the
> data. Yet our results do not indicate the presence of any problems with the exponential assumption;
> **perhaps the added complexity of the Wu–Chen model forced the Erlang-5 structure to
> counterbalance the unforeseen effects of another component of their model.**"

That is: in a richly parameterized model, a misspecified component can be silently absorbed by
another component, and the fitted "finding" (regularity in timing) is an artifact. Compare the
parallel they draw to Bass, Krishnan & Jain (1994), who showed in a diffusion context that
**covariate information does not always improve fit**.

The stated stance, which is the repo's parsimony principle in its sharpest form:

> "The main point here is **not to encourage blind reliance on the NBD** and its various extensions,
> but to use such models to point out **which assumptions should be changed and which types of model
> components should be added**."

And an explicit disclaimer against over-generalizing their own model: *"we are not putting forth the
NBD/OTB model as a new framework that can (or should) be broadly applied to other sets of count
data... But whenever an analyst has any reason to believe, a priori, that such a phenomenon might
exist, then this model is worth considering as a very logical starting point."*

Also: they concede in-sample fit is a weak test, and that comparing to a genuine future period "would
provide a much more rigorous test of its suitability than merely examining in-sample fit statistics,
as we (and Wu and Chen) have done."

**A footnote worth knowing.** A behaviourally richer alternative — "natives" (NBD) of size `p` and
"tourists" of size `1 − p` who buy with probability `c` while in market — turns out to be
**empirically indistinguishable from NBD/OTB** (`ĉ = 1`). Don't bother building it.

---

## 2. Gupta (1991) — interpurchase-time models with time-dependent covariates

The complement: how to put marketing variables into NBD-type models **without abandoning the
tradition**. Motivated by Morrison & Schmittlein's (1988) own verdict: *"Probably the most important
area for future research with NBD-type models involves incorporating the effect of marketing
variables."*

### 2.1 The four base models

Individual interpurchase time is exponential or Erlang-2; heterogeneity in rate λ via gamma(r, α).

```
Exponential:   f(t) = λ exp(−λt)              S(t) = exp(−λt)
Erlang-2:      f(t) = λ²t exp(−λt)            S(t) = (1 + λt) exp(−λt)
```

Erlang-2 is the time between **every other event** in a Poisson process — hence more "regular"
purchasing, and unlike the exponential its **mode is not at zero**, giving a built-in "dead period"
right after a purchase.

Likelihoods handle **right-censoring** explicitly (`t_ic` = censored time since last purchase, `t_is`
= sum of completed interpurchase times). Exponential-gamma for `N` consumers:

```
LL = Σᵢ [ r log α + Σ_{j=0}^{n_i −1} log(r + j) − (nᵢ + r) log(t_is + t_ic + α) ]
```

**A subtle and important warning about Pareto.** With one observation per consumer the likelihood is
the **Pareto** density (Schmittlein, Morrison & Colombo 1987). But with panel data — multiple spells
per consumer — *"using the density function of Pareto distribution to write the likelihood function
implies that we are capturing heterogeneity **across observations** instead of heterogeneity **across
consumers**."* The correct likelihood integrates once per consumer, not once per spell. Easy mistake
to make when reusing Pareto code on panel data.

### 2.2 Why covariates that vary over time need special care

Purchase rate becomes `λᵢ(t) = λᵢ₀ · exp(βXᵢₜ)` — a **nonhomogeneous Poisson process**: interpurchase
times are "neither independent nor identically distributed." The survivor function no longer
exponentiates a simple `λt`; it needs the **integrated hazard**:

```
Θ(t) = ∫₀ᵗ λ(τ) dτ ,      S(t) = exp[−Θ(t)] ,      f(t) = λ(t)·exp[−Θ(t)]
```

In practice covariates are piecewise-constant (weekly, in scanner data), so if the last purchase was
in week 1 and the current one in week `k`:

```
Θ_k(t) = λ₁d₁ + Σ_{w=2}^{k−1} λ_w + λ_k[ t − d₁ − γ(k−2) ],    γ = 0 if k = 1, else 1
```

i.e. **you must accumulate the covariate effect over every intervening week**, not just the week of
purchase. This is exactly the information the Cox partial-likelihood approach throws away — Gupta's
stated objection to it: *"if a consumer buys a product after k weeks, this approach uses the covariate
values of the kᵗʰ week only and ignores the covariates of (k − 1) weeks."*

The Erlang-2 version follows the same pattern with `f(t) = λ(t)·Θ(t)·exp[−Θ(t)]`.

**Nesting.** With `X = 0` all covariate expressions collapse exactly to the no-covariate ones, so
covariate models are nested and comparable by likelihood-ratio test. Non-nested comparisons (exp/gamma
vs Erlang-2/gamma) use **AIC = log-likelihood − #parameters** (Rust & Schmittlein 1985; note the
sign convention — *larger* AIC preferred here).

### 2.3 Why this approach rather than hazard models

Three claimed advantages over the parametric-hazard route (Flinn & Heckman 1982; Jain & Vilcassim 1990):

1. It's a **natural extension of NBD-type models** already trusted in marketing — "one need not
   abandon the very rich and useful approach applied in marketing over the last three decades."
2. **`r` is directly interpretable as heterogeneity.** Higher `r` → more homogeneous consumers. If
   heterogeneity is large, "it may be important to segment the market before interpreting parameter
   estimates."
3. **Closed-form likelihoods** — "it took less than five CPU minutes to estimate the model."

Alternatives dismissed, with reasons: linear regression on interpurchase time (Neslin, Henderson &
Quelch 1985) is **biased under right-censoring and time-varying covariates** (Helsen & Schmittlein
1989); buy/not-buy logit throws away exact purchase timing and struggles to include unobserved
heterogeneity — which is "conceptually similar to the omitted-variable problem" and **biases the
covariate estimates**.

### 2.4 Empirical application — ground coffee scanner panel

100 households, 40 calibration weeks + 25 holdout weeks. Covariates: household inventory (converted
from ounces to **weeks of supply**, clipped at 0 and 6 months), regular price, price cut, feature-and-
display, feature-or-display.

**Calibration results:**

| | Exponential | Erlang-2 | Exp/gamma | Erlang-2/gamma |
|---|---|---|---|---|
| r | — | — | 5.692 | **4.938** |
| Feature and display | 1.648 | 1.499 | 1.601 | 1.374 |
| Feature or display | 0.561 | 0.412 | 0.780 | 0.682 |
| Inventory | −0.068 | −0.040 | −0.075 | −0.037 |
| Price cut | 0.010 ns | 0.058 ns | −0.033 ns | −0.025 ns |
| Regular price | −0.034 ns | 0.005 ns | −0.089 ns | −0.014 ns |
| −LL | 2695.93 | 2725.83 | 2639.11 | **2556.68** |
| ρ² | .044 | .043 | .041 | .032 |

Purchase-rate elasticities (% change in λ per 1% change in covariate, at means):

| | Exponential | Erlang-2 | Exp/gamma | Erlang-2/gamma |
|---|---|---|---|---|
| Feature and display | .137 | .124 | .133 | .114 |
| Feature or display | .049 | .036 | .068 | .059 |
| **Inventory** | **−.408** | −.240 | **−.450** | −.222 |

**Four findings that matter more than the parameter table:**

1. **Inventory dominates promotion** — elasticities 2–3× those of feature/display.
2. **Price does nothing.** Neither price cut nor regular price is significant. Gupta's own earlier
   explanation, quoted: *"a consumer who is not planning to buy coffee in a given week may not check
   the prices or price discounts on coffee brands unless his or her attention is attracted to them
   through feature and/or display."* Dropping both variables didn't significantly hurt fit.
3. **The inventory elasticity is smaller under Erlang-2 — and this is a confound, not a finding.**
   The "dead period" (low purchase probability just after a purchase) is *built into* Erlang-2 via its
   non-zero mode; in the exponential model, **the inventory covariate is forced to absorb it**. Same
   structural lesson as Fader & Hardie's Erlang-5 remark: a covariate can be a proxy for a
   misspecified baseline.
4. **The feature×display synergy vanishes once heterogeneity is added.** Without heterogeneity,
   feature-and-display elasticity is >2× feature-or-display, suggesting synergy; with gamma
   heterogeneity the gap closes. *"This finding shows the importance of including heterogeneity."*

**And the honest caveat.** ρ² ≈ 5%: covariates explain very little of interpurchase-time variance —
consistent with Bucklin & Lattin (1990), Guadagni & Little (1987), Gupta (1988). Holdout Theil's U
ranges only 0.113–0.148 across all eight models; the best (Erlang-2/gamma with covariates) is *"only
marginally better than those of the competing models."*

Two acknowledged reasons the heterogeneity effect is muted: households making <10 purchases in two
years were **screened out**, which "eliminates the tail of the distribution, making the purchase rates
more homogeneous," hence the high fitted `r`. Defensible (those households were <1.5% of volume) but
it means `r` here is not a population estimate.

**A neat interpretive result on `r`:** Erlang-2/gamma always yields a **lower `r` than exp/gamma**
(4.938 vs 5.692 here). Total variance splits into within- and between-consumer components; Erlang-2
posits *less* within-consumer variance than exponential, so for the same total, **more** is attributed
to between-consumer heterogeneity → smaller `r`. So `r` is not comparable across timing
specifications.

---

## How these map onto the repo

- **Paper 1 is the source for [`models/purchasing/nbd-otb`](../../../notebooks/models/purchasing/)**,
  with `nbd_otb.xls` as the reference implementation. The `x = 1` Bayes split (§1.2b) and the
  20.3%-vs-32.0% diagnostic (§1.3) are the essay's payload.
- **The Period-2 spike-at-zero result (§1.2a)** is an untested-in-repo prediction and would make a
  strong holdout validation for that essay.
- **Paper 2 is the answer to "can I add marketing variables?"** — currently nothing in `notebooks/`
  does. The important, transferable content is §2.2: with time-varying covariates you need the
  **integrated hazard over all intervening periods**, and the naive approach (use the covariate at
  purchase week only) discards real information.
- **Two independent instances of the same failure mode** — Erlang-5 standing in for a misspecified
  component (§1.4), inventory standing in for the missing dead-period (§2.4.3). Worth stating
  explicitly wherever the repo argues for parsimony: complexity doesn't just cost degrees of freedom,
  it *relocates* misspecification into whichever parameter is flexible enough to absorb it.
- **Paper 2 §2.1's Pareto warning** is a live trap for anyone reusing Pareto/NBD machinery on
  multi-spell panel data.
- Contrast with the Ehrenberg tradition ([Repeat-Buying summary](../brand-choice/repeat-buying-summary.md)):
  Ehrenberg would not add covariates at all, and would read Gupta's ρ² ≈ 5% as confirmation that
  "nine hundred and ninety-nine of the thousand and one variables usually do not matter."
