# Ehrenberg, *Data Reduction* — reading summary

**A.S.C. Ehrenberg**, *Data Reduction: Analysing and Interpreting Statistical Data*.
John Wiley & Sons. Preface dated **January 1974**; corrected reprint **June 1978**. 396 pp.,
five parts, twenty chapters, exercises with worked discussions after every chapter.
(The later, shorter *A Primer in Data Reduction*, Wiley 1982, is the successor volume.)

Companion volume: [Repeat-Buying — reading notes](repeat-buying-summary.md). *Repeat-Buying* is the
substantive result; *Data Reduction* is the method that produced it. Chapter 10 here re-derives
one of that book's central laws from scratch, as a worked demonstration.

---

## 0. The argument in one paragraph

Most statistical writing teaches techniques for extracting a conclusion from **one** set of data.
Ehrenberg argues that this is the wrong unit of work. Results are only useful to the extent that
they **generalise**, so the real task is to reduce each set of data to a summary that can be
*carried into the analysis of the next set*. That reframing changes almost every downstream
judgement: it makes two significant digits enough, makes rounded averages more valuable than
precise ones, makes prior knowledge the normal starting point rather than a Bayesian exotic, and
makes best-fit criteria — correlation, regression, factor analysis — actively unhelpful, because
fitting one dataset optimally is a different goal from fitting many datasets adequately.

> *"The basic principle throughout is that data analysis must produce results which are usable in
> subsequent work."*
>
> *"The book concentrates on teaching the reader to be numerate, to see patterns and relationships
> that exist in numerical data and to reduce these to summaries that can readily be interpreted,
> used, and communicated. The need is to let the data speak."*

The three criteria of a good summary (Exercise 20A, the book's own closing answer to "what is the
main point?"):

1. **succinct**;
2. **complete** — the original data could be reconstructed from it, within the stated limits of
   approximation;
3. **usable** — the results can readily be used when analysing further data.

Note that Ehrenberg deliberately defers frequency distributions, probability, sampling and
significance testing to the *second half* of the book, "because they are relevant only in certain
limited situations."

---

## Part I — Data Handling (Ch. 1–4)

### Ch. 1 — Averages and Layout

Built around one small table (4 areas × 8 quarters) taken from undigested form to a stated model
with quantified deviations. Three steps: **(a)** improve the display, **(b)** develop an explicit
summary or "model", **(c)** check the deviations of the readings from that model.

**The layout rules**, all justified by how the eye and mental arithmetic actually work:

- **Two significant figures** — defined as *"digits that vary from one number to another."*
  Rounding 97.63 → 98 costs 1–2% of the observed variation and is what makes the pattern visible
  at all: *"the least important part of a number is the part looked at or spoken last."*
- **Averages, not totals.** Totals are on a different scale from the readings and are not
  comparable with anything else in the table.
- **Put figures to be compared down columns, not across rows.** Running down a column the eye reads
  the tens digits (9, 9, 10, 9, 9) and bypasses the units; across a row, with intervening gaps, it
  cannot.
- **Order rows and columns by size** rather than by convention. "Using the dimensions of a table to
  represent the previously unknown pattern of the data can be more useful to the reader than
  repeating the well-known order of some row or column labels (everyone already knows that QII
  follows QI)."
- **Single spacing, table grids, self-explanatory labels** (`No`, `So`, `Ea`, `We` — not A, B, C, D).
- **Exclude exceptions from the summary averages.** "We can either give four comparable averages
  with two exceptions, or four averages that are not comparable and two exceptions." The exceptions
  stand out *more* for having been excluded.
- **Twyman's Law:** *"any figure that looks interesting or different is usually wrong."* Check the
  arithmetic first, the substance second.

**What the chapter argues against**, each with a worked demonstration on the same data
(Exercise 1A):

| Device | Objection |
|---|---|
| **Graphs** | slow to construct; you cannot read quantitative detail off them; they give no usable summary |
| **Percentage changes** | every variation shows up twice, once up and once down; uninterpretable without the original data |
| **Indices on a fixed base** | all feeling for the size of the readings is lost; base choice is arbitrary and ages |
| **Percentage shares** | fine when variation is proportional; but exceptional readings distort the base (a region had its *lowest* share in the quarter of its *highest* absolute figure) |
| **Moving averages** | a rise can be caused by a low figure dropping out or a high one coming in — you cannot tell which |

Exercises 1C–1H apply the rules to real published sources — *Business Week*'s "Figures of the
Week", the UK Government Statistical Service pocket-card, a company annual report, a *Guardian*
piece on air-accident rates in which each decade's figure is quoted in different units (restated
uniformly, the pattern is simply "the fatality rate per mile has halved every ten years"). The
closing note is aimed at the analyst, not the reader: *"The reader's role is to return undigested
figures to their originator with rude comments, rather than do his arithmetic for him."*

### Ch. 2 — Using Prior Knowledge

Re-analysing the second year of the same data, now with the first year's model in hand. The
analysis is trivially quick — and the important output is not the confirmation but the **audit of
which deviations recur**. Averaging the two years' deviations shows that almost all of them cancel:

> *"It is this irregularity of the readings that appears to be generalisable."*

This produces the book's key term. An **empirical generalisation** is a model plus the *stated
range of conditions* over which it has been shown to hold — here: two different years, all four
quarters, values from 39 to 101, and despite one large unrepeated exception. Extending it does not
mean re-deriving it; it means testing it on more conditions. *"Use of prior knowledge avoids having
to re-invent the wheel every time."*

### Ch. 3 — Tables and Graphs

Tables *to illustrate* (small, rounded, ordered, in the text) versus tables *for the record*
(complete, appendixed). Graphs are good for showing that two things move together and bad for
almost everything else.

### Ch. 4 — Compared with What?

The interpretive chapter, and the one most directly relevant to modelling work.

**The driving-time parable (§4.1).** The standard research response to "how long will it take to
drive from A to B?" is to commission investigators to drive the routes and report the latest times
— generating large arrays of instantly-stale statistics. The eventual discovery is that all of it
collapses to *distance ÷ 35*, a new concept called "average speed". Forecasting then needs three
things: the generalisable law; generalisable adjustments (55 mph on motorways, +30 min entering a
conurbation); and specific facts to slot in (distances, road types, weather). **No recent
measurements are needed at all.** Errors are then classified — by road type, by occasion, by
driver, and "errors that cannot be accounted for yet" — and each class becomes the next research
question.

**High, low, or normal (§4.2).** A new Brand X: 14% of a sample express an intention to buy,
3% currently use it. Is 14% good news?

- **"I is high."** The average I/U ratio for other brands in the field is 2/1; Brand X is at 14/3.
  Looks strong.
- **"I is low."** But prior research (Bird et al. 1966) had established that `I = K√U`, holding to
  within ~3 percentage points across 20+ product-fields, both countries, five years, demographic
  sub-groups, and several question wordings. With `K = 11.5`, a 3% usage brand should score
  `11.5 × √3 ≈ 20%`. So 14% is *low*.
- **"I is normal."** But the same body of prior work records that *newly launched* brands score
  5–8 points below established ones. Brand X is new. 14% is exactly normal, and tells us nothing.

The chapter's moral, and one of the book's best lines: *"When a good statistician is asked 'How is
your wife?' he replies 'Compared with whom?'"* And the deflating corollary: *"Once we understand an
area of study, we find either that most observations turn out to be normal and predictable, or that
there is no discernible pattern at all. This may be unexciting but it is inevitable."*

Exercise 4F is a small classic: expressed intentions-to-buy reflect *current and past* usage almost
perfectly and predict *future change* not at all (75% vs 77% of 1963 users intending to buy,
regardless of whether they actually bought in 1964).

---

## Part II — Lawlike Relationships (Ch. 5–10)

### Ch. 5 — Descriptive Relationships

`y = ax + b`. The primary criterion of an equation is that it be **descriptive** — that it
adequately summarise the observed values. Its *status* is set entirely by the range of empirical
conditions under which it has been shown to hold. §5.6 "Other Things NOT Equal" is the important
one: a relationship is worth more, not less, when it survives variation in the background factors.

### Ch. 6 — Using a Given Relationship

Six uses: summarising the data; prediction and extrapolation; understanding and theory;
technological application; decision-making; and analysing further data. Plus **§6.7 The Meaning of
Failure** — a failure to fit is informative only if you had a prior expectation for it to
contradict — and **§6.9 A Common Misuse**.

### Ch. 7 — Deriving a New Relationship

The first-time problem: fitting when there is no prior result. Practical, deliberately low-tech
procedure — average the extreme groups, draw the line, look at the scatter — with §7.5 and §7.7 on
the existence of, and choice between, **alternative working-solutions**. This sets up Ch. 14.

### Ch. 8 — Non-linear Relationships

Systematic deviations from a straight line; choosing a curve; logarithmic fits. The running example
is children's height and weight, `log w = .02h + .76`. §8.6 introduces a **cube-root law** motivated
dimensionally (weight ∝ volume ∝ linear dimension³) — the point being that the theoretically
motivated form is preferred not because it fits better but because it *connects* to knowledge
outside the dataset.

### Ch. 9 — Many Variables

Handling multi-variable data without multivariate techniques: analyse structured sub-groups, look
for what is constant, and introduce correction factors. §9.3 "A Simple Model: Buyer Behaviour" and
§9.4–9.5 set up the material that Chapter 10 then resolves. §9.5 "A Breakdown in Generalisation" is
the honest counter-case.

### Ch. 10 — The Emergence of Theory

**The most important chapter in the book for this repository**, because it derives a
buyer-behaviour law end-to-end as a demonstration of method.

**The role of hypotheses.** Speculation is how new truths get found — the cube-root transformation
of weight "simply is not the kind of idea that springs to mind naturally." But it must be tested;
and Ehrenberg insists on the distinction that he thinks gave theory its bad name: *"Theoretical
arguments and assumptions based on insight or hunch must be sharply distinguished from validated
theory. The one reflects what we think, the other what we know."*

**The main role of theory is not discovery but integration** — "to link different kinds of known
results."

**The worked problem.** Five breakfast-cereal brands with market shares from 38% down to 5%. In a
4-week period they are all bought at about the same rate, `w ≈ 1.7 ± 0.2`. In a 24-week period the
rates spread widely, `w` from 6 down to 2, tracking market share. A constant in one period and a
strong trend in the other — apparently needing a three-variable model (`w`, share, period length).

**The resolution.** Introduce a fourth variable, penetration `b`, and derive the answer from three
*already-known* empirical results rather than by curve-fitting:

- **(A)** Buyers of Brand X buy the total product-class at about the same rate as buyers of Brand Y.
- **(B)** `b_XY = D·b_X·b_Y` (duplication of purchase).
- **(C)** A duplicated buyer buys a brand at about the same rate as its other buyers.

Writing out the category purchases of X's buyers as `Nb_X w_X + Nb_XY w_Y.X + Nb_XZ w_Z.X`, setting
the per-buyer version equal to the same expression for Y, substituting (B) with `D = 1` and (C),
cancelling `b_X` and `b_Y` and eliminating the common `b_Z w_Z` term, leaves:

```
w_X (1 − b_X)  =  w_Y (1 − b_Y)        i.e.   w(1 − b) = constant
```

**Why the single factor `(1 − b)` does two jobs.** In long periods penetrations are high (.4–.9),
where `(1 − b)` changes very fast — so it absorbs the large trend in `w`. In short periods
penetrations are low (.01–.2), where `(1 − b)` is close to 1 for every brand — so it introduces no
spurious trend. Period length is therefore handled *indirectly*, without appearing in the equation.

**How to use it (Exercise 10A).** For a **new brand** with a sales target of 15 purchases per 100
housewives per 4 weeks: `w` is *predictable* at ~1.7 whatever happens, so the required penetration
is ~9%. "We are not here predicting sales, the $64,000 question. The prediction is only that,
whatever happens, the new brand will tend to be bought 1.7 times in 4 weeks by its buyers." For an
**established brand**: doubling sales by doubling `w` from 1.7 to 3.4 is ruled out, because no
cereal brand has ever exhibited such a rate. Growth must come through `b`.

Exercise 10B makes the units point explicitly: these laws hold when the analysis unit is the
**purchase occasion**. For cereals it does not matter (≈1 pack per occasion); for petrol
(≈3 gallons per purchase) it matters entirely.

Hinshelwood's three stages of a scientific theory are quoted here as in *Repeat-Buying* Ch. 11.

---

## Part III — Statistical Variation (Ch. 11–15)

### Ch. 11 — Summary Measures

Averages and measures of scatter. Ehrenberg prefers the **mean deviation** to the standard
deviation for *descriptive* purposes — it is what people can actually interpret — while conceding
that the variance is mathematically far more tractable (short-cut formulae, analysis of variance),
which is why it dominates.

### Ch. 12 — Frequency Distributions

Normal, Poisson, **Negative Binomial**, Binomial, **Beta-Binomial** — i.e. exactly the four
distributions that generate this repo's models. Treated as *descriptive summaries*: a distribution
is worth invoking when it lets you replace a table of frequencies with two numbers from which the
table can be reconstructed.

The Normal is characterised by its intervals rather than its formula:

```
±1 / ±2 / ±3 standard deviations  →  68% / 95% / 99.7%
±1 / ±2 / ±3 mean deviations      →  58% / 90% / 98%
mean deviation ≈ 0.8 × standard deviation
```

§12.3 (NBD) and §12.5 (Beta-Binomial) are the direct bridge to *Repeat-Buying* and to the Dirichlet.

### Ch. 13 — Probability Models

The probability concept, independent events, **stochastic models**, and probability as applied to
uncertain (non-repeatable) events. Bayesian methods get a mention here — and a wry callback in
Exercise 20B, where Ehrenberg notes that the Bayesian approach is the statistical literature's one
apparent acknowledgement of using prior results, "but this is not widely practised."

### Ch. 14 — Correlation and Regression

The book's central methodological critique, and the source of Ehrenberg's reputation.

**On the correlation coefficient.**

```
r² = 1 − (residual variance / variance of y)
s.d. of residuals = s_y · √(1 − r²)
```

Which means correlations must be very high before they buy much:

| r | reduction in scatter |
|---|---|
| 0.5 | ~13% |
| 0.95 | ~70% |

Three separate objections, each with a figure:

1. Equal residual scatter can produce radically different correlations (because `r` measures
   residual variance *relative to the total variance of y*, which differs between datasets).
2. Equal correlations *and* equal residual scatter can coexist with completely different underlying
   relationships.
3. Therefore correlation is of no use for prediction or for comparing datasets. If you want to
   report the scatter, report the scatter: *"it is simpler for predictive or comparative purpose to
   give the size of the residual scatter directly and let anyone who wants to do so take its ratio
   to that of the y-variation."*

**On regression — the two-lines theorem.** Least squares in the y-direction gives the regression of
y on x; least squares in the x-direction gives a different line. (Perpendicular deviations are
ruled out because changing units changes the equation.) Both lines pass through the means of *that*
dataset. Another dataset has different means. Two distinct straight lines share only one point.
Hence:

> *"We therefore have the theorem that, in general, a regression equation fitted to one set of data
> cannot hold again for any other data. This is what theory says. And in practice no one has claimed
> anything different. There appear to be no cases quoted in any textbook where a regression equation
> fitted to one set of readings has held for another, different, set of data."*

The demonstration uses the Birmingham children's height/weight data: 54 sub-groups (2 sexes ×
9 ages × 3 social classes) → **108 different regression equations**; at half-yearly ages, **216** —
for data that Part II had already shown to obey a *single* generalisable relationship. "The reason
why regression analysis yields such complex results lies in the technique of analysis."

**The constructive resolution.** Fit is a very inefficient criterion for discriminating between
equations. On the chapter's five-point example:

```
y = 2.6x + 12.2  ± 4.9     ← the least-squares regression, the "best" fit
y = 2x   + 14    ± 5.0
y = 3x   + 10    ± 5.1
y = 4x   +  8    ± 5.7
```

The slope varies by more than 50% while the residual scatter moves by less than one unit against a
20-unit range in y. *"Could one say that the equation y = 4x + 8 is 'wrong' whereas y = 2.6x + 12.2
is 'right', just because of a 0.8 unit difference in the residual scatter?"* So: **among the many
equations that fit acceptably, choose the one that also holds for other datasets.** Generalisation
and fit are not in serious conflict as long as generalisation comes first.

### Ch. 15 — Multivariate Techniques

**Multiple regression.** A crop-yield example (temperature `t`, fertiliser `f`) gives
`y = 8t − f + 88`, R ≈ .9, "accounting for 80% of the variance". Two objections. First, the
coefficients cannot be read causally: the data contain no case of `f` rising while `t` stayed put —
fertiliser only ever increased when temperature did (collinearity) — so the negative `f` coefficient
is uninterpretable. Second, the alternative `y = 5t + 2f + 64` fits nearly as well (residual s.d.
15 vs 14, same R) while asserting the *opposite sign* on fertiliser and a different temperature
effect.

> *"Multiple regression analysis seeks to find the 'best' answer to a complex problem by analysing
> an isolated set of data. Irrespective of how limited or incomplete the data, the solution is
> always 'best', with scant regard to whether it is any good. (A danger with high-powered
> salesmanship is that it often deludes the salesman himself.)"*

**Component and factor analysis.** Input is a correlation matrix; output ("loadings") is more
correlations — so the Ch. 14 objections apply twice over, compounded by the standardisation of the
test variables, which makes cross-study comparison harder still. The claim of objectivity is
rejected outright: the choice of input variables, of factor vs component analysis, of the particular
variant, of the rotation, and of the interpretation are **all subjective**. *"There is nothing
inherently wrong with subjectivity since judgment has to be exercised in many problems in data
analysis. But the adoption of some arbitrary analytic technique should not be regarded as objective
justification for one's results."*

**Cluster analysis and multi-dimensional scaling** — "currently modish", boosted by cheap computing.
The diagnosis is that they answer the wrong question: *"when facing many variables, the usual
analysis problem is not that we have little information, but that we do not know how to interpret
and integrate the information that we already possess. None of these techniques seem to have shown
themselves capable of building a growing body of coherent knowledge."*

**Discriminant analysis** — an older technique with a clearer purpose (do two sets of objects
differ?), but since the data rarely arise from explicit random sampling, "it is not altogether clear
what this kind of procedure really signifies."

The chapter's summary sentence: these techniques *"lack the discipline of having to obtain
reproducible and generalisable results, since the techniques are not designed to lead to such
findings."*

---

## Part IV — Sampling (Ch. 16–18)

### Ch. 16 — Taking a Sample · Ch. 17 — Sampling Distributions

Standard material, deliberately placed late: random and stratified sampling, sampling error, the
standard error of the mean, the Central Limit Theorem.

### Ch. 18 — Statistical Inference

Estimation, confidence limits, hypothesis testing, χ² goodness-of-fit and contingency tests — with
three correctives running through:

- **Hypotheses should come from prior empirical data, not be invented for the occasion.** *"The
  hypotheses tested should generally derive from previous empirical data and should reflect what
  such prior knowledge has led one to expect. A significant difference therefore means that one's
  expectation was wrong."*
- **Statistical hypotheses are not scientific hypotheses.** A scientific hypothesis says light bends
  near the sun, or that `log w = .02h + .76`. A statistical hypothesis asks only whether an observed
  deviation in *sample* data is real or a sampling artefact. *"The question of statistical inference
  really arises only with small samples. With large samples the standard error is generally small,
  so that anything except the smallest overt differences will generally be real."*
- **If prior data exist, use them instead of sampling theory.** *"Extensive empirical evidence about
  the general variability of the data should have been built up. One therefore need not have to rely
  on theoretical sampling theory to provide an inference about the new sample's likely variability."*

Exercise 18A dispatches a common error: an observed mean of 5 with standard error 3 would *not*
become significant with a larger sample, because a larger sample would generally have a mean closer
to zero as well as a smaller standard error.

---

## Part V — Empirical Generalisation (Ch. 19–20)

### Ch. 19 — Observation and Experimentation

Repetition; which factors to vary; statistical surveys; observational studies; the randomised
experiment and the design of experiments; and §19.8 **Theoretical Norms** — the argument, developed
at length in *Repeat-Buying* Ch. 6, that a validated stationary model can *supply* the control
condition, cheaper than an experiment and applicable after the event.

### Ch. 20 — Description and Explanation

**§20.1 Laws are descriptive, and deliberately over-simplified.** Boyle's Law `pv = C` does not
claim that pressure causes volume; it describes what `p` and `v` do when a third thing (the piston)
is moved. Laws are not exact, and their inexactness is intentional: *"Science aims to find one
generalisable equation that covers a wide range of different phenomena with some known degree of
error rather than a great number of different specific equations that give a closer descriptive fit
to isolated sets of readings."* Newtonian mechanics covers falling bodies, pendulums, tides and
cannon balls only by ignoring friction and air resistance. And: *"Once an error is known it is no
longer merely an error."*

**Well-developed laws have no numerical coefficients.** Boyle's law reads `p_X v_X = p_Y v_Y`; the
buyer-behaviour law reads `w_X(1 − b_X) = w_Y(1 − b_Y)`. This is not aesthetics — *"a law is only
ready for use when it contains no coefficients whose numerical values still have to be
established."*

**§20.2 What an explanation actually is.** A chain of descriptions:

```
"How"  →  "How"  →  "How"   =   "Why"
```

"Ice floats because it is lighter than water" does two things: it links a specific phenomenon to a
larger generalisation already accepted (specific gravity), and it rules out the alternatives (the
Aristotelian doctrine that floating depends on shape). *"We seek explanation and understanding. But
this is never simple because there are always 'third factors', and it is never complete because
there are always 'black boxes' that elude our grasp."*

And explanations rarely take the form expected. The `w(1 − b)` law "might have been sought in terms
of people's incomes, the sizes of their households, and their exposure to advertising, but the
result actually follows from quite different considerations, as was outlined in Chapter 10."

**§20.3 From facts to theory and back again.** Fact-collection must be preceded by *some* hypothesis
(Popper), "but initially this only needs to be some very loose, imprecise notion of which facts it
might be interesting to collect... At the beginning these ideas are largely based on ignorance."
Against theory-first modelling: *"There is nothing like a few facts to eliminate any number of
speculative assumptions."* On "reasonable" assumptions: *"'Reasonable' is a telling word here. It is
generally used only when no reasons can in fact be given."*

The test, and the coinage the book is remembered for:

> *"Take away the mathematical language and what generalised factual knowledge of the process in
> question remains? If the answer is none, the mathematical symbol for that is very simple."*
>
> *"The pay-off of **Sonking, the Scientification of Non-Knowledge**, is only in the model-builder's
> neo-Cartesian self-regard: 'I sonk, therefore I am'. The question is not what the theoretician
> thinks, but what he knows."*

Einstein is dealt with as the standard counter-example ("people usually pick on dramatic extremes
which they do not understand"): his work concerned minor discrepancies in results resting on
centuries of empirical observation — *"before a theory explaining a process can be tested that
process must be known."*

Closing with Kuhn's three stages — pre-paradigmatic fishing expeditions (distinguished by "intense
concern with techniques and apparently endless arguments over methodology"), normal science, and
occasional revolution — and a final remark aimed squarely at the analyst's nerve:

> *"It takes more insight and courage to report an average or an abstract relationship than merely
> to present all the facts."*

---

## What this means for this repository

**Where it sits.** This is the methodological half of the Ehrenberg–Bass branch described in
[README.md § The other tradition](../../../README.md). The Dirichlet is what that tradition found; *Data
Reduction* is how it looked.

**It already agrees with the repo's stated principles, and sharpens them.** [CLAUDE.md](../../../CLAUDE.md)
records parsimony, "heterogeneity not individual dynamics," and `past = f(θ)` in preference to
`future = f(past)`. Ehrenberg supplies the general argument behind all three, and Ch. 14–15 supply
the specific case against the regression/data-mining alternative — an argument this repo currently
asserts rather than makes.

**Concrete things to adopt.**

1. **Two significant figures in every displayed table.** This is the single highest-leverage change
   and it cuts directly against `great_tables` defaults. Ehrenberg's definition — digits that vary
   between numbers — is a usable rule, not a style preference.
2. **The Observed/Theoretical table idiom.** Not a fit statistic in a caption, but paired O and T
   columns so the reader can see *where* the model succeeds and fails. This is how *Repeat-Buying*
   Ch. 3 is built and it would suit the `analyses/` essays.
3. **Always give the range of conditions.** Every result in the repo's essays should carry the
   equivalent of the book's Table 4.2 — the list of product-fields, countries, periods and
   sub-groups over which it has been checked. A model without a stated range of generalisation is
   a curve fit.
4. **Report residual scatter, not R².** Ch. 14's argument applies verbatim to any model-fit chart
   in the repo.
5. **Interpretive norms as a deliverable.** The Ch. 4 "high / low / normal" sequence is a template
   for an essay: take an observed brand or cohort statistic, apply three successively better norms,
   and show the conclusion reversing twice.

**A tension worth naming.** The repo uses Stan/BridgeStan for Bayesian fits, arviz diagnostics, and
MLE on frequency counts. Ehrenberg's own estimation practice is deliberately crude — "mean and
zeros," lookup tables, Excel Solver — on the grounds that estimator efficiency is almost never the
binding constraint, whereas generalisation always is. He is not arguing that better estimation is
wrong; he is arguing that it is usually the wrong thing to spend effort on. That is a real
methodological disagreement with the repo's current centre of gravity, and it is more useful kept
visible than smoothed over.
