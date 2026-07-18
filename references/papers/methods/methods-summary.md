# `methods/` — reading summary

One paper, and it is methodologically the most technically demanding in the corpus. It answers a
question the rest of the CBCV literature can't: **what if you have two data sources — one coarse but
representative, one granular but biased — and want to use both?**

| Work | Year | Length |
|---|---|---|
| McCarthy & Oblander, **"Scalable Data Fusion with Selection Correction: An Application to Customer Base Analysis"**, SSRN 3362595 | ~2019 | 75 pp. incl. web appendices |

Direct successor to [../valuation/valuation-summary.md](../valuation/valuation-summary.md) papers 3–4 (McCarthy, Fader &
Hardie 2017; McCarthy & Fader 2018) — same author, same CBCV problem, but relaxing the constraint
that only public aggregate disclosures are available.

---

## 1. The problem

**Two data sources, complementary defects:**

| | Aggregate "macro" data | Disaggregate "micro" panel |
|---|---|---|
| Coverage | representative of the whole population | a **possibly non-representative** subsample |
| Granularity | summary statistics only | full individual-level histories |
| Weakness | weak identification, limited model richness | **selection bias**, no external validity |

The motivating context is the explosion of third-party data: ProgrammableWeb lists ~23,000 APIs;
beyond the familiar Kantar/Comscore/Nielsen/IRI panels there are now credit-card panels (Second
Measure), geolocation (PlaceIQ, Mogean), clickstream (Jumpshot), email receipts (Rakuten Intelligence).

**What existing methods can't do.** Prior aggregate–disaggregate fusion work (Feit et al. 2013;
building on Chen & Yang 2007; and in economics Berry et al. 2004; in transportation Dias et al. 2019)
"assume that there is no selection bias in the disaggregate data, do not scale to large populations,
and/or require potentially arbitrary aggregation of granular data into summary statistics." This
paper's contribution is to fix all three at once.

### 1.1 An unusually honest scope section

§1.1 is worth reading on its own as a model of how to state boundary conditions. The method
introduces "the ancillary problem of estimating a model of selection into the disaggregate data" — a
trade-off between the information the panel adds and the estimation variance the selection model
introduces. So it is **not** beneficial when:

- selection bias is severe,
- the disaggregate sample is small,
- **or the aggregate data is already rich enough to identify the model on its own.**

It is most useful "in cases where models would only be **weakly identified** through aggregate data
alone, and where the disaggregate data is at least somewhat representative."

And they decline to oversell: *"while our proposed method may improve identification relatively
speaking, it does not guarantee strong identification in an absolute sense — indeed, in our empirical
application... model performance improves when incorporating disaggregate data, but the resulting
standard errors **can still be large**."*

Also explicitly out of scope: **macro models** (e.g. time-series models of aggregate data). The method
is for estimating an *individual-level* model.

---

## 2. The two CBCV gaps it fills

Stated as research gaps, but really they are limitations of every paper in
[../valuation/](../valuation/):

1. **Data range.** All prior CBCV uses only company-disclosed aggregates. This limits model richness
   *and* "limits analyses to firms that **voluntarily disclose** customer metrics on a regular basis,
   because public customer data disclosure is not mandatory."
2. **Repeat acquisition and churn.** No prior paper separately models *initial* vs *repeat* behaviour,
   "because the resulting models would be difficult to identify from aggregated data alone."

Gap 2 matters more than it sounds:

> "As a company matures and the composition of its customer base shifts towards **reacquired**
> customers, its overall retention curve will shift from its initial retention curve to its repeat
> retention curve."

So a model that conflates them will systematically mis-forecast a maturing firm. The Spotify finding
below is the payoff: **Spotify's repeat retention curve is significantly higher than its initial
retention curve**, implying retention *improves* as Spotify matures — invisible to any prior model.

---

## 3. The model

### 3.1 Four processes

Initial acquisition (IA) → initial churn (IC) → **repeat acquisition (RA)** → repeat churn (RC), each
a **Weibull-baseline proportional hazards** model discretized to months:

```
S(m | λ, c, β, x_{1:m}) = exp(−λ · B(m | c, β, x_{1:m}))                       (1)

B(m | c, β, x_{1:m}) = Σ_{t=1}^{m} [t^c − (t−1)^c] · exp(β′x_t)                (2)
```

With **Bernoulli gates** `π^(IA)` and `π^(RA)` determining whether an individual is *ever*
(re-)acquired at all — the split-hazard "never-acquirer" structure carried over from
[../valuation/valuation-summary.md](../valuation/valuation-summary.md) §3.4.

### 3.2 Correlated heterogeneity — the key modeling departure

The obvious choice is four **independent gammas** (conjugate with Weibull, as in Schweidel et al.
2008b). They reject it for a substantive reason:

> "A positive correlation between `λ^(IA)` and `λ^(IC)` would indicate that **early adopters also tend
> to be early abandoners** — a pattern which cannot be captured by independent gamma distributions."

So instead, **multivariate lognormal**:

```
log(λ_i) ~ N(log(λ₀), Σ_λ),      λ_i = (λ_i^(IA), λ_i^(IC), λ_i^(RA), λ_i^(RC))′        (3)
```

Conjugacy is sacrificed for the ability to estimate the correlation structure. A footnote adds a
restraint worth noting: it would be tempting to enrich `λ_i` further (e.g. letting parameters evolve
over time), "however, these extensions are likely to be **confounded with existing sources of
dynamics**, which could hurt performance due to poor identification." Same misspecification-absorption
concern that runs through [../purchasing/purchasing-summary.md](../purchasing/purchasing-summary.md) and
[../new-product/new-product-summary.md](../new-product/new-product-summary.md).

### 3.3 The selection model

Selection into the panel is `P(Z_i = 1 | ξ_i) = f(ξ_i)` for unobserved characteristics `ξ_i`. If
`ξ_i` and outcomes `Y_i` are dependent, selection is **non-ignorable** and must be corrected.

**The identifying assumption:** `ξ_i ⊥⊥ Y_i | λ_i`. Justified by *timing* — "by definition, selection
occurs **before** any granular behavior is observed in the panel." Concretely: wealthier customers may
be more likely to be in a credit-card panel *and* more likely to sign up for Spotify, but "their
selection is not based on whether they **actually** sign up."

This licenses a reduced-form selection model on the latent parameters:

```
P(Z_i = 1 | λ_i) = Logit⁻¹( β₀^(Z) + β^(Z)′ log(λ_i) )                                  (4)
```

which "controls for selection bias by **indirectly** controlling for dependency between `ξ_i` and
`Y_i`." The coefficients are directly interpretable — they tell you whether panel members are more or
less churn-prone than the population.

**Why this is identifiable at all** (the neat part): you have *two* views of `Y_i` — a possibly
contaminated panel and representative aggregates. *"Identifying the selection mechanism amounts to
identifying the **discrepancies** between the panel and aggregate data in the periods they overlap."*

Precedent cited: Manchanda et al. (2004), Van Diepen et al. (2009), Schweidel & Knox (2013) on
non-random direct-marketing targeting; Schweidel & Moe (2014) on self-selection into posting platforms.

---

## 4. Maximum proxy likelihood — the methodological contribution

### 4.1 Why the exact likelihood is infeasible

```
ℓ(θ | z, ỹ, d) = Σ_i log P_θ(Z_i = z_i)                    ← selection outcomes
               + Σ_{i: z_i=1} log P_θ(Ỹ_i = ỹ_i | Z_i = z_i)  ← panel data
               + log P_θ(D_N = d | Z_{1:N}, Ỹ_{1:N})          ← aggregate data          (8)
```

The first two terms are easy. **The third requires an `N`-fold convolution over `Y_{1:N}`** and is
intractable.

Note the two conditionings, both deliberate: conditioning on `Z_i` accounts for selection;
conditioning on `Ỹ_i` stops the aggregate term from **double-counting** panel members (who otherwise
contribute once directly and again through their share of the aggregates).

### 4.2 Why the alternatives fail

| Approach | Problem |
|---|---|
| **Moment methods / NLS** (as in all prior CBCV: GLS 2004, MFH 2017, McCarthy & Fader 2018) | Requires summarizing the granular data into moments. "Only relatively simple models admit sufficient statistics that allow summarization **without information loss**," and choosing which moments is arbitrary. |
| **Bayesian imputation** (Feit et al. 2013) | Impute a `Y_i` for **all N** population members; accept only if simulated aggregates equal observed. With high-dimensional `d` there are many equality constraints → low acceptance, poor mixing. Here `N` is **six orders of magnitude larger** than in Feit et al. |
| **Subsampling to regain scalability** (Musalem et al. 2009) | Statistically wasteful — "scaling down the aggregate data by 1,000 times would result in standard errors that are **√1000 ≈ 31.6 times larger**." |

### 4.3 The approximation

`D_N` is an aggregation of a linear transformation of `N` individual outcomes. By the **central limit
theorem**, its distribution is asymptotically normal. So replace the intractable third term with a
multivariate normal log-density:

```
µ_N(θ) = E_θ[D_N | z, ỹ]          Σ_N(θ) = Var_θ[D_N | z, ỹ]                            (9)
```

Since `Σ_N` is `q × q` and scales **quadratically** in the dimension of `D_N`, while `µ_N` scales
**linearly**, they fix the covariance at some positive-definite `Σ̂_N` rather than updating it:

```
ℓ̃_N(θ | Σ̂_N) = Σ_i log P_θ(Z_i = z_i)  +  Σ_{i: z_i=1} log P_θ(Ỹ_i = ỹ_i | Z_i = z_i)
                −  ½ (d − µ_N(θ))′ Σ̂_N⁻¹ (d − µ_N(θ))                                   (10)
```

**Two useful readings of that third term.** As a normal log-likelihood, or as **a quadratic form in
moment conditions — i.e. the GMM objective** (Hansen 1982), up to normalization by `N`. The
distinction from standard GMM: a typical moment estimator uses *unconditional* moments; here they are
conditioned on the panel data to avoid double-counting.

**Asymptotic properties:** consistency and asymptotic normality require only CLT regularity
conditions. Under stronger local-limit conditions (Bhattacharya & Rao 1986) the approximation is
asymptotically *exact*. And the estimator "retains favorable statistical properties even when only the
first moment is computable."

The aggregate data can be **any asymptotically normal summary statistic** — sample moments (CLT),
nonlinear transformations of them (delta method), or sample quantiles.

---

## 5. The Spotify application

**Two data sources:**

- **Aggregate:** Spotify (NYSE: SPOT) `END` and `LOSS` disclosures from SEC filings and investor
  presentations. Badly censored — commercial operations began **October 2008**, but END was disclosed
  only *intermittently* from Q1 2011, *quarterly* from Q1 2015, and LOSS quarterly only from Q4 2015.
  Calibration runs to Q3 2018 (`M = 120` months).
- **Disaggregate:** a **Second Measure credit-card panel** — monthly transactions for **3,003,746**
  panel members, Jan 2015 (`m* = 75`) to Sept 2018, of whom **289,541** were acquired as Spotify
  premium subscribers during the window.

Population = **world population** (Spotify has operated globally since 2011); unit = individual person.
Covariates = quarterly seasonal dummies in all four sub-models.

Estimation: R's `nlm` (Newton-type), initialized from `DEoptim` (evolutionary algorithm) "so that our
starting parameter values for nlm were in a better part of the parameter space."

### 5.1 The rolling holdout — a well-designed experiment

Data availability is varied on **two dimensions**: aggregate data (all / END only / none) × panel data
(yes / no), giving five non-degenerate scenarios, benchmarked against GLS, SSW, and MFH — all three
**enhanced with the same seasonal dummies** so no model is penalized for missing seasonality.

Seven calibration periods (`M = 99, 102, …, 117`), up to six quarters ahead, 81 rolling predictions.

**Average holdout MAPE:**

| Model | Aggregate | Panel | ADD | LOSS | END |
|---|---|---|---|---|---|
| GLS | All | No | 23.4% | 31.0% | 22.1% |
| SSW | All | No | 25.3% | 24.3% | 6.7% |
| MFH | All | No | 14.4% | **8.9%** | 7.1% |
| Proposed | **None** | Yes | **481%** | **628%** | **860%** |
| Proposed | END only | No | 132.8% | 211.5% | 10.5% |
| Proposed | END only | **Yes** | 25.3% | 41.9% | 8.3% |
| Proposed | All | No | 13.1% | 13.3% | 6.4% |
| **Proposed** | **All** | **Yes** | **13.0%** | 9.8% | **4.7%** |

**Four things to read off this table:**

1. **Row 4 is the paper's most important result.** Panel data *alone* gives MAPE in excess of 400–860%.
   *"This suggests that panel selection bias is not ignorable, and that **naively combining the panel
   data with the aggregate would make the resulting forecasts worse than if the panel data were simply
   ignored**."* Three million individual-level records, used without selection correction, are worse
   than useless.
2. **END alone cannot separate acquisition from churn.** With END only and no panel, END is forecast
   reasonably (10.5%) but ADD and LOSS exceed 100%. This matters because **many firms disclose only
   END** — Netflix, Blue Apron, HelloFresh, Care.com are named.
3. **Panel data helps uniformly once corrected** (row 6 vs 5; row 8 vs 7), and aggregate ADD/LOSS help
   uniformly whether or not panel data is present (row 8 vs 6; row 7 vs 5).
4. **The proposed model wins on ADD and END** (though MFH is better on LOSS). END is singled out as
   "particularly important... because it is most directly tied to total revenues."

**Robustness to horizon** is arguably the more valuable finding for CBCV: MFH is better at very short
horizons but its MAPE "grows quickly... rising to approximately **20% six quarters out**," while the
proposed model stays **in single digits across all horizons**. Since CBCV requires 50-year revenue
projections, long-horizon stability is the property that matters.

### 5.2 What the parameters say

- **Seasonality is driven by repeat acquisition** — high propensity to be *re*-acquired in Q2 and Q4 —
  not by initial acquisition. A decomposition no prior model could produce.
- **Strong positive `ρ_λ^(IA,IC)` = 0.516**: those who acquire early also churn early, so **later
  joiners are more loyal**. Consistent with Schweidel et al. (2008a) — and note this is the exact
  correlation the independent-gamma specification would have been unable to represent.
- **`ρ_λ^(IA,RA)` = 0.994**: high initial-acquisition propensity goes with high reacquisition propensity.
- **Selection coefficients**: `β_RA^(Z)` = 2.893, `β_RC^(Z)` = −2.868 — panel members have **higher
  propensity to re-adopt and lower propensity to re-churn** than the population. Explanation offered:
  panel members are US-based credit-card holders, hence "wealthier and more likely to adopt than the
  average Spotify prospect."
- **The headline substantive finding:** Spotify's **repeat retention curve sits well above its initial
  retention curve** — so as the base shifts toward reacquired customers, aggregate retention improves.
  Their phrase: *"a more sanguine view of Spotify's future retention profile than previous approaches
  which do not use multiple data sources."*

### 5.3 The candid limitation

Standard errors on the heterogeneity and selection parameters are **large** (e.g. `σ_λ^(IC)` = 5.517
with SE 22.748). They own this:

> "This nonetheless suggests that **the empirical identification of our model is not strong, even
> after performing data fusion**. This reflects the fact that our aggregate data is limited: even
> though the panel is very informative about initial and repeat behaviors, **under the presence of
> selection bias, we are uncertain as to how well this information generalizes to the population**."

Two of the large SEs have benign explanations, which they give: `β₀^(Z)`'s SE is inflated by
uncertainty in the mean of `λ_i` (centering the λ's gives −10.60 with SE 2.58), and correlations
involving `λ^(RC)` are poorly identified because `σ_λ^(RC)` is small — there is little variation to
correlate with.

---

## 6. Where it generalizes

- **Noncontractual CBCV** (McCarthy & Fader 2018) is named as "an important extension" — harder,
  because churn is latent.
- **Discrete choice**: aggregate market-share data could generalize scanner-panel price sensitivities
  beyond panel members, "who may differ from the general population in their sensitivities **even
  after controlling for demographics**" (Lusk & Brooks 2011). Note this is an *inference* problem, not
  prediction — and they claim their simulations support that use too.
- **A third data structure, and the most likely one to arise in practice:** firms that "only possess
  detailed internal transactional data for **recently acquired cohorts** (e.g. due to adoption of a new
  CRM system), but possess only aggregated statistics summarizing customer activity of previous
  cohorts." This is an *inside-out* problem, not outside-in, and it is extremely common.
- For **Markovian** models, the belief-propagation algorithm in Web Appendix 2 computes the required
  moments efficiently.

---

## How this maps onto the repo

- **This is the frontier of the CBCV line** in [../valuation/valuation-summary.md](../valuation/valuation-summary.md), and
  nothing in `notebooks/` approaches it. It is also the only paper in the corpus with a genuine
  **estimation-theory** contribution rather than a modeling one.
- **The single most transferable warning** is §5.1 row 4: granular data combined naively with
  aggregate data produced **481–860% MAPE**, far worse than discarding it. Any future essay that
  merges a panel with company disclosures must model selection explicitly.
- **MPL as a technique is reusable well beyond CBCV.** Any repo model currently fitted by NLS on
  aggregate series (`bg-nbd`, the CBCV essays) could in principle be extended: keep the exact
  likelihood for individual-level data, add a normal-approximation term for aggregate series, optimize
  jointly. The BridgeStan/cmdstanpy infrastructure under `stan/` is well suited to it.
- **The correlated-lognormal heterogeneity (§3.2)** is a genuinely different choice from the
  gamma/beta conjugate mixing used everywhere else in the repo. The trade — lose conjugacy, gain the
  ability to estimate cross-process correlations — is worth a worked comparison, since "early adopters
  are early abandoners" is exactly the kind of claim the Fader–Hardie models cannot express.
- **Initial vs repeat retention (§2, §5.2)** is a real gap in
  [`valuation/cbcv-subscription-based`](../../../notebooks/valuation/) and in
  [`models/retention/`](../../../notebooks/models/retention/): every retention model in the repo
  treats all customers as one population, when reacquired customers demonstrably behave differently.
- **§1.1 is a template.** Few papers state so precisely when their own method should *not* be used.
  Worth emulating in the essays' "limits to application" sections.
