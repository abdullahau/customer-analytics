# `foundations/` — reading summary

Two survey/overview pieces that frame the whole repo. Read these **first**: they supply the
taxonomy, the vocabulary, and the philosophical stance that every other essay assumes.

| # | Work | Year | Length |
|---|---|---|---|
| 1 | Fader & Hardie, **"Probability Models for Customer-Base Analysis"**, *Journal of Interactive Marketing* 23, 61–69 | 2009 | 9 pp. |
| 2 | Ascarza, Fader & Hardie, **"Marketing Models for the Customer-Centric Firm"**, in *Handbook of Marketing Decision Models* (2nd ed.), Springer, 297–329 | 2017 | 44 pp. (post-print) |

Companion notes: [Repeat-Buying summary](../brand-choice/repeat-buying-summary.md)
and [Data Reduction summary](../brand-choice/data-reduction-summary.md) cover the
Ehrenberg–Bass tradition; paper 1 below is the Fader–Hardie tradition's equivalent manifesto, and
explicitly traces its lineage to Ehrenberg (1959).

---

## 1. Fader & Hardie (2009) — *Probability Models for Customer-Base Analysis*

The single most useful 9 pages in the repo. It is the source of the 2×2 taxonomy, the
`past = f(θ) / future = f(θ)` framing, and the "RFM are sufficient statistics" result — all of
which are quoted (sometimes verbatim) in `CLAUDE.md`.

### 1.1 The probability-modeling approach

The modeler's mindset: observed behaviour is the **outcome of an underlying stochastic process**.
We have only a *"foggy window"* onto customers' true tendencies, "and therefore the past is not a
perfect mirror for the future."

> If a customer made two purchases last year, is he necessarily a "two per year" buyer, or is there
> some chance that he might make three or four or perhaps even zero purchases next year?

The build sequence (their Fig. 1):

1. **Individual-level model** — specify `past = f(θ)` using a simple distribution (Poisson,
   binomial, exponential) or a combination of them.
2. **Mixing distribution** — θ is by definition unobserved, so assume a distribution capturing
   cross-sectional heterogeneity. Choice driven by "the dual criteria of **flexibility and
   mathematical convenience**."
3. **Mixture model** — the two combined; characterizes a *randomly chosen* customer.
4. **Bayes' theorem** — after fitting, invert to get `g(θ | data)`, hence individual-level
   predictions.

Crucially: *"there is no attempt to explain the variation in θ as a function of covariates; we are,
in most cases, content to capture the variation using probability distributions alone."*

**Two-step vs one-step.** `θ = f(past)` then `future = f(θ)`, versus the regression/data-mining
single step `future = f(past)`. Two stated advantages of the probability model:

- **No holdout split needed to create a dependent variable.** All observed data is used to infer
  behavioural characteristics — you don't burn half your calibration window building a y-variable.
- **Any future horizon.** Predict over an arbitrary period, including a closed-form **infinite
  horizon with discounting** (i.e. CLV). A regression trained on a fixed-length window cannot do this.

A footnote draws a boundary worth keeping: this is **not** the same as Markov-chain approaches
(Pfeifer & Carraway 2000), which "do not account for heterogeneity in the underlying behavior
characteristics, which can lead to misleading inferences about the nature of buying behavior"
(citing Massy, Montgomery & Morrison 1970).

### 1.2 The classification of analysis settings

Motivated by two real quotes, only one of which is legitimate:

- **Vodafone UK, Q3 2008 press release** — "7.3 million *pay monthly* customers." **Valid.** These
  are contract customers; the customer must *tell* Vodafone when switching provider.
- **Amazon CFO, Q4 2007 earnings call** — "active customer accounts [customers who ordered in the
  past year] exceeded 76 million." **Not valid.** The 12-month cutoff is arbitrary; move it to nine
  months and "the apparent size of Amazon's customer base would be smaller, even though the true
  size would remain unchanged."

**Dimension 1 — contractual vs noncontractual.** Noncontractual = the time a customer becomes
inactive is *unobserved*; customers "do not notify the firm when they stop being a customer.
Instead they just silently attrite" (Mason 2003). A firm in a noncontractual relationship **can
never know how many customers it has at any point in time.**

**Dimension 2 — continuous vs discrete transaction opportunities.** Four worked settings:

| Setting | Contractual? | Timing |
|---|---|---|
| Airport lounge (United Red Carpet Club) | contractual (lapse on non-renewal) | discrete |
| Electrical utility | contractual | continuous |
| Academic conference | **non**contractual (no attendee ever writes to say they're done) | discrete |
| Mail-order clothing | **non**contractual | continuous |

> "While in certain circumstances a model developed for a discrete setting can be applied in a
> continuous setting (and vice versa), the **contractual/noncontractual divide is fundamental and
> the boundary cannot be crossed**: it is completely inappropriate to apply a model developed for a
> contractual setting in a noncontractual setting (and vice versa)."

### 1.3 Noncontractual, continuous time (the most-studied quadrant)

**The four-customer diagnostic (their Fig. 3)** — the clearest statement anywhere of *why* recency
and frequency both matter, and why neither alone suffices:

- **B and C both made 4 purchases**, but C's last was long ago → C is likely dead; expect more from B.
- **A and C have the same recency**, but A is a *light* buyer, so her long hiatus is unremarkable →
  **A is more likely alive than C**. But whether A will buy more is open: C, *conditional on being
  alive*, has the higher rate.
- **B and D have the same recency** → equally (highly) likely alive, but D made fewer purchases →
  expect fewer future purchases from D.

**Why not just NBD?** Tracking a cohort's cumulative sales gives a curve that bends over (Fig. 4).
A steady aggregate rate would be a straight line, so we are seeing **nonstationarity — a "slowing
down."**

**Pareto/NBD** (Schmittlein, Morrison & Colombo 1987) explains it with "buy till you die": customers
buy at steady but *different* rates (different sloped lines), and at different points they become
permanently inactive. NBD purchasing while alive; exponential lifetime with gamma heterogeneity =
**Pareto Type II**. On the cause of death:

> "It could be a change in customer tastes, financial circumstances, and/or geographical location,
> the outcome of bad customer service experiences, or even physical death... But given the modeling
> objectives, **why this death occurs is of little interest to us**; our primary goal is to ensure
> that the phenomenon is captured by the model."

**The sufficiency result.** Given the assumptions, we do *not* need the timing of the intermediate
transactions — only `(x, tₓ, T)`. Called "a very important result that ties this model to the
traditional direct marketing literature," and it is what makes implementation cheap.

**Extensions catalogued** (a useful map of the literature):

| Direction | Work |
|---|---|
| MCMC estimation | Ma & Liu (2007); Abe (2008) |
| Time-invariant covariates | Abe (2008); Fader & Hardie (2007b) |
| + spend submodel | Schmittlein & Peterson (1994); Fader, Hardie & Lee (2005b); Glady et al. (2008) relaxes independence of spend and transaction flow |
| **DERT** → residual CLV from RFM alone | Fader, Hardie & Lee (2005b) |
| Only histogram / cross-sectional data (no individual RFM) | Fader, Hardie & Jerath (2007) — *Tuscan Lifestyles* revisited |
| Death only at discrete calendar points | Jerath, Fader & Hardie (2007) — **PDO** model |
| Easy-to-estimate variant | Fader, Hardie & Lee (2005a) — **BG/NBD** |

**The PDO limiting result is worth remembering**: as periodicity → 0 the PDO converges to the
Pareto/NBD; when periodicity exceeds the calibration period the dropout process is "shut off" and it
converges to the **plain NBD**. So NBD and Pareto/NBD are two ends of one family.

**Why BG/NBD exists.** Despite 1987 publication, the Pareto/NBD saw "relatively limited real-world
action, the major problem being perceived challenges with respect to parameter estimation." BG/NBD
changes the death story — dropout *after a transaction* w.p. p, beta heterogeneity — and is "vastly
easier to implement; for instance, its parameters can be obtained quite easily in Microsoft Excel."

**A recurring caveat about richer alternatives.** Erlang (Wu & Chen 2000), generalized gamma
(Allenby, Leone & Jen 1999), and other nonstationarity stories (Moe & Fader 2004; Fader, Hardie &
Huang 2004) are all noted — and all carry the same two objections: they typically **require the full
transaction history** (not just RFM), and **no one has derived P(alive) or conditional expectations
for them**, "which are central to any forward-looking customer-base analysis exercise."

### 1.4 Noncontractual, discrete time

Data is a **binary string** per customer. Natural starting point: Bernoulli purchasing (not Poisson).
Example: Berger, Weinberg & Hanna (2003) on repeat cruising in each of the 4 years after first cruise.

Two reasons to be here even when reality is continuous: (i) genuinely discrete opportunities
(a conference happens on specific dates — "if the conference is scheduled for June 20–23, one cannot
attend it on May 30!"); (ii) **management discretizes** for summarization/storage — "particularly
appropriate for very rare events" (e.g. a charity recording only whether you gave to the year-x fund
drive).

**BG/BB** (Fader, Hardie & Berger 2004): beta-Bernoulli purchasing while alive + beta-geometric death.

> As the discrete period length → 0, beta-Bernoulli → NBD and beta-geometric → Pareto II. **The BG/BB
> is the discrete-time analog of the Pareto/NBD and converges to it.**

Same sufficiency result: recency + frequency only, no need for the full binary string.

Fader & Hardie flag this quadrant as **neglected** — "we find this surprising and feel that it is an
area of research that deserves more attention."

### 1.5 Contractual settings

Two managerial questions, and they need **different tools**:

1. *"Which customers have the greatest risk of churning next period?"* → best answered by
   **regression / predictive data mining** (logit with usage, usage deltas, call-centre contacts,
   marketing activity).
2. *"How much longer can we expect this customer to stay?"* → **duration models only.**

The reason (1)'s tools fail at (2) is sharp and worth quoting: *"Standing at the end of period t, it
would not be possible to predict contract renewal probabilities for period t + 3 since we do not have
the values of the independent variables for period t + 2, let alone period t + 1."*

**Discrete time → sBG** (shifted-beta-geometric; Kaplan 1982, Weinberg & Gladen 1986). Constant
individual retention `1 − θ`, beta-distributed θ. "Despite what may seem to be overly simplistic
assumptions... generates very accurate forecasts of retention."

**The heterogeneity/sorting argument** — the repo's central methodological commitment, stated here in
its canonical form. Retention rates almost always rise with tenure: *"renewal rates at regional
magazines vary; generally 30% of subscribers renew at the end of their original subscription, but
that figure jumps to 50% for second-time renewals and all the way to 75% for longtime readers"*
(Fielding 2005).

> The aggregate retention rate associated with the sBG **is an increasing function of time, even
> though the individual-level retention probability is constant**. The observed dynamics are "the
> result of a **sorting effect in a heterogeneous population** where individual customers exhibit no
> retention-rate dynamics."

**Continuous time → exponential-gamma** (= Pareto II). Long pedigree outside marketing: new-product
trial (Hardie, Fader & Wisniewski 1998), retail franchise store lifetimes (Dekimpe & Morrison 1991),
and "jobs, strikes, and wars" (Morrison & Schmittlein 1980). Its **hazard function decreases** with
time even though the individual-level exponential hazard is constant — the same sorting effect.

**When you genuinely want individual-level dynamics** → replace exponential with **Weibull**, giving
Weibull-gamma; this permits *positive* duration dependence too. Empirically: Schweidel, Fader &
Bradlow (2008) find the basic exponential-gamma "often quite acceptable." Where Weibull wins, the
finding is counterintuitive and important — **individual subscribers exhibit *increasing* churn
hazard even though aggregate churn rates are *decreasing*** (supported by Jamal & Bucklin 2006).

### 1.6 The closing philosophy

> "These are all parsimonious models... an **evolutionary approach to model building** — one in which
> we start with the simplest reasonable representation of the behaviors of interest, with a view to
> creating an easy-to-implement model. Further texture is added to the model **only if the end-use
> application really requires it**."

And the historical irony they end on: the building blocks "were developed at a time when data were
scarce... How times have changed! The proverbial fire hose is invoked over and over again, and
advances in computation are not enough to keep up." The models "come into their own in such an
environment as they are simple to implement and make use of easy-to-compute data summaries."

---

## 2. Ascarza, Fader & Hardie (2017) — *Marketing Models for the Customer-Centric Firm*

A far broader literature review, organised around **managerial activity** rather than model type.
Where paper 1 is the modeler's manifesto, this is the map of the whole field — including large areas
(acquisition targeting, churn campaigns, cross-sell, budget allocation) that the repo does **not**
cover and, mostly, deliberately shouldn't.

### 2.1 What makes a firm "customer-centric"

Distinguished from merely "customer-oriented" by three properties: (i) tracks individuals over time
and across channels and computes **forward-looking** metrics at a granular level; (ii) identifies
high-CLV customers and treats them as the growth engine "in the same way that a product-centric firm
views its best products"; (iii) sees product development as a **means to an end** — elevating
customer value — "instead of seeing it as an end unto itself."

**Three drivers of organic growth: acquisition, retention, development.** They flag immediately that
retention and development cannot be cleanly separated in practice ("is getting the next transaction
'retention' or 'development'?"), and so review them jointly as *managing acquired customers*.

An alternative vocabulary they cite (Bolton et al. 2004): **length, depth, and breadth** of the
relationship — depth = usage frequency and upgrades, breadth = cross-buying.

### 2.2 The CLV definitional formulas

Following Rosset et al. (2003):

```
E(CLV) = ∫₀^∞  E[V(t)] · S(t) · d(t) dt

E(RLV) = ∫_{t₀}^∞  E[V(t)] · S(t | t > t₀) · d(t − t₀) dt
```

where `E[V(t)]` = expected net cash flow at t given alive, `S(t)` = survival probability, `d(t)` =
discount factor, `t₀` = the customer's current age.

**Three quantities that must not be conflated:** the value of an *as-yet-unacquired* customer, the
value of a *just-acquired* customer (the two differ by the value of the first transaction — and
possibly acquisition cost), and the **residual** lifetime value of an existing customer.

Two warnings stated flatly:

- *"Any calculation of CLV or RLV **cannot terminate the calculation at, say, three years** and call
  the resulting quantity lifetime value."*
- You must not assume the customer is alive throughout a finite horizon — an explicit criticism of
  Kumar et al. (2008), Rust et al. (2004), Venkatesan & Kumar (2004).

**On time-varying covariates in CLV.** This is why the stochastic-model tradition ignores them:
including marketing-activity covariates means you must **forecast those covariates far into the
future**, "which clearly introduces a lot of additional noise into the exercise." Hence the whole CLV
literature "has tended to ignore the effects of time-varying covariates and drawn on the
well-established traditions of stochastic models of buyer behavior."

**On textbook CLV formulas.** The standard `S(t) = rᵗ` constant-retention formula has "pedagogical
value as a means of introducing the concept... [but is] of limited value in the real world," because
observed cohort retention rates rise over time. Consequences ripple into finance: this "has
implications for work that explores the linkage between the value of a firm's customer base and its
stock market valuation, such as Gupta et al. (2004), Schulze et al. (2012)" — see
[../valuation/valuation-summary.md](../valuation/valuation-summary.md).

**Hybrid settings** are an emerging category — observed *and* unobserved attrition in the same
customer pool (Ascarza, Netzer & Hardie 2016). Note also the explicit rejection of Jackson's (1985)
*lost-for-good vs always-a-share* classification as a substitute: "the notion of **latent attrition**
is missing from the basic always-a-share model."

### 2.3 Customer acquisition — the under-served area

> "There is very little research on acquisition marketing... Positioning, segmentation, targeting is
> a generic concept. Research in advertising studies the general impact of communications but does
> not separate newly acquired customers from retained customers" (Blattberg et al. 2008).

**The key conceptual trap:** many apparently acquisition-focused papers are "**acquiring customers
for the product**, which is not the same as acquiring customers for the firm." Example given:
Schwartz et al. (2016) count an account opening as acquisition without distinguishing genuinely new
bank customers from existing ones. **The new-product trial and diffusion literatures are
product-centric in exactly this sense** — which matters directly for reading
[../new-product/new-product-summary.md](../new-product/new-product-summary.md): those models are valuable to a
customer-centric firm (they cite McCarthy et al. 2016b), but their original application was not.

Their working definition: a customer is acquired at **first purchase** — with freemium noted as
genuinely ambiguous (sign-up vs first payment).

Classic direct-marketing practice reviewed: A/B tests → fractional factorial and Plackett-Burman
designs; list testing; a priori segment tests; response scoring (logit, discriminant, CHAID, CART).
**Rollout response is commonly *lower* than test response** — hence a line of work on adjusting test
results (Allenby & Blattberg 1987; Ehrman 1990; Morwitz & Schmittlein 1998).

**The threshold should be lifetime value, not first-transaction profit** — recommended since Simon
(1967), with Petrison et al. documenting the practice back to the 1940s–60s.

**Response probability is not the whole story:** *"it may make sense to target those prospects with
lower response probabilities but higher value given acquisition than ones with higher response
probabilities but lower value given acquisition."* Requires modeling value-given-acquisition on
covariates (Hansotia & Wang 1997); Ainslie & Pitt (1998) add riskiness.

Beyond direct mail: WOM and seeding (Hinz et al. 2011; Van der Lans et al. 2010), **referral
programs** (Kumar et al. 2010; Schmitt et al. 2011; Van den Bulte et al. 2015), and comparisons of
**acquisition-channel quality** (Steffes et al. 2011; Trusov et al. 2009; Verhoef & Donkers 2005;
Chan et al. 2011). Datta et al. (2015) on free trials, Lewis (2006) on introductory discounts.

### 2.4 Churn management — and the critique of it

Standard practice: binary DV, predictors from a prior window, evaluate by **top-decile lift**.
Methods surveyed: logistic regression, CART/C4.5, neural nets, SVM, ensembles.

**Blattberg et al.'s (2008) profitability framework** for a proactive retention campaign — worth
reproducing because it makes the economics explicit. Contact a fraction α at cost `c` with an
incentive worth `δ`. Of those contacted, β would have churned, and γ of those are "rescued." Of the
`1 − β` who would *not* have churned, ψ take the incentive anyway with value change ∆.

```
upside   =  βγ·CLV  +  (1 − β)ψ∆·CLV
downside =  c  +  [βγ + (1 − β)ψ]·δ
```

Used by Neslin et al. (2006) to score a churn-modeling tournament; Verbeke et al. (2012) turn it into
a **maximum-profit (MP) model-selection criterion** — choose the model maximizing profit at its own
optimal targeting fraction, rather than lift at an arbitrary 10%. Verbraken et al. (2013) add
uncertainty in costs/benefits.

**Then the punchline, which undercuts the entire literature above.** Quoting Hansen (2015):

> "The business objective is never 'predict the churners', it is 'reduce the value and rate of churn'
> ... do not waste time improving identification of churners, **focus on identifying those that can
> be dissuaded**."

And the authors are explicit that profit-based criteria do **not** fix this: "All this work targets
those with the highest risk of churning, but ignores the fact that **many of those with a high risk
of churning are very dissatisfied and cannot be dissuaded** (at least profitably)." Ascarza (2016)
therefore proposes targeting by **sensitivity to the intervention**, not risk. Ascarza, Iyengar &
Schleicher (2016) go further — contacting non-would-be-churners can *cause* churn.

This is the **uplift / incremental modeling** argument, and it is the chapter's main forward-looking
recommendation (§5): estimate the *counterfactual difference* with and without intervention, and
recognize heterogeneity in that difference — not in the base rate.

### 2.5 Contact response models (noncontractual)

Since attrition is unobservable, there is **no attrition KPI** — so modeling effort goes into
predicting response to contacts instead.

**Hughes' (1996) quintile RFM** described precisely: rank on recency into quintiles (5 = most
recent), repeat for frequency and for average spend → `5 × 5 × 5 = 125` segments. Useful context for
[`analyses/rfm-summary`](../../../notebooks/analyses/) — this is the *practitioner* RFM the
probability models displace.

**Selection bias and endogeneity** are called out as endemic: the model is estimated on a non-random
sample (because the firm's own targeting rule chose who got mailed), and the RFM predictors are
correlated with that targeting rule, biasing their coefficients. Remedies: instrumental variables,
policy functions, latent trait models (Cui et al. 2006; Donkers et al. 2006; Rhee & McIntyre
2008/2009; Rhee & Russell 2009). Muus et al. (2002) add a Bayes decision rule accounting for
parameter uncertainty.

**Beyond incidence:** Type II Tobit is the workhorse for modeling *whether* and *how much* jointly.

**The multi-mailing trap**, quoting Kestnbaum et al. (1998) — the best statement of why campaign-by-
campaign optimization fails:

> "If a customer is not selected because he or she falls **a little below the cutoff**... This may
> happen for every campaign, so the customer is **inadvertently abandoned**. Receiving no contacts
> for an extended period of time, he or she is not very likely to buy and the poor performance
> becomes worse."

So the decision should be *how many* mailings per customer per year, not *whether* to mail each time.

Also noted: HMM-based approaches to underlying dynamics (Netzer et al. 2008; Montoya et al. 2010),
with the observation that **the Schmittlein et al. (1987) latent-attrition tradition can be viewed as
a constrained HMM** (Schwartz et al. 2014).

### 2.6 Contact customization, cross-sell, up-sell

Cross-sell = new categories; up-sell = pricier variants/add-ons. Simplest form is the "next product
to buy" model (Knott et al. 2002; Moon & Russell 2008), criticized by Li et al. (2011) as too
campaign-focused; the customer-centric version asks "the right product to the right customer at the
right time using the right communication channel."

**Bodapati's (2008) result mirrors the uplift argument** and is the cleanest statement of it: don't
recommend the product with the highest purchase probability, recommend the one whose **purchase
probability increases the most with recommendation**. *"Why recommend a product the customer was
going to buy anyhow?"*

Up-selling has received less attention; related work on **share of wallet** (Du et al. 2007; Chen &
Steckel 2012).

### 2.7 Coordinating acquisition and retention

Blattberg & Deighton (1996) introduced customer equity with decision-calculus models for optimal
acquisition and retention spend; extended by Berger & Bechwati (2001), Dong et al. (2007)
(acquisition-**channel quality**, creating dependence between acquisition and retention), Swain et
al. (2014) (margin-reducing incentives that attract the "wrong" customers).

**Two limitations the authors stress.** First, all of it models per-period retention rate as a
function of per-period retention spend, ignoring cohort-level retention dynamics — "**as such, it
only applies to contractual settings**. The analog formulation for noncontractual settings is not
immediately obvious." Second, the formulation is static/single-period with a fixed prospect pool,
assuming the same retention spend in perpetuity without checking that this is optimal.

A footnote kills an apparent shortcut: embedding Blattberg–Deighton in a **brand-switching**
framework does *not* make it work noncontractually, because "the fact that someone purchases from a
competitive firm between two purchases from the focal firm should not necessarily mean that they
churned after the first purchase and were acquired (again) when they made their second purchase."

**Acquisition and retention are empirically linked**, which most allocation models ignore: relationship
duration correlates with acquisition likelihood (Thomas 2001; Reinartz et al. 2005) and with
**acquisition speed** — "customers who are acquired more quickly tend to have shorter relationships
than those who took longer" (Schweidel et al. 2008b).

---

## How these map onto the repo

- **The 2×2 taxonomy** (§1.2) is the organising principle of `notebooks/models/`. Paper 1's Fig. 2 is
  the source of the table in `CLAUDE.md`.
- **§1.3's four-customer diagnostic** is the natural opening exposition for `pareto-nbd` and
  `bg-nbd` essays.
- **§1.5's sorting argument** is the "ruse of heterogeneity" that `models/retention/beta-geometric`
  demonstrates, and §1.5's Weibull discussion is exactly `beta-discrete-weibull`'s motivation.
- **The PDO limiting result** (§1.3) gives a clean way to position `nbd-overview` and `pareto-nbd`
  as endpoints of one family — currently not made explicit in the essays.
- **Paper 2 §2.2's `E(CLV)` / `E(RLV)` integrals** are the general form that `models/clv/rfm-and-clv`
  and `valuation/cbcv-subscription-based` specialize.
- **Paper 2 is largely a map of what this repo does *not* do** — acquisition targeting, churn
  campaigns, cross-sell, budget allocation. Useful for scoping: those are covariate/optimization
  problems, not probability-model problems, and the chapter's own §5 says the field there is thin.
- **The uplift argument** (§2.4, §2.6) is the single most transferable idea for anyone tempted to
  bolt a "who will churn" classifier onto these models: the right target is sensitivity to
  intervention, not risk.
