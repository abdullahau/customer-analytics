# `spend-clv/` — reading summary

Three distinct works covering the **monetary-value sub-model** and the **assembly of CLV** from its
components — plus a short teaching note that is the best available corrective to how CLV is usually
taught.

| # | Work | Year | Length |
|---|---|---|---|
| 1 | Fader, Hardie & Lee, **"RFM and CLV: Using Iso-Value Curves for Customer Base Analysis"**, *JMR* 42 (Nov), 415–430 | 2005 | 16 pp. |
| 1w | *(same paper, working-paper version)* `rfm_clv_2005-02-16.pdf` | Feb 2005 | 40 pp. |
| 2 | Fader & Hardie, **"Simple probability models for computing CLV and CE"**, ch. 3 in *Handbook of Research on Customer Equity in Marketing* (Kumar & Shah, eds.), 77–100 | 2015 | 24 pp. |
| 3 | Fader & Hardie, **"Reconciling and Clarifying CLV Formulas"**, note 024, brucehardie.com | 2012 | 9 pp. |

**On the duplicate:** `rfm_clv_2005-02-16.pdf` is the pre-publication version of paper 1 — same
argument, same numbers, same section structure. Its only advantage is a **substantially longer
appendix** (full step-by-step derivation of the DET expression rather than the compressed JMR
version). Read the JMR PDF for the paper; open the working paper only when you need the derivation.

Mirrored by [`models/clv/rfm-and-clv`](../../../notebooks/models/clv/) and
[`models/spend/gamma-gamma`](../../../notebooks/models/spend/).

---

## 1. Fader, Hardie & Lee (2005) — RFM, iso-value curves, and CLV

### 1.1 The three objections to scoring models

The paper opens by naming what's wrong with regression/scoring approaches to CLV. All three are worth
keeping — they are more specific than the usual "regressions are atheoretical" complaint:

1. **They predict period 2 only.** "When computing CLV, we are interested not only in Period 2 but
   also in Periods 3, 4, 5, and so on. It is not clear how a regression-type model can be used to
   forecast the dynamics of buyer behavior well into the future and then tie it all back into a
   'present value.'"
2. **They burn data to make a dependent variable.** Two periods are required — one to define RFM, one
   to build the DV. "It would be nice to be able to leverage **all** of the available data for model
   calibration purposes without using any of it to create a dependent variable."
3. **Observed RFM ≠ latent traits.** RFM variables are "only imperfect indicators of underlying
   behavioral traits" (Morrison & Silva-Risso 1995). Consequently **different slices of the data
   yield different RFM values and therefore different scoring-model parameters** — so the fitted
   coefficients are an artifact of the window you chose. Footnoted as applying equally to Dwyer's
   customer migration model and its extensions.

### 1.2 The exploratory motivation

CDNOW: the cohort of **23,570** customers who first purchased in Q1 1997, tracked 78 weeks. (Ten
buyers spending >$4,000 are removed — "probably unauthorized resellers" per CDNOW contacts — leaving
23,560.) Split 39/39, group by recency and frequency, plot mean spend in weeks 40–78.

The empirical surface is **visibly unusable**: "despite the large number of customers we used to
generate this graph, it is still sparse and, therefore, somewhat untrustworthy. Several 'valleys'...
are simply due to the absence of any observations for particular combinations." Plus the pattern
**depends on the arbitrary choice of period lengths**.

So: a model is needed not merely to predict, but **to fill in and de-noise the RFM space**. The
parallel drawn is to Schmittlein, Cooper & Morrison's (1993) work on "80/20 rules," where a model
yields a *time-invariant* concentration measure — cf.
[`analyses/estimating-purchasing-concentration`](../../../notebooks/analyses/).

### 1.3 The decomposition

```
CLV = margin × revenue/transaction × DET                                     (1)
```

This factorization is licensed by an **independence assumption** between spend and the transaction
process — which the paper then goes to unusual lengths to *test* rather than assert (§1.5).

**DET** — the paper's headline new analytical result. Rather than the cumbersome discrete sum

```
DET = Σ_t  { E[Y(t)|x,tₓ,T] − E[Y(t−1)|x,tₓ,T] } / (1+d)^t
```

they move to continuous compounding at rate δ over an **infinite horizon**, giving a closed form:

```
                        α^r β^s δ^{s−1} Γ(r+x+1) Ψ[s, s; δ(β+T)]
DET(δ|r,α,s,β,x,tₓ,T) = ───────────────────────────────────────────          (2)
                          Γ(r) (α+T)^{r+x+1} L(r,α,s,β|x,tₓ,T)
```

with `Ψ(·)` the confluent hypergeometric function of the second kind and `L(·)` the Pareto/NBD
likelihood.

**Why infinite horizon rather than a cutoff.** They explicitly reject the common practice of finding
the time at which `P(active|x,tₓ,T)` drops below a threshold and truncating there (as in Reinartz &
Kumar 2000/2003; Schmittlein & Peterson 1994): *"the probability that the customer is active is
already embedded in the calculation of E(Y(t)|x,tₓ,T), so this approach goes against the spirit of the
model."* Double-counting the death process.

### 1.4 The gamma-gamma spend sub-model

**Why a model is needed at all** — the cleanest statement of regression-to-the-mean in the repo:

> Suppose mean spend across all customers is $35, but Customer A has made **one** repeat purchase
> totaling **$100**. What value of E(M) should we use? Should we assume E(M) = $100, or should we
> "debias" our estimate down toward the population mean?

**Why not normal.** Schmittlein & Peterson (1994) assumed normal-on-normal. But the CDNOW data
(n = 946 repeat buyers) is badly skewed:

| | $ | | $ |
|---|---|---|---|
| Minimum | 3 | Mean | 35 |
| 25th pct | 16 | Std dev | 30 |
| Median | 27 | Mode | 15 |
| 75th pct | 42 | Skewness | **4** |
| Maximum | 300 | Kurtosis | **17** |

Lognormal would work distributionally but "there is no closed-form expression for the **convolution
of lognormals**" — so no closed form for the average of `x` transactions, which is exactly what's
needed. Hence **gamma** ("similar properties... albeit with a slightly thinner tail"), adapting
Colombo & Jiang (1999).

**Construction.** Transaction values `zᵢ ~ i.i.d. gamma(p, ν)`. Two standard gamma facts — the sum of
`x` i.i.d. gamma(p,ν) is gamma(px, ν), and scaling by `1/x` gives gamma(px, νx) — yield the
individual-level distribution of the observed average `mₓ`. Heterogeneity: `ν ~ gamma(q, γ)`.

**`p` is held constant across customers**, which is equivalent to assuming a **common coefficient of
variation** `CV = 1/√p`. Worth flagging — it is the model's least-discussed assumption.

Marginal distribution and the posterior mean:

```
f(mₓ|p,q,γ,x) = [Γ(px+q) / (Γ(px)Γ(q))] · γ^q m_x^{px−1} x^{px} / (γ + mₓx)^{px+q}     (3)

E(M|p,q,γ,mₓ,x) = (γ + mₓx)p / (px + q − 1)

                =  [ (q−1)/(px+q−1) ] · [ γp/(q−1) ]  +  [ px/(px+q−1) ] · mₓ           (4)
                    └─ weight on population ─┘  └pop mean┘  └── weight on own mₓ ──┘
```

Equation (4) written this way is the payload: **an explicit precision-weighted blend** of the
population mean `γp/(q−1)` and the customer's own observed average `mₓ`, with weight shifting toward
`mₓ` as `x` grows.

### 1.5 Testing the independence assumption (rather than assuming it)

The authors treat this as a genuine empirical question, and their approach is a template worth reusing:

- **Raw correlation** between average transaction value and number of transactions: **.11**. Driven
  largely by one outlier (21 transactions at $300 average); removing it drops it to **.06 (p = .08)**.
- **Box-and-whisker plots by frequency**: a slight positive tilt is visible, but "the variation
  **within** each number-of-transactions group dominates the between-group variation."
- **A holdout test that separates the two sub-models** (their Fig. 8), which is the clever part. Two
  sets of conditional expectations of forecast-period spend:
  - `expected | actual x₂` — model spend × *actual* holdout transaction count → **a clean test of the
    gamma-gamma alone**.
  - `expected | expected x₂` — model spend × *predicted* holdout count → **a test of the two
    sub-models combined**.

  Neither shows systematic bias, supporting both stationarity of spend and independence from frequency.

### 1.6 Fit and validation

Calibration on a 1/10th systematic sample (2,357 customers), 39/39 split.

**Pareto/NBD:** `r = .55, α = 10.58, s = .61, β = 11.67`. Aggregate cumulative repeat transactions
tracked closely, **under-forecasting by <2% at week 78**. Conditional expectations by calibration
frequency also track well.

**Gamma-gamma:** `p = 6.25, q = 3.74, γ = 15.44`. Theoretical mean transaction value differs from the
observed mean by **$0.09**.

**The one honest miss:** theoretical mode $19 vs observed mode **$15** — "the typical price of a CD at
the time the data were collected." The model "is not designed to recognize the existence of threshold
price points (e.g., prices ending in .99), so this mismatch is not surprising"; they decline to add
parameters "to maintain model parsimony."

**A parameter-stability check worth copying.** Re-estimate on all 78 weeks, then plug the 78-week
parameters back into the *39-week* log-likelihood:

| | optimal 39-wk LL | 78-wk params in 39-wk LL |
|---|---|---|
| Pareto/NBD | −9595 | −9608 |
| Gamma-gamma | −4659 | **−4661** |

The gamma-gamma degradation of 2 log-likelihood units over a doubled calibration window is "remarkable"
and is direct evidence that spend is stationary.

### 1.7 Iso-value curves and the "increasing frequency paradox"

Evaluating (2) across `tₓ = 0…78`, `x = 0…14` at a 15% annual discount rate (`δ = .0027` continuously
compounded) produces DET contours.

**The finding.** For low-frequency customers, DET is roughly **linear** in recency. For high-frequency
customers it is **highly nonlinear**, and the iso-value curves **bend backwards**:

> Someone with frequency `x = 7` and recency `tₓ = 35` has approximately the same DET (≈2) as someone
> with frequency `x = 1` and recency `tₓ = 30`. **In general, for people with low recency, higher
> frequency seems to be a bad thing.**

**Why this is correct, not a bug.** Consider two customers with the same (old) recency. If both were
certainly alive, the high-frequency one would be worth more. But a customer who *used* to buy
frequently and has now been silent for a long time is **strongly indicated to be dead** — the silence
is a large departure from their established rate. A light buyer's identical silence is unremarkable.
The net effect in their example: **DET = 4.6 for the light buyer, 1.9 for the heavy one.**

This is exactly the four-customer intuition from
[../foundations/foundations-summary.md](../foundations/foundations-summary.md) §1.3, now quantified. And it is the paper's
strongest argument against scoring models: *"The use of a regression-based specification... would
likely miss this pattern and lead to faulty inferences for a large portion of the recency/frequency
space."* A monotone-in-frequency regression cannot represent it.

### 1.8 The customer-base results

Full 78 weeks, 30% assumed gross margin ("no information about the actual margins for CDNOW, but this
number seems reasonably conservative"), 15% annual discount.

- **Cohort average CLV ≈ $47/customer**; 23,560 customers → **slightly more than $1.1 million**.
- **Best cell (R=3,F=3,M=3): $435 average NPV per customer, ≈38% of the cohort's entire future value**
  from 954 customers.
- **The zero class is the substantive surprise.** The 12,054 customers with *no* repeat purchase have
  an average residual CLV of only **$4.40** — but collectively **≈5% of the cohort's total future
  value, more than most of the other 27 RFM cells**.

  > "Many managers would assume that after a year and a half of inactivity, a customer has dropped out
  > of the relationship with the firm, but these very light buyers collectively constitute
  > approximately 5% of the total future value."

**Average CLV by tercile** — and note this validates the *ordering of the letters in "RFM"*:

| | 1 | 2 | 3 |
|---|---|---|---|
| Recency | 10 | 62 | **201** |
| Frequency | 18 | 50 | 205 |
| Monetary value | 31 | 81 | 160 |

"The greatest variability in CLV is on the recency dimension, followed closely by frequency. The least
variation is on monetary value. This is consistent with the widely held view that recency is usually a
more powerful discriminator... (thus, the framework is called RFM rather than, for example, FRM)."

### 1.9 Stated limitations and extensions

Four extensions named: marketing-mix covariates (with a warning about endogeneity and selection bias
from history-based targeting); an optimization layer; relaxing spend/transaction independence — via a
**bivariate Sarmanov distribution with gamma marginals** (Park & Fader 2004) correlating ν with λ, or
by going hierarchical Bayes; and relaxing constant margin.

On margin specifically: if margins vary within-customer you'd model **margin per transaction** rather
than spend, which requires "a skewed distribution defined over the domain of real numbers (to
accommodate the transactions on which the company makes a loss)" — the gamma's non-negative support
won't do. (McCarthy et al. later do exactly this; see [../valuation/valuation-summary.md](../valuation/valuation-summary.md).)

Also flagged: **only one cohort** was examined, and the definition of a cohort (initial-purchase date
vs geography vs acquisition channel) "might have a large influence on how the model is implemented in
practice."

---

## 2. Fader & Hardie (2015) — Simple probability models for computing CLV and CE

A handbook chapter that is the **best single reference for the DEL/DERL/DET/DERT formula set**. Much
overlaps [../foundations/foundations-summary.md](../foundations/foundations-summary.md); what follows is what's distinctive.

### 2.1 The framing contribution: observation-driven vs parameter-driven

Drawing on Cox's (1981) time-series taxonomy — a sharper way to state the anti-regression argument
than "scoring models are bad":

- **Observation-driven:** `θ_t = f(y_{t−1}, y_{t−2}, …)` — parameters depend on *past observed
  behaviour*.
- **Parameter-driven:** `θ_t = g(θ_{t−1}, θ_{t−2}, …)` — parameters depend on *past latent values*.

Why it matters for CLV: with an observation-driven model calibrated on `y₁,y₂,y₃`, you can predict
period 4 from `y₂,y₃` — but to predict period 5 you need `y₃,y₄`, and `y₄` is in the future. So you
must **simulate** it, "and as we move further away from the last period for which we have realizations
of Yₜ, we expect the forecasts to become increasingly unreliable as any prediction error propagates."

Parameter-driven models have no such problem: the process is estimated once from `y₁,y₂,y₃` and "no
additional observations (actual or simulated) are required regardless of the length of the forecast
horizon."

Their assessment of the field: *"The majority of models developed by researchers interested in CE are
observation-driven models."*

### 2.2 The four quantities

```
E(CLV) = ∫₀^∞ E[v(t)] S(t) d(t) dt          E(RLV) = ∫_{t'}^∞ E[v(t)] S(t|t>t') d(t−t') dt
```

Assuming constant net cash flow `v`:

| Setting | CLV | RLV |
|---|---|---|
| **Contractual** | `v · DEL` | `v · DERL` |
| **Noncontractual** | `v · DET` | `v · DERT` |

```
DEL  = ∫ S(t) d(t) dt                    DERL = ∫_{t'} [S(t)/S(t')] d(t−t') dt
DET  = ∫ t(t) S(t) d(t) dt               DERT = ∫_{t'} t(t) S(t|t>t') d(t−t') dt
```

With no discounting, `DEL = ∫S(t)dt = E(T)`, the expected lifetime.

### 2.3 The formula catalogue

**BG (discrete contractual):**

```
S(t|γ,δ) = B(γ, δ+t)/B(γ, δ)          r(t) = (δ+t−1)/(γ+δ+t−1)

DEL(γ,δ,d)  = ₂F₁(1, δ; γ+δ; 1/(1+d))                                       (3.8)
DERL(…; n−1 renewals) = [(δ+n−1)/(γ+δ+n−1)] · ₂F₁(1, δ+n; γ+δ+n; 1/(1+d))  (3.9)
```

*To get DEL for a **just-acquired** customer, subtract 1.* Period discounting: with `k` contract
periods per year, `d = (1+r)^{1/k} − 1`.

**Pareto Type II (continuous contractual):**

```
S(t|s,β) = (β/(β+t))^s          h(t) = s/(β+t)

DEL(s,β,δ_c)  = β^s δ_c^{s−1} Ψ(s, s; βδ_c)                                (3.11)
DERL(…; tenure t') = (β+t')^s δ_c^{s−1} Ψ(s, s; (β+t')δ_c)                 (3.12)
```

with `δ_c = ln(1+d)`; for data in `k` periods/year, `δ_c = ln(1+r)/k`.

**Pareto/NBD (continuous noncontractual):**

```
DET(r,α,s,β,δ_c)  = (r/α) β^s δ_c^{s−1} Ψ(s, s; βδ_c)                      (3.14)
DERT(…|x,tₓ,T)    = [Γ(r+x+1) α^r β^s δ_c^{s−1} / (Γ(r)(α+T)^{r+x+1})]
                     × Ψ(s,s;(β+T)δ_c) / L(r,α,s,β|x,tₓ,T)                 (3.15)
```

*DET here is for a **just-acquired** customer; **add 1** for an as-yet-unacquired one* — the `t=0`
first-ever purchase that starts the repeat clock.

**BG/BB (discrete noncontractual):**

```
DET(α,β,γ,δ,d) = [α/(α+β)]·[δ/(γ+δ)]·[1/(1+d)] · ₂F₁(1, δ+1; γ+δ+1; 1/(1+d))   (3.19)
DERT(…|x,tₓ,n) = [B(α+x+1,β+n−x)/B(α,β)] · [B(γ,δ+n+1)/(B(γ,δ)(1+d))]
                  × ₂F₁(1, δ+n+1; γ+δ+n+1; 1/(1+d)) / L(α,β,γ,δ|x,tₓ,n)        (3.20)
```

**BG/NBD:** noted that its DET/DERT expressions "are very messy" — better to compute DERT numerically
from conditional expectations via

```
DERT = Σ_{i≥1} (1/(1+d))^{i−0.5} { E[X(T,T+i)|·] − E[X(T,T+i−1)|·] }           (3.13)
```

Note the **`i − 0.5` mid-period discounting convention**.

### 2.4 The aggregation illusion — why company-reported retention looks constant

The chapter's best original contribution. Cohort retention rates rise; yet published company numbers
(they show two years of Vodafone Germany quarterly annualized churn) look flat. Both are true:

> "The aggregate retention rate numbers are a **weighted average of the retention rates across all
> cohorts** at any given time (i.e., a mix of 'young' and 'old' customers), and this weighted average
> will **mask and moderate** the within-cohort retention patterns, giving the analyst the impression
> that the retention dynamics are mild (and therefore possibly ignorable)."

A nice illustrative quote from a professional society newsletter: *"41% of new members who joined in
2011 renewed their membership in 2012, and ION has an overall retention of 78%."* — both numbers in
one sentence, from one organization.

**And the bias is large.** Taking a BG with `γ=0.764, δ=1.296` (fitted to the "regular" segment of
Fader & Hardie 2007a), the implied constant aggregate retention is 0.833. At $100/period and 10%
discount:

| | Constant r = 0.833 | BG (cohort dynamics) |
|---|---|---|
| RLV, end of 1st period | $343 | **$288** |
| RLV, end of 2nd period | $343 | **$394** |
| RLV, end of 5th period | $343 | **$568** |

The constant-rate model gives the same $343 forever; the correct model shows RLV *rising with tenure*.
Fader & Hardie (2010) put the resulting customer-base undervaluation at **25–50%** in standard
settings.

**And you don't need individual data to fix it.** A likely reason people persist with constant rates
is the belief that cohort-level or individual data is required. Fader & Hardie (2007b) show that under
certain assumptions, **only the number of new subscribers and total subscribers per period** are
needed — though you need them from launch, with reporting period = contract period. Fader, Hardie &
Liu (2012) handle reporting periods spanning multiple renewal periods and left-censored series.

### 2.5 Repeat-buying rate ≠ retention rate

Stated more forcefully here than anywhere else in the corpus. In a noncontractual setting you *can*
compute a **repeat-buying rate** ("percentage of brand customers in a given period who are also brand
customers in the subsequent period") and a **repurchase rate** ("percentage... who repurchase that
brand on their next purchase occasion"). Neither is a retention rate.

> "These measures are frequently **incorrectly referred to as retention rates**; for example, the
> annual **J.D. Power Customer Retention Study** for automobiles talks of retention when they are
> actually computing a repurchase rate."

Plugging such a number into `r^t` "leads to seriously biased estimates of CLV and CE."

### 2.6 On the absence of covariates

Notably, they defend it rather than apologize:

> "The documented multi-period forecasting performance of these models indicates that the absence of
> marketing covariate effects is **not a fundamental flaw. In fact, we view it as a positive
> characteristic.** The only real downside is that the models cannot be used for any CE-based
> **resource allocation** exercise."

A useful footnote on relaxing constant cash flow: the assumption is weaker than it looks. `v` is not
constant *across* individuals (the gamma-gamma handles that), and growth is easy — **if `v(t)` grows at
`100g`% per period, keep `v` and replace `d` with `d' = (d − g)/(1 + g)`.**

Closing quote, Urban & Karash (1971): *"The introduction of models as an evolutionary development from
simple to more complex but a related one would foster managerial acceptance, encourage an orderly
development of data and analysis systems, and reduce risks of failure."*

---

## 3. Fader & Hardie (2012) — Reconciling and Clarifying CLV Formulas

Nine pages, and it resolves a genuine confusion: three different CLV formulas circulate in textbooks
and cases, and most instructors don't know the others exist.

| Formula | Sources |
|---|---|
| `CLV = m(1+d)/(1+d−r)` | Blattberg, Kim & Neslin (2008); Steenburgh & Avery (2011) |
| `CLV = mr/(1+d−r)` | Capon (2007); Kotler & Keller (2012); Lehmann & Winer (2008) |
| `CLV = m/(1+d−r)` | Ofek (2002); Davis (2007) |

**All three are correct** — of different questions. The difference turns on exactly two things:
(i) is the customer's **first payment** included? (ii) is each period's cash flow booked at the
**beginning or end** of the period?

```
Case 1:  m at t=0, 1, 2, 3, …    →  E(CLV) = m Σ_t (r/(1+d))^t     = m(1+d)/(1+d−r)
Case 2:  m at t=1, 2, 3, …       →  E(CLV) = m[Σ_t (r/(1+d))^t −1] = mr/(1+d−r)
Case 3:  m at end of each period →  E(CLV) = (m/(1+d)) Σ_t (…)     = m/(1+d−r)
```

**Interpretation:**
- **Case 1** = value of an **as-yet-to-be-acquired** customer → the **upper bound on acquisition
  spend**.
- **Case 2** = **residual** value of a customer whose current-period payment is already booked.
- **Case 3** = as-yet-to-be-acquired, end-of-period cash flows.

**The concrete error they catch:** *"Capon (2007) proposes using equation (2) to determine an upper
bound on acquisition spend, when clearly it should be based off equation (1)."*

They also recommend a notation change worth adopting repo-wide: **write `E(CLV)`, not `CLV`** — the
quantity is an expectation over a probabilistic survival process. *"We strongly recommend this change
of notation in all discussions and demonstrations of customer lifetime value."*

**The prescription:** draw the Figure-1 timeline first, make the cash-flow timing explicit, *then*
derive. Don't hand out a magic formula or a margin-multiplier lookup table.

> "Some readers may be thinking 'Who cares? ... it doesn't really matter which formula I use, so long
> as they grasp the idea.' **We completely disagree.** ... By not encouraging our students to [think
> carefully], we only **lower the reputation of marketers in the eyes of finance and accounting
> professionals**, who generally have a strong understanding of these issues, at a time when we are
> crying out for more credibility."

### 3.1 The two deeper problems (§3.1–3.2)

**Non-constant retention.** All three formulas assume constant `r`. Replace `r^t` with `∏ᵢ rᵢ` and
"we do not get clean closed-form expressions" — plus you must now *project* retention. Bias is small
for new customers but **"easily on the order of 50–60%" for existing customers**, which "can have a
tremendous impact when computing the residual value of an entire customer base (e.g., for M&A
activities)."

**Contractual only.** In noncontractual settings "it is **meaningless** to talk about observed
retention rates, which means the above CLV expressions are of no use whatsoever... the `r^t` component
is completely meaningless in a noncontractual setting when the observed repeat-buying rate is treated
as a retention rate."

**Three named examples of the error in respected sources** — useful as cautionary cases:

1. **Ofek (2002)**, HBS Note "Customer Profitability and Lifetime Value" — the example is a **direct
   catalog retailer** (noncontractual), yet "what must be a repeat-buying rate is reported as a
   retention rate."
2. **Rosewood Hotels & Resorts** (Dev & Stroock 2007) — hotels, "clearly noncontractual"; the teaching
   note treats a repeat-buying rate as a retention rate and the spreadsheet has students apply
   equation (1).
3. **Gupta, Lehmann & Stuart (2004)**, *"Valuing Customers"* — the award-winning paper valuing five
   firms. Three (**Ameritrade, Capital One, E*Trade**) are contractual and "the CLV-based model
   provides good approximations for each firm's observed market value." Two (**Amazon, eBay**) are
   noncontractual and "not surprisingly, the incorrect use of a repeat-buying rate as a retention rate
   certainly helps explain why the CLV-based valuations are **way off the mark**." — This paper is in
   [../valuation/](../valuation/); read that summary alongside this critique.

> "It is not our objective here to 'call out' any colleagues in particular... the concerns described
> here are **endemic to the entire field of marketing**."

---

## How these map onto the repo

- **Paper 1 is the source for [`models/clv/rfm-and-clv`](../../../notebooks/models/clv/)** — the
  iso-value curves, the CDNOW parameters (`r=.55, α=10.58, s=.61, β=11.67`; `p=6.25, q=3.74, γ=15.44`),
  and the $1.1M cohort valuation.
- **Equation (4)'s explicit weighted-average form** is the payload of
  [`models/spend/gamma-gamma`](../../../notebooks/models/spend/) — write it in the two-term form, not
  just `(γ+mₓx)p/(px+q−1)`, because the shrinkage structure is the insight.
- **§1.7's backward-bending iso-value curves** are the single best visual argument in the repo for
  probability models over scoring models. If only one figure from this corpus gets reproduced, it's
  that one.
- **§1.5's two-way holdout design** (`expected|actual x₂` vs `expected|expected x₂`) is a reusable
  pattern for validating any two-component model, and is under-used generally.
- **Paper 2 §2.3 is a formula reference** — worth transcribing into `lib/models/` docstrings. Note
  the recurring ±1 conventions for just-acquired vs as-yet-unacquired customers; they are the most
  common source of off-by-one errors in CLV code.
- **Paper 2 §2.4 (the aggregation illusion)** explains why real company retention disclosures look
  flat, and is essential background for
  [`valuation/cbcv-subscription-based`](../../../notebooks/valuation/), which must fit models to
  exactly such aggregated public data.
- **Paper 3 is short enough to read in full** and should inform any CLV exposition in the repo —
  particularly the `E(CLV)` notation convention and the timeline-first derivation habit.
- **Cross-tradition note:** the Ehrenberg branch
  ([Repeat-Buying summary](../brand-choice/repeat-buying-summary.md)) computes
  repeat-buying rates as a *primary deliverable*. Paper 3 §3.2 is the reminder that those are
  **category-level behavioural measures, not survival probabilities**, and must never be substituted
  into `r^t`.
