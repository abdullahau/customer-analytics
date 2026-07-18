# Ehrenberg, *Repeat-Buying: Facts, Theory and Applications* — reading summary

**A.S.C. Ehrenberg** (London Business School). New Edition, Charles Griffin & Co. (London) /
Oxford University Press (New York), **1988**. First published North-Holland, 1972; the 1988
re-issue leaves the original text essentially unchanged but adds **Chapter 13 (The Dirichlet
Model)** and **Appendix C**. 387 pp., six parts, thirteen chapters, three appendices.

> *"Of the thousand and one variables which might affect buyer behaviour, it is found that nine
> hundred and ninety-nine usually do not matter. Many aspects of buyer behaviour can be predicted
> simply from the penetration and the average purchase frequency of the item, and even these two
> variables are interrelated."* — the book's epigraph, and its entire thesis.

Companion volume: [Data Reduction — reading notes](data-reduction-summary.md), Ehrenberg's book on
*method*. The two are meant to be read together — *Data Reduction* Ch. 10 derives one of this
book's central laws from scratch as a worked illustration of how theory emerges from facts.

---

## 0. What kind of book this is

Not a marketing textbook and not a "how to change consumer behaviour" book. Ehrenberg is explicit
that it "deals with a part of the *context* of marketing management rather than with the execution
of marketing management. (It is not so much a book on how to build aeroplanes, as it were, but on
certain elementary strands in aerodynamics.)"

The programme is stated in the Foreword and is worth stating precisely, because it is the opposite
of the usual modelling order:

1. **Establish empirical generalisations first.** Find patterns that hold across brands, products,
   countries, demographic sub-groups, and analysis-period lengths.
2. **Then model them** in mathematical form.
3. **Then interrelate the models**, so that different findings explain each other.

The whole of the repeat-buying theory is compressed by Ehrenberg into one expression — the
probability generating function of the **multivariate NBD**:

```
{ 1 + a Σᵢ Tᵢ(1 − uᵢ) }^(−k)
```

"This one expression essentially covers all that is contained in this book about repeat-buying."

The theory is **descriptive**: it says *how* consumers behave and on what that does (and does not)
depend, not *why*. Ehrenberg's position is that you cannot explain behaviour you have not yet
described.

---

## Part I — Introduction

### Ch. 1 — Buyer Behaviour

**The data.** Continuous **consumer panels** — the same households recording all purchases in a
product-class, week by week, over a year or more. UK samples up to ~5,000, US up to ~8,000
(AGB's Television Consumer Audit, Attwood, Research Bureau, MRCA, Chicago Tribune). Ehrenberg
rates well-run panels "amongst the most fully checked and reliable data-sources available in the
social sciences," and disposes of the measurement-error objection with a line from Chatfield et
al. (1966):

> *"If the purchasing claims more or less represent actual purchasing behaviour, we are discussing
> some empirical regularities in sociology and marketing, but if they refer to imaginary purchases,
> then we are discussing regularities in psychology and as such they might be deemed the more
> remarkable."*

**Four analysis decisions**, each justified *empirically* (because it worked), not a priori:

| Decision | Alternative rejected | Why |
|---|---|---|
| Analyse **one brand at a time**, then integrate | product-class first, then brand-choice | Repeat-buying of Brand X can be predicted without knowing what else its buyers bought. Ehrenberg calls this "one of the most fundamental empirical discoveries treated here" — and its theoretical justification arrived only *ten years later* (§11.5). |
| **Purchase occasion** as the unit | units bought, money spent | Lets multi-unit purchases and multiple pack-sizes be handled by one theory. Sales are recovered at the end by multiplying back up. |
| **Fixed time-periods** | purchase sequences (AABAB…) | Consumers' sequences get out of phase; no generalisable results have ever come from that route. Time-periods also tie in with all other marketing data. |
| **Stationary (no-trend) conditions** | modelling dynamics | Most brands in most markets are near-stationary most of the time; and you cannot interpret change without a no-change baseline. |

**The two variables.** Everything reduces to:

- **b — penetration**: the proportion of the population buying the item at least once in the period.
- **w — purchase frequency**: the average number of purchases per buyer in the period.

with the decomposition

```
Sales = N × b × w × (packs per purchase) × (size or price per pack)
```

Only `b` varies much between brands. The other components are approximately constant — which is
why penetration is the whole game.

**Stationarity** is defined narrowly: no trend in *this item's* aggregate sales. It does **not**
mean a quiet market; it means the net effect of all the varying marketing inputs on this brand
was nil. The theory "tells us more or less all about stationary buyer behaviour except for one
thing, namely why one brand has more buyers than another."

### Ch. 2 — Regularities of Behaviour

The fundamental finding, demonstrated on **20 varied case-histories** (Table 2.1: food and
non-food, UK and US, 1951–1966, periods 1–24 weeks, penetrations 1%–50%): a handful of
repeat-buying indices all vary systematically with **`w` alone** — not with the brand, the
product-field, the country, the period length, the market share, advertising, or price.

The table is laid out sorted by `w`, so the pattern is visible without any arithmetic. Six
regularities emerge, and each has a one-line formula in the **LSD** (Logarithmic Series
Distribution) version of the theory, which needs only one parameter **q**, itself fixed by `w`:

| Empirical regularity | LSD formula |
|---|---|
| % of sales from repeat-buyers (bought in previous period too) | **q** |
| % of sales from buyers making ≥ 2 purchases | **q** |
| ⇒ these two are numerically equal (observed to within ~3 pts) | — |
| % of sales from buyers making ≥ r purchases | **q^(r−1)** |
| purchase rate of "new" buyers (didn't buy last period) | **q/ln(1+q) ≈ 1.4**, a near-constant |
| shortfall for r ≥ number of weeks in the period | the "shelving" effect (§7.9) |

`q` is related to `w` by `w = −q / [(1−q) ln(1−q)]`, which cannot be inverted algebraically —
hence Ehrenberg's lookup tables (Appendix B) — but for `w > 2`,

```
q ≈ (w − 1.4) / (w − 1.15)     accurate to ±0.01
```

**Worked application (§2.4): a seasonal trend for Brand M.** Peak-quarter sales rose from 36 to
48 purchases/100 households. Observed: 8% repeat-buyers × 4 purchases = 32; 8% "new" buyers ×
2 = 16. Stationary NBD norms predicted 8% repeat-buyers × 4 = 32 (exactly as observed) and 4%
new buyers × 1.4 ≈ 4. Conclusion: **the entire seasonal uplift came from extra new buyers**;
the year-round buyers were completely unaffected by the season. The market is segmented into
all-year buyers and peak-season-only buyers. This is the archetype for the whole book: the model
supplies the counterfactual.

---

## Part II — Repeat-Buying

### Ch. 3 — The Repeat-Buying Structure of a Market

A full standardised audit of one product-field (five leading brands A–E, 75% of the market, 48
weeks), presented as ten tables of **Observed "O" vs Theoretical "T"**. This chapter is the model
for what the repo's `analyses/` essays do, and is worth mining directly as a table specification:

| Table | Content | Typical finding |
|---|---|---|
| 3.1 / 3.1a | Penetration by quarter; **penetration growth** over 1, 4, 12, 24, 48 weeks | 24 predictions from 1% to 80% fit to ~1.5 pts average |
| 3.2 / 3.2a | Purchase frequency `w` by quarter and by period length | `w` ≈ 3 per quarter for *every* brand, though shares differ 10:1 |
| 3.3 | **Packs per purchase** | ~1.05 for all brands, all buyer weights |
| 3.4 | Distribution of light/heavy buyers (% making 1, 2, 3, … purchases) | NBD fits brands well; product-class slightly too regular |
| 3.5 | **Sales importance** of heavy buyers | ~80% of a brand's annual sales from its ≥6-times buyers |
| 3.6 / 3.6a | Incidence of repeat-buyers, period to period | Brand A: 78% observed vs 77% predicted |
| 3.7 | Purchase frequency *per repeat-buyer* | close to norms even where the *count* of repeat-buyers is off |
| 3.8 | Purchase frequency per **"new" buyer** | norm ≈ 1.4; excess here revealed "jag"-buying |
| 3.9 | Repeat-buying in **non-consecutive** periods | Should equal the consecutive rate — and does. No erosion. |
| 3.10 / 3.10a | **Conditional trend analysis**: repeat-buying split by previous non-, light-, heavy-buyers | The decisive diagnostic |

The payoff of Table 3.10: three brands showed a shortfall of repeat-buyers. Conditional analysis
showed the shortfall was entirely among **once-only** buyers — heavy buyers repeated at exactly
the normal rate. The apparent "loss of loyalty" was in fact an **excess of occasional buyers**
(seasonal brand-switching), "something with radically different marketing implications."

Note the presentation discipline throughout: **"results are usually set out to at most two
significant figures."**

### Ch. 4 — Basic Theory

Three forms of repeat-buying: (i) more than one purchase within a period, (ii) buying in more
than one period, (iii) more than one unit per occasion (bypassed by using purchase occasions).

**The NBD.** Distribution of purchases in a period, parameters mean `m` and exponent `k`
(with `a = m/k`):

```
p_r = (1 + m/k)^(−k) · Γ(k+r) / [Γ(r+1)Γ(k)] · (m/(m+k))^r
variance = m(1 + a)
```

**Fitting by "mean and zeros"** — the observed mean `m` and the observed proportion of non-buyers
`p₀`, since market research tabulations routinely give exactly those two numbers and nothing else:

```
p₀ = (1 + a)^(−m/a)          solved iteratively for a (or read from Appendix B Table B.3
                              via the transform c = m / ln p₀)
```

This is **≥ 90% efficient** for typical consumer data — far better than method of moments (which
can be under 50% efficient) and vastly less laborious than maximum likelihood. Existence
condition: `m > −ln p₀`. Forward recursion generates the `p_r`.

**The underlying stochastic model (§4.5)** — a two-dimensional model, one dimension time, one
consumers:

- each consumer buys as a **Poisson** process with their own long-run rate μ;
- μ is distributed **gamma** across consumers, with exponent `k`.

("In the modern literature, this type of model tends now to be referred to as a *mixed Poisson*.")
This one model yields the NBD in any single period, *and* the formulae relating different period
lengths, *and* period-to-period repeat-buying.

**The LSD approximation (§4.4).** Where `b ≲ 0.2`, the non-zero part of the NBD is well
approximated by the one-parameter Logarithmic Series Distribution:

```
p'_r = q^r / [ r · (−ln(1−q)) ]        for r ≥ 1
tail share of sales from buyers of ≥ r  =  q^r
```

The LSD is not an alternative to the NBD but a limiting case of it. Its conceptual importance:
it shows that repeat-buying is **independent of how the population of potential buyers is
defined** — which matters a lot when "the population" is arbitrary (all adults? all drivers?
all car owners?).

**§4.10 — the honest summary.** Two brands with the same `w` have the same repeat-buying
patterns, full stop. It is *not* a case of "my brand is different." There is **no erosion of
repeat-buying over time**: "lapsed" and "new" buyers are not leaving or entering the market,
they are simply infrequent buyers. And:

> *"All this is not to say that the NBD model is fundamentally 'true'... neither the Poisson- nor
> the Gamma-distribution assumption can be altogether right. Some quite fundamental reformulation
> is required... The justification of the theory is therefore not the absolute truth of the theory
> in itself but that it works in practice."*

---

## Part III — Practical Applications

### Ch. 5 — Some Practical Applications

- **§5.2 American vs British repeat-buying.** Re-analysis of George Brown's published Chicago
  Tribune panel data (1951), 19 near-stationary cases. Predictions of repeat-buyer counts, their
  rates, sales share, and new-buyer rates all fit closely. Conclusion: US and UK repeat-buying
  habits are the same. The methodological point matters more than the result: *because* a
  validated model existed, no matching of American conditions to British ones was needed —
  "much more efficient than reference back to raw data or the use of controlled experimentation."
- **§5.3 Clothing** (stockings, knitting-yarn, socks) — the boundary cases. Stockings behave
  NBD-like. Knitting-yarn shows wildly excessive week-to-week repeat-buying (yarn for one garment
  bought in instalments) which returns to normal over 2-week periods. Socks show almost **zero**
  week-by-week repeat-buying: the "dead period" between purchases is longer than the analysis
  period. The general lesson: the NBD fails below a product's minimum inter-purchase interval.
- **§5.4 A new Brand R.** Quarterly repeat-buying 21% vs a norm in the high 30s. The diagnostic
  was **non-consecutive** quarters: repeat-buying fell to 11% two quarters later, whereas for a
  healthy brand it should be unchanged. The brand was living on first-time triers and would
  exhaust the population. Management withdrew it before sales collapsed.
- **§5.5 Product S.** Below-normal repeat-buying for every brand. Management hypothesised the
  new large pack-sizes; the analysis showed the reverse — large/giant were normal (42% vs 38%),
  small/medium were the problem (37% vs 52%) — and conditional analysis showed even that was an
  **excess of occasional buyers** caused by price-cutting, not a loyalty failure.
- **§5.6 Brands M₅ and M₆.** Genuine segmentation: repeat-buying 10+ points low for two brands
  sharing a product characteristic, with the shortfall exactly made up by extra switching *between*
  those two. Ehrenberg stresses how **rare** this is.

### Ch. 6 — Further Applications

- **§6.2 Evaluating a consumer promotion.** A banded giant-pack deal; February sales +25%. Seven
  specific marketing questions. NBD norms from January (11% buying, `w`=1.9) predict 58%
  repeat-buyers at 2.3 each and 5% new buyers. Observed: 72% repeat-buyers and 7% new buyers. So
  the deal did both — but conditional analysis (Table 6.2) shows the repeat-buying gain was
  concentrated among *previously light* buyers (63% vs a 43% norm). The key methodological claim:
  the theory supplies the control group, so the evaluation is **cheaper than a controlled
  experiment and can be done after the event**.
- §6.3 a new-product launch in test market; §6.4 the effect of irregular panel reporting;
  §6.5 quick standard errors.

---

## Part IV — Mathematical Theory

### Ch. 7 — The NBD Theory

- **§7.2 Compound Poisson.** Support for the model comes not from the single-period fit (several
  processes can produce an NBD) but from the many *other* deductions that also hold. The
  Poisson-with-LSD-amounts alternative (Quenouille, Williamson & Bretherton) is rejected because it
  requires `a` constant and `k` varying across period lengths — empirically the opposite is true.
  On heterogeneity vs contagion ("proneness" vs "learning", the old accident-statistics
  controversy): the evidence points clearly to **heterogeneity**.
- **§7.3** NBD probability generating function `(1 + a − au)^(−k)`; mean `ka = m`; variance `m(1+a)`.
- **§7.4 The multivariate NBD** (due to G. J. Goodhardt) — the technical heart of the book:

  ```
  { 1 + a Σᵢ₌₁ᵗ Tᵢ(1 − uᵢ) }^(−k)
  ```

  for any number of periods of any lengths. Every repeat-buying and penetration-growth formula in
  the book is a coefficient in the expansion of this. It **partitions**: conditional on `(r₁…r_s)`
  purchases in the first `s` periods, purchases in the remainder are again multivariate NBD with

  ```
  m' = (k + Σrᵢ)·(m/(m+k)),      k' = (k + Σrᵢ)
  ```

- **§7.5 `k` is invariant to period length.** Under stationarity `m_T = Tm`, so `a_T ∝ T`, while
  **`k` stays constant** — `k` is the gamma-heterogeneity parameter and describes long-run
  differences between consumers, which do not depend on how long you look. Table 7.1 verifies this
  over 4/8/12/24-week periods for 15 brands. This is the empirical linchpin: *"Most of the
  repeat-buying formulae from the NBD model depend explicitly on k being constant in this way."*
  It follows that

  ```
  b_T = 1 − (1 + aT)^(−k)          w_T = Tm / b_T
  ```

- **§7.6 Repeat-buying in two periods.** With `b_R` = proportion buying in both:

  ```
  b₂  = 1 − (1 + 2a)^(−k)                      (combined double period)
  b_R = 2b − b₂ = 1 − 2(1+a)^(−k) + (1+2a)^(−k)
  b_N = b_L = (1+a)^(−k) − (1+2a)^(−k)         ("new" and "lapsed")
  m_N = m / (1+a)^(k+1)
  m_R = m · { 1 − (1+a)^(−k−1) }
  ```

  **Conditional trend analysis**: consumers making exactly `r` purchases in period I have an NBD in
  period II with mean `(k+r)·a/(1+a)` and exponent `(k+r)`; the proportion of them buying again is
  `1 − {1 + a/(1+a)}^(−k−r)`. This is the formula behind Tables 3.10, 5.11 and 6.2 — the single
  most diagnostically useful result in the book.

- **§7.7 Aggregating NBDs.** Two NBD variables sum to an NBD **if and only if** they are
  independent and `a_x = a_y`. Theoretically a severe constraint; empirically both conditions turn
  out to hold closely (Ch. 10–11), which is why brands aggregate to product-classes and pack-sizes
  aggregate to brands. Sub-group NBDs (by household size, etc.) also combine acceptably, because
  between-group differences are small relative to within-group scatter.

- **§7.8 The variance discrepancy.** Known since Ehrenberg (1959): for large variances the fitted
  NBD's variance exceeds the observed one, and the discrepancy is itself highly regular:

  ```
  σ − s ≈ m      (later work suggested σ − s ≈ m/2);   equivalently  σ/m − s/m ≈ 1
  ```

  Systematically **not** explained by: the Poisson assumption, Erlang inter-purchase times, the
  marketing mix, non-stationarity, excess heavy buyers, or measurement error.

- **§7.9 Shelving.** The real cause. Purchases cluster at or just below the number of *weeks* in
  the period, and there are consistently **too few** buyers above that — a shelf-like
  discontinuity — because for most grocery products the minimum inter-purchase interval is about a
  week. Few people buy more than 12 times in 12 weeks. Because it is the tail that is missing, the
  effect on the variance and on heavy buyers' sales share is large even though the headcount is
  small. Conclusion: **the NBD breaks down only at the boundaries** — very short periods and very
  high purchase counts.

### Ch. 8 — The LSD Theory

The LSD arises as a limit (Fisher, Corbett & Williams 1943): as `k → 0` and `m → 0` with
`a = m/k` tending to a non-zero limit, the non-zero part of the NBD tends to the LSD. Table 8.1
demonstrates the striking corollary: **holding the 388 observed buyers fixed and varying the
notional non-buyer count from 362 to 19,612**, the NBD keeps fitting well and `m/k` converges
(here to ~6.7). The number of non-buyers is largely irrelevant to the fit. Practical range for a
good LSD fit: `b < 0.2` for any `w > 1.5`, or `b < 0.4` for `w > 4`. Not suitable for
heavily-aggregated product-class data, where `k` is much larger.

---

## Part V — Buying More than One Brand

### Ch. 9 — The Multi-Brand Structure of a Market (empirical)

The same product-field as Ch. 3, now brand-by-brand. Headline findings:

- **Buyers of a brand buy other brands far more often than they buy the brand itself.** Over
  48 weeks: ~7 purchases of the brand vs ~15 of other brands. Across 10 product-fields: 7 vs 20,
  totalling 27 product purchases per average buyer. "Except perhaps in rather short periods, it is
  therefore generally wrong to think of buyers of one's brand as being people who buy only, or even
  just mainly, that brand."
- **Sole (100%-loyal) buyers** decay predictably with period length and vary little across brands:
  ~70% of a brand's weekly buyers, ~50% in 4 weeks, ~30% in a quarter, ~10% in a year.

### Ch. 10 — Multi-Brand Buying Theory

The four laws of this chapter are the empirical foundation of everything the Ehrenberg-Bass
tradition later built.

**1. Purchase rates barely vary across brands (§10.2–10.3).** `w_X ≈ w_Y` for brands; likewise
across pack-sizes of a brand, and across *sole* buyers of different brands. The sharpened version:

```
w_X (1 − b_X)  =  w_Y (1 − b_Y)  =  constant
```

Small brands' buyers buy slightly less often — a *double* disadvantage on top of having fewer
buyers. Ehrenberg names this **Double Jeopardy** (crediting McPhee 1963), and stresses it as a
constraint on marketing action: you cannot get existing buyers to buy much more, because no brand
has ever managed it.

**2. Product rates are constant (§10.4).** The average number of *category* purchases per buyer of
brand j is ~15–16 regardless of which brand j is, and regardless of pack-size. So there is no
demand-side reason why a brand's buyers couldn't buy more of it — "but they do not do so, and
different brands find it virtually impossible to break through this constraint."

**3. The Duplication of Purchase Law (§10.5).**

```
b_XY = D · b_X · b_Y          equivalently      b_X|Y = D · b_X
```

with a single `D` for all brand pairs in the field, best estimated as `D = Σb_XY / Σb_X b_Y`.
Average residual ~1 percentage point. Buyers are shared **in proportion to penetration**, not
according to positioning. Where genuine segmentation exists (Table 10.9: two manufacturer-groups
with D = 3.5 / 2.5 within and 1.5 between), it appears as *"local densities superimposed on the
underlying duplication pattern."* Known systematic failure: the model **over-predicts** duplication
for very high-penetration brands (a defect of the model, later addressed by the Dirichlet).

**4. Sole buyers (§10.7).** Their purchase rate barely varies by brand, and their *incidence*
follows

```
b_sX · (1 − b_X) / b_X  =  constant       i.e.   b_sX ∝ b_X/(1 − b_X)
```

"This is another Double Jeopardy pattern."

**Time-trends (§10.8).** The `D` coefficient rises with period length for substitutable brands
(from < 1 in a week — short-period "dead-period" inhibition — to ~1.5–2 in long periods) but
**falls** for different *varieties* of one brand, which are complementary rather than substitutable
and may both be bought on a single occasion. Purchase-rate growth follows two different laws:

```
brand rates:   (w_T − 1) ≈ T^0.82 · (w_1 − 1)
product rates: (w_pT − 1) ≈ T · (w_p1 − 1)      — sole buyers follow this one
```

---

## Part VI — R & D

### Ch. 11 — The Growth of Theory

**§11.2 Models without facts.** A blunt critique of the then-dominant approaches:

- The **Howard–Sheth** theory: "there is no detailed evidence of just how any of these ideas relate
  to any specific facts of consumer behaviour." When it was empirically tested, the authors
  concluded that the test "put extreme pressure on the *data*" — Ehrenberg's italics-equivalent
  aside: "(not on the model!)". His test of any such theory: does it predict, contradict, or even
  *relate to* the finding that buyers of a small pack buy it about as often as buyers of the large
  pack buy that?
- **Kuehn's learning models**: Frank (1962) showed long ago that mere population heterogeneity
  produces the *appearance* of learning. Under stationarity, people who last bought X were more
  frequent buyers of X before and will be after — no learning required.
- **First-order Markov brand-switching**: assumes switching probabilities are properties of the
  specific brand-pairs, invariant to shares. "Something like the exact opposite" is true — switching
  depends on penetration and purchase frequency, not on brand identity.

**§11.3 Facts without models.** Tens of millions spent annually on panels, used almost entirely for
aggregate share-tracking and demographic profiles, making "virtually no explicit use of the
continuing panel nature of the data." (In TV audience measurement, ~500 million panel-type
measurements a year of which "499½ million were not used for panel-type analyses.")

**§11.5 Reasons why — the integrative step.** This section is the intellectual climax. Three
initially separate empirical findings are shown to imply one another:

Given (A) product rates constant across brands, (B) duplication `b_XY = D b_X b_Y` implying
near-zero correlation between buying X and buying Y, and (C) `w_X.Y ≈ w_X` — write out the average
product purchases per buyer of X and per buyer of Y, set them equal, substitute independence,
cancel, and you get

```
w_X (1 − b_X) = w_Y (1 − b_Y)
```

So Double Jeopardy is not a separate law; it is a **consequence** of category-rate constancy plus
brand-independence. Ehrenberg also notes:
- the same argument with the observed coefficients gives `w_X(1 − CDb_X) = w_Y(1 − CDb_Y)`, with
  `C ≈ 0.8–1.0` and `D ≈ 1.4`, which is barely different — hence the simpler `(1−b)` form is used;
- `a_X ≈ a_Y` (from `w_X ≈ w_Y`) gives Goodhardt's alternative `w_X(1 − ½b_X) = w_Y(1 − ½b_Y)`;
- the near-zero between-brand correlation also **explains** why single-brand NBD analysis works at
  all without reference to other brands — the coefficients on those other brands would be ~0 anyway.
  The explanation arrived ten years after the fact it explains.

**Hinshelwood's three stages** (quoted here and again in *Data Reduction* Ch. 10) as the model for
how this literature progresses:

1. *"gross over-simplification, reflecting partly the need for practical views and even more a
   too-enthusiastic aspiration for the elegance of form"* — e.g. "the purchase rates are constant";
2. *"the symmetry of the hypothetical system is distorted and the neatness marred as recalcitrant
   facts increasingly rebel against uniformity"* — the trends and discrepancies;
3. *"a new order emerges, more intricately contrived, less obvious and with its parts more subtly
   interwoven, since it is of nature's and not of man's conception."*

**§11.6 Discrepancies** — honestly catalogued: the variance discrepancy; the total breakdown in
very short periods; poor fit for "very frequently-bought" items (bread, milk, cigarettes) and
sometimes for the total product-class.

### Ch. 12 — Developing Prototype Applications

Argues for deliberate investment in prototype applications, since the recurrent marketing questions
("how do I increase sales?", "what does advertising do?") are by definition recurrent and therefore
need generalisable rather than ad hoc answers. §12.4 "The Way Sales Increase": since `w` is
constrained, sales growth must come through `b`.

### Ch. 13 — The Dirichlet Model *(new in 1988)*

An edited version of **Goodhardt, Ehrenberg & Chatfield, "The Dirichlet: A Comprehensive Model of
Buying Behaviour", *JRSS-A* 147(5), 1984, 621–655** — read before the Royal Statistical Society
with the discussion. It integrates *all* of Parts I–IV (repeat-buying) and Part V (multi-brand)
into a single model with `g + 2` parameters.

Four assumptions: (B1) Poisson category purchasing, (B2) gamma-distributed rates → **NBD** with
mean `MT`, exponent `K`; (A1) multinomial brand choice, (A2) **Dirichlet(α₁…α_g)** choice
probabilities → Dirichlet-multinomial; (C) independence between the two. Key properties: the
**additivity property** (brands combine into super-brands, so brand-j-vs-rest reduces to a
beta-binomial), estimation of `S = Σαⱼ` by iterative matching of theoretical to observed
non-buyers, and time extrapolation in which **only `M` scales** (`M → MT`) while `K` and `S` are
invariant.

*This repo's* treatment of the Dirichlet — the model spec, the brand performance measures, the
empirical laws it predicts, and the planned essay locations — lives in
[README.md § The other tradition](../../../README.md) and in [CLAUDE.md](../../../CLAUDE.md), so it is not repeated
here.

---

## Appendices

- **Appendix A — Calculations for an individual brand.** A fully worked numerical example (Brand E,
  12-week base period, `m = .21`, `k = .0396`, `a = 5.34`) computing penetration growth and purchase
  frequency for 1/4/24/48-week periods **three ways** — the NBD formula, the LSD formula, and the
  approximation `b_T/b = Tw / [1 + (w−1)T^0.82]` — showing all three agree. This is the most
  directly implementable part of the book.
- **Appendix B — Tables.** `q` against `w` for the LSD; the NBD `a` against `c = m/ln p₀`
  (Chatfield 1969); natural logarithms.
- **Appendix C — Calculations for multi-brand buying** *(new in 1988, by Mark Uncles).* The
  step-by-step **Dirichlet estimation algorithm**: build the NBD `P_n` with a truncation rule,
  then for each brand iterate on `S` (start at 2; double or halve depending on whether the
  estimated `p₀` overshoots; then interpolate) until the estimated and observed `p₀` agree; then
  form the share-weighted average `Ŝ = Σ(Sⱼmⱼ/M)/Σ(mⱼ/M)`, dropping irregular brands. The worked
  example converges in ~5 cycles. **This is precisely the procedure implemented in
  `ndb-dirichlet/NBDdirichlet-main/nbddirichlet/dirichlet.py`** — and the reference against which
  that implementation's `_estimate_S` should be checked.

---

## Conditions under which the results have been found to hold

From Table 1 of the 1988 Preface — the range of generalisation *is* the claim:

- **Product-fields:** aviation fuel, biscuits, breakfast cereals, butter, canned vegetables, cat
  and dog foods, cocoa, coffee, confectionery, convenience foods, cooking fats, cosmetics,
  detergents, disinfectants, flour, food drinks, gasoline, household soaps and cleaners, instant
  potatoes, jams, margarine, motor oil, polishes, processed cheese, refrigerated dough, sausages,
  shampoos, soft drinks, soup, take-home beer, toilet paper, toilet soap, **TV programmes**.
- Leading brands in each field; large, medium and small pack-sizes.
- Retail chains; individual stores; brands within chains.
- Great Britain, Continental Europe, USA, Japan; demographic sub-groups; **1950–1985**.
- Analysis periods from **1 week to 12 months**.

---

## What this means for this repository

**Where it sits.** This is the founding text of the **Ehrenberg–Bass** branch described in
[README.md § The other tradition](../../../README.md) — category-level and multi-brand, driven by panel
aggregates (`b`, `w`, market share), as against the Fader–Hardie customer-base branch that drives
most of `notebooks/`.

**Direct overlaps with existing work.**

- The NBD of Ch. 4 and 7 is *the same NBD* as `notebooks/models/purchasing/nbd-overview` — Poisson
  × gamma, the same forward recursion, the same χ² check. What differs is the question asked of it.
- "Fitting by mean and zeros" is a genuinely different estimator from the MLE-on-frequency-counts
  used in the repo's essays, and Ehrenberg's efficiency argument for it (≥90%, vs <50% for method
  of moments) is worth reproducing.
- Conditional trend analysis (§7.6) has no counterpart in the repo and is the sharpest diagnostic
  in the book.

**Things worth lifting.**

1. **The Ch. 3 audit table set** as a specification for a `notebooks/analyses/` essay — ten tables,
   each Observed vs Theoretical, two significant figures.
2. **Appendix A's worked calculations** as the test fixture for any NBD helper in `lib/`.
3. **Appendix C's `S` iteration** as the reference implementation for a `lib/models/Dirichlet.py`.
4. **The `w(1−b)` derivation (§11.5)** as a self-contained essay — it is short, purely algebraic,
   and it is the cleanest available demonstration of "heterogeneity, not individual dynamics."

**A caution to preserve.** Ehrenberg is scrupulous about where the model fails: short periods,
heavy-buyer tails ("shelving"), very frequently-bought products, and the total product-class. Any
essay written from this material should carry those boundaries, not just the successes.
