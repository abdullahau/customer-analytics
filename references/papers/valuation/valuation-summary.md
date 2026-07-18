# `valuation/` — reading summary

The **customer-based corporate valuation (CBCV)** literature — connecting the probability models in
the rest of this repo to actual firm valuation using *publicly disclosed* data. Read in the order
below; it is a genuine intellectual progression, with each paper naming and fixing the previous
one's defects.

| # | Work | Year | Length |
|---|---|---|---|
| 1 | Gupta, Lehmann & Stuart, **"Valuing Customers"**, *JMR* 41 (Feb), 7–18 | 2004 | 12 pp. |
| 2 | Schulze, Skiera & Wiesel, **"Linking Customer and Financial Metrics to Shareholder Value: The Leverage Effect in Customer-Based Valuation"**, *Journal of Marketing* 76(2), 17–32 | 2012 | 17 pp. |
| 3 | McCarthy, Fader & Hardie, **"Valuing Subscription-Based Businesses Using Publicly Disclosed Customer Data"**, *Journal of Marketing* 81 (Jan), 17–35 | 2017 | 19 pp. |
| 4 | McCarthy & Fader, **"Customer-Based Corporate Valuation for Publicly Traded Noncontractual Firms"**, *JMR* (2018) | 2018 | 19 pp. |
| 4w | *(working paper of #4)* "Valuing Non-Contractual Firms Using Common Customer Metrics", SSRN 2923466 | 2017 | 54 pp. |
| 5 | Damodaran, **"Going to Pieces: Valuing Users, Subscribers and Customers"**, NYU Stern | 2018 | 46 pp. |
| 6 | Reutterer, **"Models for Customer Valuation"** — annotated bibliography | 2015 | 5 pp. |

**On the duplicates:** `Valuing Customers.pdf` and `Valuing Customers-v2.pdf` are **byte-identical
in content**; ignore one. `Valuing Non-Contractual Firms...` (SSRN, Feb 2017) is the working-paper
version of the JMR article (#4) — same model, more appendix detail, and a **different retailer**
in places; the published version uses Overstock and Wayfair.

Mirrored by [`valuation/cbcv-subscription-based`](../../../notebooks/valuation/) (paper 3) and
[`analyses/customer-acquisition-cost`](../../../notebooks/analyses/).

---

## 1. Gupta, Lehmann & Stuart (2004) — *Valuing Customers*

The paper that started CBCV. Everything after it is partly a correction of it, but its framing and
its elasticity results have held up.

### 1.1 The problem it solves

Valuing **high-growth firms with negative earnings**. P/E is undefined with negative earnings; DCF
struggles with negative cash flow. During the dot-com bubble this produced "eyeballs" metrics —
and academic support for them: Trueman, Wong & Zhang (2000) found that for 63 internet firms
*"bottom-line net income has no relationship to stock price, [but] unique visitors and page views add
significant explanatory power."*

**Their objection to that literature** is worth keeping, because it is a general methodological point:
those studies "are correlational and assume that the market value represents the true intrinsic value
of the firm at any time, which is an efficient market argument. However, even if the markets are
efficient in the long run, recent history suggests that significant deviations exist in the short
run." Regressing on market value bakes in the market's error.

### 1.2 The model

Start with the per-cohort lifetime value, then aggregate across cohorts:

```
LV = Σ_t  m_t · r^t / (1+i)^t                            (2)   [one cohort, constant retention r]

              ∞    ∞                                    ∞
Value  =  Σ      Σ    [n_k/(1+i)^k] · m_{t−k} · r^{t−k}/(1+i)^{t−k}  −  Σ  n_k c_k/(1+i)^k    (7)
            k=0  t=k                                                    k=0
```

with `n_k` = customers acquired in cohort `k`, `c_k` = acquisition cost, `m_t` = margin at customer
age `t`. Then converted to continuous time — noting the useful identity `r^t/(1+i)^t ≡ e^{−[(1+i−r)/r]t}`.

**Four stated reasons for an infinite horizon** (a good checklist): no arbitrary cutoff year; the
retention rate already discounts distant periods; the common "convert retention to expected lifetime,
then take PV over that finite period" approach **overestimates** LV; and infinite-horizon models are
simpler to estimate.

That third point comes with a worked example: at $100/year margin, 80% retention, 12% discount, the
correct LV is **$250**; treating 80% retention as "5-year expected life" and taking the 5-year PV
gives **$360 — a 44% overestimate.**

**Customer acquisition** is modeled with an S-shaped logistic (Fisher–Pry technological substitution,
equivalent to the internal-influence special case of Bass), chosen over Bass proper for mathematical
convenience:

```
N_t = α / (1 + exp(−β − γt)) ,     n_t = dN/dt = αγ·exp(−β−γt) / [1+exp(−β−γt)]²

peak customer acquisition at  t = −β/γ
```

**Everything comes from public data except the retention rate** — a deliberate design goal, so that
"external constituencies, such as investors, financial analysts, and acquirer companies" can use it.

### 1.3 Data and results

Five firms, quarterly data 1996/97–March 2002: **Capital One** (traditional, as a validity check) plus
**Amazon, Ameritrade, eBay, E*Trade**.

| | Customers (Mar '02) | Qtrly margin | Acq. cost | Retention |
|---|---|---|---|---|
| Amazon.com | 33.8M | $3.87 | $7.70 | 70% |
| Ameritrade | 1.88M | $50.39 | $203.44 | 95% |
| Capital One | 46.6M | $13.71 | $75.49 | 85% |
| eBay | 46.1M | $4.31 | $11.26 | 80% |
| E*Trade | 4.12M | $43.02 | $391.00 | 95% |

**Valuation vs market value ($B, March 2002):**

| | Customer value | Market value | Verdict |
|---|---|---|---|
| Capital One | 11.00 | 14.08 (range 9.48–14.31) | ✔ within range |
| Ameritrade | 1.62 | 1.40 (1.09–1.49) | ✔ close |
| E*Trade | 2.69 | 3.35 (2.71–4.49) | ✔ close |
| **Amazon.com** | **0.82** | **5.36** | ✘ far below |
| **eBay** | **1.89** | **15.85** | ✘ far below |

**The two misses are exactly the two noncontractual firms** — a fact the authors don't note but
which papers 3–4 make the centre of their critique. Regression of market value on customer value
across all firm-quarters gives **R² = 0.139**; dropping Amazon and eBay gives **R² = 0.927**, with
intercept indistinguishable from 0 and slope indistinguishable from 1.

### 1.4 The elasticity results (the paper's lasting contribution)

Effect of a **1% improvement** in each lever on customer value:

| | Retention | Acq. cost | Margin | Discount rate |
|---|---|---|---|---|
| Amazon.com | 2.45% | .07% | 1.07% | .46% |
| Ameritrade | **6.75%** | .03% | 1.03% | 1.17% |
| Capital One | 5.12% | .32% | 1.32% | 1.11% |
| eBay | 3.42% | .08% | 1.08% | .63% |
| E*Trade | 6.67% | .02% | 1.02% | 1.14% |

Three headline conclusions:

1. **Retention elasticity is 3–7× margin elasticity and 10–100× acquisition-cost elasticity.**
2. **Retention elasticity is ~5× discount-rate elasticity.** The pointed implication: *"Financial
   analysts and company managers spend considerable time and effort in measuring and managing discount
   rate... our results show that it is perhaps more important... to pay close attention to a firm's
   customer retention rate."*
3. **The higher a firm's current retention, the larger the effect of improving it** (Ameritrade at 95%
   vs Amazon at 70%) — and there is a strong **interaction with the discount rate**: retention matters
   more at *low* discount rates, so "companies in mature and low-risk businesses should pay even more
   attention to customer retention."

**Two caveats the authors themselves raise**, often dropped when this paper is cited: the analysis
**excludes the cost of improving retention or margin**, and it **ignores interactions** among
acquisition, retention and margins (e.g. price-promotion acquisition attracting low-retention
customers — Thomas 2001). Also cited: Shaffer & Zhang (2002) show it is *not* optimal to eliminate
churn entirely — 100% loyalty may mean you are underpricing, "leaving money on the table."

**The known defect** (see [../spend-clv/spend-clv-summary.md](../spend-clv/spend-clv-summary.md) §3.2): constant retention
rate, and for Amazon/eBay a **repeat-buying rate used as a retention rate**.

---

## 2. Schulze, Skiera & Wiesel (2012) — the leverage effect

Adds the **finance** that GLS omitted: firms have debt and non-operating assets, so customer equity
is not shareholder value.

### 2.1 The argument

The first four CBV studies all implicitly assume customer equity = shareholder value, hence that a
10% rise in CE gives a 10% rise in SHV. Not so: **debt amplifies and non-operating assets dampen** the
percentage transmission.

```
              CE_afterIndC + NOA − DEBT
SHV_preTax  =  ─────────────────────────  ... so, defining the leverage effect as an elasticity:

        dSHV_preTax     CE_afterIndC          CE_afterIndC
LE  =  ─────────────  × ────────────  =  ────────────────────────────       (6)
       dCE_afterIndC     SHV_preTax      CE_afterIndC + NOA − DEBT
```

Their three-company illustration makes it concrete: with CE rising $1,000 → $1,100 in all three cases,

| CE : SHV ratio | 1:1 | 1:2 | 10:1 |
|---|---|---|---|
| Leverage effect | 1.0 | 0.5 | 10.0 |
| % increase in SHV | 10% | 5% | **100%** |

### 2.2 The empirical result

**>2,000 companies over ten years.** Debt averages **23% of firm value**, non-operating assets **4%**;
debt exceeds NOA for **86%** of companies.

> **The average leverage effect is 1.55** — a 10% increase in customer equity produces, on average, a
> **15.5%** increase in shareholder value. LE < 1 in only 14% of cases.

Company-specific examples: **Verizon 1.40** (high debt) vs **Netflix 1.04** (little debt, little NOA).
For Verizon, *"ignoring debt and non-operating assets in the CBV model would yield a SHV result that
is 29% too high."*

Practical advice: compute a firm-specific LE, but **1.55 is a usable rule of thumb.**

### 2.3 The challenge to "retention is king"

This is the paper's most interesting and least-cited result. Observed change in SHV combines **two**
things: the *elasticity* of SHV to a metric, and the *magnitude of change* actually observed in that
metric. GLS measured only the first.

For Netflix, elasticities are broadly consistent with GLS — retention **4.4**, profit contribution
1.8, discount rate 1.1, number of future customers only **0.9**. But:

| Netflix 2003 | Elasticity | Unexpected change | Total effect |
|---|---|---|---|
| Retention rate | 3.4 | +8.1% | **+27%** |
| Number of future customers | 0.9 | **−61.4%** | **−57%** |

> "Despite its high elasticity, the retention rate has a **smaller effect on changes in SHV** because
> its likelihood to change (as measured by the magnitude of change over time) is rather low. Instead...
> **the number of customers**, which deviates strongly from the previous year's predictions, plays
> this role."

Verizon shows the same pattern: future customers, profit contribution, and the discount rate dominate.

**The implication for this repo:** the most valuable modeling effort in a CBCV exercise may be the
**acquisition** sub-model, not the retention sub-model — because retention is stable and predictable
while acquisition is volatile. This directly motivates the elaborate acquisition models in papers 3
and 4.

They also find, via a projection-horizon analysis on Netflix and Verizon, clear support for **infinite
projection horizons**: for a high-debt firm like Verizon, short horizons produce *negative* SHV
because there is not enough time to accumulate profits to repay debt.

---

## 3. McCarthy, Fader & Hardie (2017) — subscription-based CBCV

The paper the [`valuation/cbcv-subscription-based`](../../../notebooks/valuation/) essay implements.

### 3.1 The two indictments of GLS

1. **Constant retention rate** → undervalues existing customers (Fader & Hardie 2010).
2. **The valuation framework does not meet finance standards** — no capital structure, no
   non-operating assets. And this applies to SSW too: *"the underlying models of customer behavior and
   the associated valuation frameworks are not up to the standards expected by marketers and financial
   professionals, respectively."*

### 3.2 The DCF scaffolding

```
SHV_T   = OA_T + NOA_T − ND_T                                   (1)
OA_T    = Σ_t  FCF_{T+t} / (1 + WACC)^t                         (2)
FCF_t   = NOPAT_t − (CAPEX_t − D&A_t) − ΔNFWC_t                 (3)
NOPAT_t = [REV_t·(1 − VC_t) − FC_t]·(1 − TR_t)                  (4)
```

The whole marketing contribution is **producing `REV_t`** — everything else is standard finance.
Quoting Damodaran (2005): *"The research into valuation models and metrics in finance is surprisingly
spotty, with some aspects... being deeply analyzed and others, such as **how best to estimate cash
flows**... not receiving the attention that they deserve."*

### 3.3 The C(·,·) matrix — the conceptual centrepiece

`C(m, m′)` = customers acquired in month `m` still active in month `m′`. Rows = acquisition cohorts,
columns = calendar time. From it:

```
A(m) = C(m, m)                                   acquisitions
L(m) = C(·, m−1) − [C(·, m) − C(m, m)]           losses
ARPU(m) = R(m) / ([C(·,m−1) + C(·,m)]/2)         average revenue per user

END_q  = C(·, 3q)
ADD_q  = A(3q−2) + A(3q−1) + A(3q)
LOSS_q = L(3q−2) + L(3q−1) + L(3q)
```

**And this reconciles the supposed DCF-vs-CBV schism** — a genuinely clarifying contribution. Skiera
& Schulze (2014) argue the two approaches are fundamentally different. McCarthy et al. disagree:

> "Previous 'customer-based valuation' methods are performing **on a row-by-row basis** what are
> effectively net present value calculations across columns and then summing across rows. **'DCF
> methods'... are summing the columns** and then effectively performing a net present value calculation
> across these column totals. Given the same customer matrix C(·,·)... both approaches should yield the
> same estimate of firm value."

Different traversals of the same matrix. The practical reason to prefer the DCF traversal is
sociological: *"finance professionals (including the chief financial officer and company directors)
are more comfortable with a valuation model based on estimates of period-by-period FCF."*

### 3.4 The customer model

**Retention** — Weibull-baseline proportional hazards with gamma heterogeneity:

```
S_R[m′−m | m, X_R; λ_R, c_R, β_R] = exp[−λ_R B_R(m, m′)]

B_R(m,m′) = Σ_{i=m+1}^{m′} [(i−m)^{c_R} − (i−m−1)^{c_R}] · e^{β_R x_R(i)}

Integrating λ_R ~ gamma(r_R, α_R):
S_R[·] = [ α_R / (α_R + B_R(m,m′)) ]^{r_R}
```

`c_R = 1` reduces to exponential; they expect `c_R ≥ 1` (Schweidel, Fader & Bradlow 2008b; Jamal &
Bucklin 2006). Note this captures **both** heterogeneity (gamma) **and** individual duration
dependence (Weibull) — see [../retention/retention-summary.md](../retention/retention-summary.md) §6.

**Acquisition** — and here they give **four explicit reasons Bass/logistic won't do**:

1. It assumes churned customers **disappear forever** and cannot re-enter the pool of potential
   adopters. (SSW work around this by modeling *net* customers.)
2. It assumes **fixed population size**, when the number of potential customers grows.
3. The Bass adoption curve is **symmetric about the peak**; "in real data sets, skewness about the
   peak is almost always present."
4. It **ignores seasonality and macroeconomic events**.

So: prospect pools re-form each month from population growth **plus churned customers**,

```
M(m) = POP(m) − POP(m−1) + L(m)                                       (15)
A(m) = Σ_{i=0}^{m−1} M(i)·[F_A(m−i|i) − F_A(m−i−1|i)]                 (16)
```

with a **split-hazard** model: a proportion `p_NA` of each pool never acquires; the rest have
Weibull-PH/gamma acquisition timing.

**Parsimony is defended, not just asserted**, citing Van den Bulte & Lilien (1997): ill-conditioning
in small samples means "adding new predictors to alleviate model misspecification concerns may make
the resulting model fit (and forecast) **worse**."

**Estimation** — joint nonlinear least squares on ADD/LOSS/END, with explicit handling of **missing
data**. Two forms of missingness: **left-censoring** (Sirius XM began operations 2001/02 but only
disclosed paying-customer data in Q3 2008 — "almost half of Sirius XM's customer data are missing"),
and **staggered disclosure** (END reported before ADD/LOSS). The SSE objective adapts accordingly
(their Eq. 21), using *differences* of END during the ADD/LOSS-free window.

**ARPU** — a time-trend regression, but with a real diagnostic: fit `ARPU(m) = b₀ + b₁m + ε`, run the
**augmented Dickey–Fuller** test on the residuals, and if it fails, switch to **ARIMA(0,1,0)**:
`ARPU(m) = ARPU(m−1) + b₀ + ε`. (DISH fails ADF at t = −2.6, p = .31 → ARIMA; Sirius XM passes at
t = −3.56, p = .04 → trend regression.)

**Why not use reported ARPU?** Because there is no standard definition — quoting DISH's own 2014
filing: *"We are not aware of any uniform standards for calculating ARPU and believe presentations of
ARPU may not be calculated consistently by other companies."* Revenue is reliable; ARPU is not. So
they impute monthly revenue from quarterly revenue using the modelled customer counts (Eq. 24).

### 3.5 Results

**DISH Network** (mature, high-variable-cost, sells into households; 77 quarters to Q1 2015, ADD/LOSS
left-censored to Q1 1998). Covariates: three quarterly dummies + a **Great Recession** dummy.

The fitted covariates tell a coherent story: recession coefficient **negative in acquisition**,
**positive in retention** (higher churn) — and larger in magnitude than any seasonal term. The
seasonal pattern matches DISH's own annual-report language about first-half vs second-half
activations and Q1/Q4 churn.

**Rolling validation is the real test:** 60 different calibration periods (Q = 10…69), each forecasting
8 quarters ahead. MAPE at Q+8:

| | GLS | SSW | Proposed |
|---|---|---|---|
| ADD/LOSS/END, Q+1 | 26.0 | 14.7 | **8.2** |
| Q+8 | 55.8 | 22.9 | **16.0** |

Crucially, the proposed model's accuracy "remains tight **even for short calibration periods**."

**Valuations:**

| | DISH (Q1 2015) | Sirius XM (Q1 2015) |
|---|---|---|
| Operating assets | $15.7B | $27.1B |
| NOA − Net debt | $14.1B | −$3.7B |
| Shareholder value | $29.9B | $23.4B |
| Implied stock price | **$64.62** | **$4.24** |
| Actual | $66.38 | $3.90 |
| Error | **−2.7%** | **+7.4%** |

(Benchmarks for DISH: GLS $48.84, SSW $63.72.)

**A sensitivity analysis with a genuinely actionable output.** Bootstrapping each process's residuals
separately gives 95% intervals on the implied price: acquisition **±0.2%**, retention **±3.4%**, ARPU
**±3.0%**. Conclusion: *"it would be most beneficial to investors if DISH were to provide more or
better data regarding **customer retention** (e.g., by disclosing LOSS figures monthly instead of
quarterly)."* A model that tells a firm which disclosure would most reduce investor uncertainty.

### 3.6 The customer-level insights from firm-level data

The best demonstration of what the model buys you. **"Recent Robin"** (acquired Q1 2015) vs
**"Longtime Larry"** (acquired Q1 2005):

```
E[residual lifetime | acquired m, alive at M] = Σ_i  S_R[M+i−m|·] / S_R[M−m|·]      (26)
```

| | Recent Robin | Longtime Larry |
|---|---|---|
| Expected residual lifetime | 5.5 years | **9.4 years** |
| Pretax RLV | $1,426 | **$1,932** |

*(Robin's average initial acquisition cost: $854.)* **GLS and SSW would give both customers the same
expected future lifetime.** And all of this is derived **with no customer-level data whatsoever** —
only public aggregate disclosures.

They also note the risk dimension: Longtime Larry is more valuable *and* more risky (higher variance
about the expectation), and that longer expected lifetimes mean more stable cash flows → lower
perceived risk → lower cost of capital → higher valuation.

---

## 4. McCarthy & Fader (2018) — noncontractual CBCV

The hardest case, and the direct answer to GLS's Amazon/eBay failure.

### 4.1 Three challenges specific to noncontractual settings

1. **Churn is unobservable**, so firms cannot disclose customers lost or total customer base.
2. **Order and spend patterns are far more variable** than for subscription firms.
3. External stakeholders have only **repeated cross-sectional summaries** (Jerath, Fader & Hardie
   2016), not individual data — limiting model richness.

### 4.2 The critique of the standard workaround

The workaround is: assume an observable "retention rate" (usually the repeat rate), assume alive
customers = active customers, proceed as if contractual. Four things wrong with it:

- **The repeat rate understates future activity.** Their example is excellent: *"6% of consumer
  products seller QVC's total sales in 2015 came from customers who had **not purchased in over a
  year**."*
- Ignoring **heterogeneity in retention** further undervalues the base.
- **Firms define the same metric differently.** "Active customers" means orders in the preceding
  **3 months at Overstock, 12 at Wayfair, 24 at Camping World.** Cross-firm comparison is meaningless.
- Resulting inferences about **unit economics** are wrong.

And the scoreboard: of GLS's five firms, *"the only two noncontractual businesses, eBay and Amazon,
were the two most misvalued"* — undervalued by **88% and 83%** respectively.

### 4.3 The model

Same DCF scaffolding as paper 3. Revenue decomposes into **total orders** (initial + repeat) ×
**average revenue per order (ARPO)**.

**Acquisition — a two-segment "time of mass awareness" model.** Prospects are split by whether their
pool formed before or after a **structural break `w*`, which is estimated from the data**:

- Early prospects: a proportion `p₁` are "intenders" at pool formation, with Weibull(λ₁)-PH timing.
- The rest have **zero acquisition probability before `w*`**.
- At `w*`, a proportion `p₂` of the remaining early prospects **become** intenders, with a different
  Weibull(λ₂) baseline but shared covariate coefficients `β_A` (for identification).
- The rest, `(1−p₁)(1−p₂)`, never acquire.
- Late prospects: proportion `p₂` are intenders at formation, Weibull(λ₂)-PH.

**The estimated `w*` is independently interpretable in both applications** — the strongest evidence
the structure is real:

- **Overstock:** `w*` coincides with its 2003 pivot from B2B to consumer. (B2B activity with Safeway
  alone fell from 16% of sales in 2002 to <1% by 2004.)
- **Wayfair:** `w*` = Q4 2012, when the company **closed and redirected 240+ niche websites into
  Wayfair.com**, becoming a one-stop shop. *"Whereas only 11% of early prospects were intenders at the
  time their prospect pool first formed, **41%** of those remaining became intenders at the time of
  mass awareness."*

**Repeat orders** — Poisson with log-normal intensity `λ_O(w) = exp(β_O + β_O^T x_o(w))`, capturing
unobserved heterogeneity and seasonality/macro effects together.

**A notable modelling choice, and its justification:** heterogeneity is *omitted* from the acquisition
Weibull baseline — *"both to maintain model parsimony and because, empirically, heterogeneity has been
rejected every time we have applied the model to data allowing for it."*

**On endogeneity** — an unusually direct defence of not correcting for it:

> The modeler "is a passive external stakeholder who only has access to publicly disclosed data...
> an endogeneity-corrected valuation model may have **lower holdout predictive validity** than an
> uncorrected model because the firm and external stakeholders are **unable to observe endogenous
> variables in the holdout period**."

Citing Besanko, Gupta & Jain (1998) and Neslin (1990) as prior cases where corrected models
underperformed. The general principle: **endogeneity correction serves inference, not prediction**,
and valuation is a prediction problem.

### 4.4 Results

Metrics used: `QADD`, `QAU`/`AAU` (quarterly/annually active users), `QTO` (total orders), `QREV`,
`AREV`. Overstock and Wayfair each report only *one* of QAU/AAU.

**MAPE of rolling two-year predictions:**

| Overstock | GLS | SSW | LMP | Proposed |
|---|---|---|---|---|
| QADD | 67.6 | 18.8 | 18.0 | **11.8** |
| QAU | 64.2 | 16.5 | 16.2 | **10.5** |
| QTO | 61.9 | 17.0 | **14.5** | 15.3 |
| QREV | 56.3 | 23.2 | 16.2 | **15.0** |

| Wayfair | GLS | SSW | LMP | Proposed |
|---|---|---|---|---|
| QADD | 17.8 | 21.0 | 15.0 | **4.9** |
| AAU | 19.9 | 3.0 | 2.7 | **2.1** |
| QTO | 20.5 | 8.8 | 8.8 | **5.8** |
| QREV | 18.9 | 5.9 | 5.6 | **4.9** |

On average ~80% / 30–40% / 18–35% lower MAPE than GLS / SSW / LMP respectively.

**A finding that contradicts the natural expectation:** you'd think a mature firm is easier to forecast
than a young one, but "holdout prediction accuracy is **dramatically higher at Wayfair** than at
Overstock," and within Overstock accuracy is best for *mid-length* calibration periods. They are
appropriately cautious — two companies is not a meta-analysis.

**Valuations (Q1 2017):**

| | Overstock | Wayfair |
|---|---|---|
| Operating assets | $354.1M | $825.4M |
| NOA − Net debt | $72.7M | $55.5M |
| Shareholder value | $426.8M | $880.8M |
| Implied stock price | **$16.88** | **$10.24** |
| Actual | $15.50 | **$64.16** |
| Error | +8.9% | **−84.0%** |

**Valuation intervals, not point estimates.** 2,500 bootstrap resamples of the residuals produce a
distribution. Overstock's observed price sits at the **38th percentile** of the model's distribution —
"not significantly different from our fair-value estimate." For Wayfair, **every single bootstrapped
realization lies below the observed price**; even the most optimistic revenue path (peak QREV >$12B vs
a baseline of $2.3B) implies $57.03, still 11% below market. The uncertainty itself is informative:
the SD of the percentage difference is **72% for Wayfair vs 28% for Overstock**.

They then situate this in the actual market disagreement — bulls (MKM Partners, Cowen) vs bears
(Citron Research: *"Wayfair is a throwback to 1999, a business where there's never EBITDA, just
cumulative losses"*), with over **40% of Wayfair's tradeable shares sold short** and a 6% borrow fee.

### 4.5 Unit economics — the part they think matters most

> "We predict that this deeper examination of the underlying financial health of a firm may be **more
> useful to financial professionals than the valuation estimate itself**."

Definitions used:
- **CAC** = trailing-12-month advertising expense ÷ customers acquired (consistent with both firms'
  own statements and with GLS).
- **Marginal profit** = **"EBITDA − CAC"** — expected QREV per acquired customer × the firm's overall
  ratio of (EBITDA − CAC) to revenue.

| | Overstock | Wayfair |
|---|---|---|
| NPV of post-acquisition profits per customer | $47 | **$59** |
| CAC | **$38** | $69 |

So Wayfair's customers are *more* profitable once acquired but cost **nearly double** to acquire. The
general principle stated:

> "Businesses that acquire low- (or negative) CLV customers may nevertheless **report strong revenue
> growth** if they grow customer acquisition expenses quickly enough, [but] will be very reliant on a
> continued high rate of new customer acquisition and will have greater difficulty growing themselves
> into profitability."

**A stated limitation worth remembering:** they assume the **disclosure decision is not strategic**.
Firms may choose what to disclose in a forward-looking way (Mintz et al. 2016).

---

## 5. Damodaran (2018) — *Going to Pieces: Valuing Users, Subscribers and Customers*

The same problem from the **finance** side. Damodaran thanks McCarthy in the acknowledgments and cites
paper 4, so this is a genuine cross-disciplinary meeting rather than a parallel literature.

### 5.1 The framing: aggregated vs disaggregated valuation

DCF is **additive** — value the whole or value the parts and sum; in theory identical. Aggregated
valuation dominates historically for two reasons: we buy whole companies, and **disclosure is
aggregated**. Four reasons to disaggregate anyway: fundamental differences in risk/growth across
units; divergent growth rates (which make a weighted bottom-up beta unstable over time); transactional
needs (spin-offs); and management/monitoring.

His claim: for user-based companies, **the natural disaggregated unit is the user.**

### 5.2 The three-part decomposition

```
Value of a user-based company
    = Value of Existing Users  +  Value of New Users  −  Value of Corporate Drag
```

**Why separate new from existing:** "to allow for a cleaner analysis of **acquisition costs and
whether they are paying off**, not in terms of just additional users, but in terms of value created."

**Corporate drag** is Damodaran's distinctive contribution — costs "indispensable to business existence
but unrelated to users" (G&A and similar). His Netflix illustration shows why it can't be ignored:
an existing subscriber costs little to serve and delivers ~$100/year, but Netflix spent **>$9B in 2017
on content**, and "it is almost impossible to determine how much of this spending is for existing
customers and how much is to grow the subscriber base. Consequently, you may choose to ignore this
cost when valuing existing and new users... but **you cannot ignore it, if your intent is to invest in
the company**."

He is candid that the framework needs data that isn't public: *"tagging the information you need to
value a user is the first step towards better information disclosure at these companies."*

### 5.3 The three worked valuations

| | Existing users | New users | Corporate drag | Total |
|---|---|---|---|---|
| **Uber** (user-based) | | | ~$1B initial | **$42.5B** incl. $5B cash + $6B Didi stake |
| **Netflix** | $59.8B (117M subs) | $137.3B | −$111.3B | operating assets **$85.9B**, equity **$82.2B** |
| **Amazon Prime** | $58.45B | $101.75B | −$87.3B | **$72.9B** |

Note the scale of corporate drag — for Netflix and Amazon Prime it is roughly the size of the existing-
user value. A valuation that omits it is not merely imprecise; it is wrong by a factor.

For Uber his user-based approach gives $42.5B against $36B from an aggregated valuation — "a little
higher," which he treats as reassuring rather than alarming.

### 5.4 The value-dynamics propositions

These are the genuinely portable ideas, and they have no counterpart in the marketing papers.

**Proposition 1 — how you lose money matters.** Reallocating Uber's operating expenses between
servicing existing users and acquiring new ones:

| % of opex on new-user acquisition | Value existing | Value new | Total ($M) |
|---|---|---|---|
| 0% | 6,167 | 18,147 | 24,314 |
| 50% (interp.) | ~17,300 | ~20,400 | ~37,700 |
| 100% | 28,426 | 22,587 | **51,013** |

> "A money-losing company that is losing money **providing service to existing users** is worth less
> than a company with equivalent losses where the primary expenses are **acquiring new subscribers**."

The counter-intuitive part: shifting spend toward acquisition raises the value of existing users
(they're now cheap to serve) **and** the value of new users (the added value outweighs the added cost).

**The 2×2 that classifies user businesses:**

| | **High** cost of new user | **Low** cost of new user |
|---|---|---|
| **High** existing user value | *Exclusive user business* — focus on getting, keeping, and upselling the highest-value users | ***Value stars*** — strong competitive advantages keeping acquisition cheap |
| **Low** existing user value | ***Disasters*** — "lots of users, but they will continually lose money, even as they grow" | *Commoditized user business* — most users wins |

The structural insight behind it: high existing-user value and low acquisition cost "generally don't go
together, since the features of the business that allow **you** to add new users at low cost usually
allow **your competitors** to do the same," which then erodes renewal rates and value per user. Hence
value stars are "the exception, not the rule."

**Network effects and big data, demystified:** both are just mechanisms that move a company toward the
top-right cell — raising existing-user value *and* lowering acquisition cost simultaneously.

---

## 6. Reutterer (2015) — *Models for Customer Valuation*

Not a paper — a **five-page annotated bibliography** in five sections: managerial CLV; overviews of
stochastic buyer-behaviour models; BTYD models proper; extensions toward full CLV (spend sub-models);
and recent developments.

Useful mainly as a **taxonomy of Pareto/NBD variants**, most of which appear nowhere else in this
corpus:

| Variant | Modification | Source |
|---|---|---|
| **BG/NBD** | dropout only at repurchase incidents | Fader, Hardie & Lee (2005) |
| **MBG/NBD** | + dropout opportunity right after the initial purchase | Batislam, Denizel & Filiztekin (2007) |
| **CBG/NBD** | same, "central" variant | Hoppe & Wagner (2007) |
| **PDO** | decouples discrete dropout opportunities from the purchase process | Jerath, Fader & Hardie (2011) |
| **gamma-Gompertz/NBD** | non-constant hazard in the dropout process | Bemmaor & Glady (2012) |
| **BG/BB** | discrete-time analog of Pareto/NBD | Fader, Hardie & Shang (2010) |

Also flags five active research directions: covariates; Bayesian estimation; more flexible
interpurchase timing; HMM-based nonstationarity; and **"clumpiness"** — Zhang, Bradlow & Small (2015),
*"Predicting customer value using clumpiness: From RFM to **RFMC**"* — plus Platzer & Reutterer (2015)
on incorporating regularity. The BTYD R package (Dziurzynski, Wadsworth & McCarthy) is listed.

---

## How these map onto the repo

- **Paper 3 is the source for
  [`valuation/cbcv-subscription-based`](../../../notebooks/valuation/)** — the DISH and SiriusXM data
  live in `data/`, and the ADD/LOSS/END/REV structure is exactly what that essay fits.
- **The `C(·,·)` matrix (§3.3) deserves to be a first-class object in `lib/`.** Every CBCV quantity —
  ADD, LOSS, END, ARPU, cohort survival, RLV by tenure — is a projection of it, and the row-vs-column
  framing dissolves the DCF-vs-CBV argument in one paragraph.
- **Paper 4 is not yet implemented** and is the obvious next essay: it is the noncontractual analogue
  and the natural destination for the repo's Pareto/NBD machinery. The Overstock/Wayfair data is
  public.
- **The estimation patterns are the transferable engineering content**: joint NLS on multiple
  aggregate series (§3.4), explicit left-censoring/staggered-disclosure objectives (Eq. 21), and
  **bootstrap valuation intervals** (§4.4). None of the repo's current essays produce interval
  estimates; they should.
- **Paper 2 §2.3 should change modeling priorities.** Retention has the highest *elasticity* but low
  *variance*; acquisition has low elasticity but high variance, so it drives observed SHV changes.
  If effort is finite, spend it on the acquisition sub-model.
- **Paper 1 §1.4's elasticity table** is a good sanity check for any CLV model built here: retention
  elasticity should land in the 2–7 range, margin elasticity near 1.0.
- **Papers 4 §4.5 and 5 §5.4 together are the unit-economics story** — CAC vs post-acquisition NPV,
  and Damodaran's "how you lose money matters" proposition. These belong in
  [`analyses/customer-acquisition-cost`](../../../notebooks/analyses/), which currently has no
  valuation framing.
- **Damodaran's corporate drag (§5.2)** is absent from all the marketing papers and is a real gap: a
  CBCV built purely from customer sub-models will overstate firm value unless non-user costs are
  explicitly deducted.
- **Cross-reference:** the constant-retention critique running through papers 2–4 is developed in
  [../spend-clv/spend-clv-summary.md](../spend-clv/spend-clv-summary.md) §2.4 (the aggregation illusion) and
  [../retention/retention-summary.md](../retention/retention-summary.md) §3.2 (the sorting effect). Paper 1 is the
  cautionary example those critiques are aimed at.
