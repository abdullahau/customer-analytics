# The Customer-Base Audit (Fader, Hardie & Ross, 2022) — Summary

Reading notes on *The Customer-Base Audit: The First Step on the Journey to
Customer Centricity* (Wharton School Press, 2022). The book's running example is
**Madrigal**, a US catalog→online retailer, analysed over 2016–2019.

---

### The premise (Introduction, Ch. 1)
- Firms know product × time cold, but cannot answer basic customer questions
  ("How many customers do you *really* have? How many one-time buyers last year?
  What share of sales came from new vs existing?"). Revenue is customers pulling
  out wallets; the audit makes that visible.
- A **customer-base audit** = a *systematic, descriptive* review of buying
  behaviour from transaction data, answering **how customers differ** and **how
  their behaviour evolves**. Deliberately **descriptive (and lightly diagnostic),
  not predictive/prescriptive** — the authors reject "sophisticated = better."
- Defining "customer" is genuinely hard (payer vs user vs decider; how long after
  purchase; channel intermediaries). Count **unique** customers, not trips/seats.
  Be explicit and consistent about the definition.

### The data cube and the five lenses (Ch. 2)
- A transaction = **customer × time × product**. Most reporting shows the
  **product × time** face. The audit **pivots to the customer × time face**
  (aggregating over product; product returns in Ch. 8).
- **The five lenses** (Fig. 2.9 classification — rows = # periods, columns =
  period vs cohort):

  | | **Period** (all active in the period) | **Cohort** (customers "born" together) |
  |---|---|---|
  | **One** | **Lens 1** — how different are customers? | **Lens 3** — how does a cohort evolve? |
  | **Two** | **Lens 2** — what changed period-to-period? | **Lens 4** — cohort vs cohort |
  | **Three+** | | **Lens 5** — whole face, health |

- Madrigal: US catalog→online retailer, loyalty program, 2016–2019. Profit =
  spend − direct product costs (simplest of a spectrum). Revenue/profit grew (2018
  & 2019 both +21% rev; +18% / +22% profit). Data path: transaction → order-level
  → customer×period aggregation.

### The "three Ds" and the multiplicative decomposition (used everywhere)
- **Distribution, Decomposition, Decile** are the recurring toolkit.
- **Profit = #customers × AOF × AOV × margin**, where AOF = orders/customer
  (`#trans/#cust`), AOV = spend/order (`revenue/#trans`), margin = profit/spend.
  avg spend/customer = AOF × AOV; avg profit/customer = avg spend × margin.

### Lens 1 — How different are your customers? (Ch. 3)
- 2019: **$583M rev, $280M profit, 3,185,335 customers**, avg spend **$183**,
  **median $113**, **69% below the mean spend**. Distribution is **right-skewed**
  ("reverse-J") — *"purge 'the average customer' from your vocabulary."*
- Transactions: 6.09M total, mean **1.9**, median 1.0; **63% made exactly one**
  transaction, 18% two (**81% ≤ two**); >1% made 10+.
- Avg spend/transaction: **unweighted mean $98** (each customer equal weight),
  median $77, 62% below mean; **weighted (ratio of totals) = $96**. The book
  reserves **"AOV" for the weighted ratio-of-totals** and is explicit these two
  numbers differ (equal only if every customer transacts the same #times).
  Corr(#trans, AOV) = −0.03 → treat as independent.
- Profit: mean **$88**, median **$52**, **69% below mean**, **<1% loss-making**
  (range −$2,470 → $22,139). Margin: mean **46%**, median **48%**, *much less
  skewed* (77% between 40–60%); loss-makers negative.
- **Decile analysis** (two flavours). Equal-customer deciles: **decile 1 = 40% of
  profit; deciles 1+2 = 58%; decile 10 = 1%.** Equal-profit deciles: **top 1% of
  customers = 10% of profit = the bottom 41%**; half of profit from top 15%.
  Decomposition shows higher deciles win on **AOF and AOV (spend), not margin**;
  top deciles differ mostly on **AOF**, low deciles on **AOV + lower margin**
  (cherry-pickers; loss-makers AOF 1.4/AOV $44/margin −19%).
- *"Celebrate heterogeneity."* The base is not chaotic — the variation is stable
  and leverageable; don't over-reach into 1:1 marketing.

### Lens 2 — What changed since last period? (Ch. 4)
- 2018: $483M/$230M/**2.6M** customers → 2019 $583M/$280M/**3.2M**. Per-customer
  metrics are **nearly identical** year-to-year (avg spend $184→$183, AOF
  1.95→1.91, AOV $97.6→$98.2, avg profit $87.84→$87.89) ⇒ **growth is almost
  entirely more customers**, not richer ones.
- **Overlap** (Fig. 4.2): 2018-only **1,638k**, both **982k**, 2019-only
  **2,203k**, total unique **4,823k**. Only **20%** active in both years; only
  **37%** of 2018 customers bought in 2019. **Refuse to call 2018-only "lost" or
  2019-only "new"** — light buyers skip years (resolved later in Lens 5: 83% of
  2019-only really were new).
- **Additive** decomposition of profit (both-years vs 2018-only vs 2019-only) +
  **multiplicative** temporal decomposition (Table 4.1): both-years group has
  **much higher AOF (2.9/2.8)** than one-year groups (1.4/1.5) — a **selection
  effect** (light/one-time buyers can't appear in both years). Both-years profit
  fell $5.5M, mostly via AOV ($93→$90).
- Then a **modified decile analysis with common cut-offs across both years** +
  a **decile-migration** matrix; and an **up-down** analysis (flag profit/#trans/
  AOV/margin up-vs-down for both-years customers). Strategic point: period-to-
  period "declines" are often natural — judge programs on *future* expectations.

### Lens 3 — How does a cohort evolve? (Ch. 5)
- Q1/2016 cohort (**294,450**). Weekly revenue spikes during the acquisition
  quarter then collapses to <20% of peak (first-purchase vs repeat split).
- **Revenue = cohort size × % active × AOF × AOV** (Fig. 5.3). Decline is driven
  **primarily by the falling % active**, not spend; AOF drifts *up* slightly, AOV
  drifts *down* (dominant), so spend/active is roughly flat; Q4 seasonal spikes.
- **Annual buying patterns** (16 Y/N sequences): **45% never make a 2nd purchase
  ("N-N-N-N") by end 2019**; +15% "Y-N-N-N" ⇒ **60% did not buy in 2017–19**; only
  **7% "Y-Y-Y-Y"**; **26% have a gap-then-return** pattern ⇒ *inactivity ≠ lost.*
- **Annual repeat-buying rates**: 2016→17 **25%**, 2017→18 **56%**, 2018→19
  **57%** (each conditioned on prior-year activity). 39% of 2018-active were
  inactive in 2017.
- **Time to 2nd purchase**: 55% eventually repeat; 17% same quarter, 38% within a
  year, 21% within 16 weeks; curve flattens hard ("early or never"). **Time-to-
  next** family (1→2, 2→3, …, 9→10, Fig. 5.8): same shape, rising faster for
  higher purchase numbers — **heterogeneity** (heavy buyers), not causation
  ("bribing" a 2nd purchase doesn't change propensity).
- **Value to date (VTD)** = undiscounted 4-yr profit: mean **$171**, median
  **$78**, 73% below mean. VTD decile 1 = 1% of cohort, **AOF 36.3**, AOV $136,
  avg VTD $2,441; top 5 deciles (11% of cohort) = half of VTD (heterogeneity
  **stretches** over time). **AOF varies 26× across deciles, AOV only 2×.**
  Table 5.2: annual % active by VTD decile (decile 1: 100/95/94/90; decile 10:
  100/7/6/5) — but in absolute terms more decile-10 customers are active than
  decile-1 (don't write off low-value customers).
- **RFM**: R = recency (last-purchase quarter), F = frequency (#trans over 4 yrs),
  M = avg profit/transaction. Only 52 of 64 cells feasible (freq 1 ⇒ recency Q1).
  Most "action" is in **R and F, not M** — the ordering of the letters is
  deliberate: **recency & frequency > monetary**.

### Lens 4 — Comparing cohorts (Ch. 6)
- Compare **two cohorts at a time**, controlling for **cohort size**; decompose
  profit = size × %active × AOF × AOV × margin.
- Two flavours: (a) **Q3/2016 vs Q4/2016** — same year, different quarter →
  seasonality confound; (b) **Q4/2016 vs Q4/2017** — same quarter, different year
  → clean like-for-like.
- **Left-align by cohort AGE (quarters since acquisition), not calendar time**
  (align same-season cohorts). Aligned, Q4/2016 & Q4/2017 age almost identically
  in %active/AOF/AOV. The **margin** difference looked large *aligned* but
  disappeared *time-aligned* → it was a **firm-wide pricing/promotion change over
  time, not a cohort-quality difference.** Cross-cohort stability is normal and
  good; degradation is an early-warning signal ("boring is good; where there's
  smoke there's fire").

### Lens 5 — How healthy is the base? The C3 (Ch. 7)
- Decompose annual performance by **annual acquisition cohort** (pre-2016 + 2016–
  2019). The stacked **"C3" (Customer Cohort Chart)** of profit by acquisition
  year (Fig. 7.2) is the signature tool. Much of each year's profit comes from
  *that year's* acquisitions (2016: 64%; 2019: 47%); a cohort's profit drops
  sharply the year after formation, then tapers.
- **Acquisition** (Fig. 7.3): down 15% in 2017 (explains the anemic year); ~45%
  of all acquisition happens in Q4 (holiday reliance — mixed blessing).
- **Active customers by cohort** (Table 7.2): totals 2,063k / 2,153k(+4%) /
  2,620k(+22%) / 3,185k(+22%) — **growth in the active count tracks revenue &
  profit growth**, and avg spend/active ($182–186) and avg profit/active ($88–91)
  are flat ⇒ **growth is driven by base *size*, not per-customer value.** 83% of
  the 2.2M "2019-only" customers were genuinely new.
- **Two carefully-distinguished quantities**: *% of a cohort active in a year*
  (the diagonal — includes one-timers, low ~25–28%) vs the **repeat-buying rate**
  (% active in year *t* also active *t+1*, conditional — Table 7.4; older cohorts
  ~50–57%, rising toward steady state as one-timers "shake out"; overall = a
  weighted average). **Aggregate AOF/AOV/margin (Table 7.5) mask cohort
  differences — always decompose to cohort level first.**
- **Back-of-envelope planning**: given acquisition + repeat rates, project how
  many *new* customers are needed to hit a growth target — the audit's bridge to
  planning. Health framed as **Acquisition / Retention / Development**.

### Ch. 8 — Bringing back the product dimension
- Madrigal: 12,142 products, 23 categories. Higher-value deciles buy in **more
  categories / more SKUs**; their higher AOV comes from **more units per basket**
  (mostly more units *per category*, not more categories per trip); price/unit is
  flat across the top deciles.
- **Category profit = #active customers × category penetration (% active in
  category) × ACOF × ACOV × category margin** (distinguish category-level ACOF/
  ACOV from firm-level AOF/AOV). 53% of customers bought only one category (cf.
  63% one transaction). Co-purchasing/duplication, sole-category buyers, "most
  common additional category." **Sign-flip decisions**: a category that looks
  loss-making on a product P&L can be the *acquisition doorway* for the best
  customers (La Perla; low-margin beds as trigger purchases).

### Ch. 9 — Variations on a theme
- **Noncontractual vs contractual.** Madrigal is **noncontractual** (silent
  attrition — you never observe "death"). Contractual/subscription: churn is
  observed → **survival curve** (monotone decreasing) replaces %active;
  **retention rate = renewed/at-risk**. **Aggregate retention rate is misleading**
  — a weighted average across cohort ages, driven by the *acquisition* pattern,
  not retention per se (same trap as Table 7.5).
- **"Be Wary of the 'R' Word."** *Only use "retained"/"retention" in a
  contractual setting.* In noncontractual settings, someone inactive one period
  can buy the next, so they were never "lost"/"retained." Calling %-active or the
  cohort-activity ratio a "retention rate" is **bad practice** — the right names
  are **"repeat-buying rate"** and **"% of cohort active."** Label axes carefully.
- Also: different notions of **acquisition** (install→register→subscribe funnels,
  freemium), analysing **usage** (not just spend), extra dimensions (channel,
  device, demographics; cohorts by channel).

### Conclusion — From audit to action
- Customer-centric firm = customer as unit of analysis; **acquisition / retention
  / development** growth framework; decisions through long-term customer profit;
  acts on the fact that customers are unequal.
- **Customer-centric planning**: how much revenue/profit comes from existing
  customers, and how many new ones must "fill the gap." Cohorts (fixed membership)
  are foundational for planning; persona/RFM segments drift.
- **Align acquisition spend to value** (VTD by channel/keyword): averages mislead
  (pay-TV: *Times* 4× CAC but 5× value; Google: £12 avg CAC / £95 avg VTD hid most
  keywords >£30 CAC / <£30 value). **"Acquire customers, not transactions"**
  (Lands' End: "not a customer until the 2nd purchase"; nursery/welcome programs).
