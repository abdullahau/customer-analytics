# Customer-Base Analytics

A research library of **probability models for customer-base analysis** — the Fader–Hardie tradition of parsimonious stochastic models that treat a customer's observed buying as the visible output of a latent behavioural process, and use it to project future purchasing, retention, and **customer lifetime value (CLV)**.

Each topic is a self-contained [Quarto](https://quarto.org) essay (mathematical exposition + executable Python) published to GitHub Pages: [**https://abdullahau.github.io/customer-analytics/**](https://abdullahau.github.io/customer-analytics/){.uri}

> **New here?** Read [The big idea](#the-big-idea-probability-models-for-buyer-behaviour) for the one-page mental model, skim [the taxonomy](#dimension-1--the-firmcustomer-relationship-2×2-taxonomy) to see how the models relate, then jump to [Getting started](#getting-started) to run the code. This is **not** a "buy-till-you-die (BTYD)"-only project — BTYD (Pareto/NBD, BG/NBD) is just **one corner** of the space covered here.

------------------------------------------------------------------------

## The big idea: probability models for buyer behaviour {#the-big-idea-probability-models-for-buyer-behaviour}

We only ever get a *"foggy window"* onto a customer's true tendencies: someone who bought twice last year is not necessarily a "two per year" buyer. So instead of extrapolating the observed numbers, we model the **latent process** that generated them. Two ingredients:

1.  **An individual-level model** for one customer's behaviour given latent traits θ — e.g. Poisson (how many purchases), exponential/geometric (how long until they lapse), Bernoulli (buy vs. not).
2.  **A mixing distribution** (gamma, beta, …) describing how θ is spread across the customer base — i.e. **heterogeneity**.

Combining the two gives a **mixture model** for a randomly-chosen customer; Bayes' theorem then turns any customer's observed history into forward-looking inferences — **P(alive), expected future transactions, residual CLV** — typically from nothing more than **RFM** (recency, frequency, monetary value), which are the *sufficient statistics* for these models. Formally: `past = f(θ)` and `future = f(θ)`, in contrast to the regression / data-mining `future = f(past)` approach. A recurring lesson from this literature is that many "dynamics" people try to model (a slowing aggregate purchase rate, retention rates that *rise* with tenure) are **not** individual-level effects at all — they are **sorting effects** that fall out of heterogeneity ("the ruse of heterogeneity").

## Dimension 1 — the firm–customer relationship (2×2 taxonomy)

Two questions classify any customer base (Schmittlein, Morrison & Colombo 1987; Fader & Hardie 2009) and **determine which model is even admissible**:

- **Is churn observed?** *Contractual* (the customer cancels / fails to renew — we see it) vs. *noncontractual* (the customer just silently stops — "silent attrition", and we must infer whether they are dead or merely dormant).
- **Can transactions happen anytime?** *Continuous* vs. *discrete* (only at fixed epochs).

The contractual/noncontractual boundary is **fundamental — a model built for one side must never be applied to the other.**

|   | **Noncontractual** (churn latent) | **Contractual** (churn observed) |
|--------------------|---------------------------|--------------------------|
| **Continuous** (any time) | grocery, hotel, mail-order → **Pareto/NBD, BG/NBD, NBD, NBD/OTB** | credit card, mobile, utilities → **exponential-gamma (EG), Weibull-gamma** |
| **Discrete** (fixed epochs) | event attendance, charity drives, refills → **BG/BB** | magazine/SaaS subs, insurance, gym → **sBG, BdW** |

In **noncontractual** settings the modelling challenge is telling a dead customer apart from one in a long hiatus; in **contractual** settings churn is known, so the focus shifts to **duration / retention** and projecting the survivor curve.

## Dimension 2 — the building blocks (counting / timing / choice)

Every model is assembled from — and usually **integrates** — three process types, each paired with a heterogeneity distribution:

| Block | Question | Individual model → with heterogeneity |
|--------------|--------------|---------------------------------------------|
| **Counting** | how many? | Poisson → **NBD** (gamma); Bernoulli → **beta-Binomial** (beta) |
| **Timing** | when / how long alive? | exponential → **Pareto / exp-gamma**; geometric → **sBG**; Weibull → **Weibull-gamma / BdW** |
| **Choice** | whether / which / how much? | Bernoulli/binomial (buy-vs-not, brand, one-time-buyer); spend → **Gamma-Gamma** |

**Integrated models** combine the blocks to solve jointly for the latent parameters:

- **Counting + Timing** — a purchasing process *and* an "alive/death" process: **Pareto/NBD** (Poisson-gamma buying + exponential-gamma dropout), **BG/NBD** (dropout occurs after a purchase, beta-geometric), **BG/BB** (their discrete analog). Also "stickiness" (# visits × duration/visit) and new-product **trial timing + repeat counting** (depth-of-repeat).
- **Counting + Counting** — purchase *volume* (# transactions × units/transaction); page views (# visits × pages/visit).
- **Counting + Choice** — brand purchasing (category incidence × brand choice), "conversion" (# visits × buy/not-buy), and the **NBD/OTB** one-time-buyer split.

Layer a **spend sub-model** (Gamma-Gamma) on a purchasing model and you get monetary value → **CLV = margin × revenue/transaction × DET** (discounted expected transactions). Roll **acquisition + retention + spend** together and you get firm-level **customer-based corporate valuation (CBCV)**.

## The model catalogue

Rendered pages are linked from [`index.qmd`](index.qmd); sources live under [`notebooks/`](notebooks/), organised by purpose.

**Repeat purchasing — noncontractual** (`notebooks/models/purchasing/`) - **NBD overview** — the Poisson-gamma counting model; foundation for everything. - **NBD/OTB** — NBD with a "one-time buyer" (spike-at-zero) segment. - **BG/NBD** (+ a **Stan/Bayesian** version) — the easy-to-estimate alternative to Pareto/NBD; dropout modelled as beta-geometric after each purchase. - **Pareto/NBD** — the original "counting your customers" model (exponential-gamma dropout at any time). - **BG/BB** — the discrete-time analog (beta-Bernoulli buying + beta-geometric death), e.g. annual donation incidence.

**Retention — contractual, discrete-time** (`notebooks/models/retention/`) - **Beta-geometric (sBG)** — constant individual retention prob. + beta heterogeneity; explains why *aggregate* retention rises with tenure. Plus an interactive [marimo](https://marimo.io) app, `sBG-Model.py`. - **Beta-discrete-Weibull (BdW)** — generalises sBG to allow duration dependence. - **Subscription retention** — discrete-time contractual retention applied.

**Acquisition & new-product forecasting** (`notebooks/models/acquisition/`) - **Depth-of-repeat** — decompose new-product sales into **trial** + **repeat** (by depth-of-repeat level). - **Finite-mixture BG sales forecast** — unit-sales forecasting via a beta-geometric finite mixture. - **Dynamic changepoint** — a multiple-event timing model whose buying-rate *changepoints* evolve as the product moves from "new" to "established" (Fader–Hardie–Huang; the "Kiwi Bubbles" test market).

**Spend & CLV** (`notebooks/models/spend/`, `notebooks/models/clv/`) - **Gamma-Gamma** — monetary value / spend-per-transaction (with regression-to-the-mean). - **RFM & CLV** — iso-value curves linking recency/frequency/monetary to CLV.

**Descriptive analyses** (`notebooks/analyses/`) — the customer-base audit and buyer-behaviour summaries that precede and motivate the models (see below).

**Valuation** (`notebooks/valuation/`) — **CBCV** for subscription businesses (DISH / SiriusXM style): fit acquisition + retention + spend sub-models to publicly-disclosed customer data and roll them into firm value.

------------------------------------------------------------------------

## Summarizing Buyer Behavior

Before any model, we *describe* the customer base. Using transactions log data and marketing spend data we calculate:

1.  Monthly sales over time
2.  Total customers acquired
3.  Customer acquisition cost (CAC)
4.  Distribution of spend per purchase
5.  Initial versus repeat sales volume
6.  Initial versus repeat average order value (AOV)
7.  Sales and AOV by source
8.  First-purchase profitability
9.  Cohorted sales (the “C3”)
10. Revenue retention curves
11. Cumulative spend per customer
12. Distribution of total spend by customer
13. Customer concentration (“Pareto”) chart

What the analysis summarize:

1.  Growth
2.  Unit costs
3.  Unit profitability (unit economic performance)
4.  Retention
5.  Heterogeneity (customers, time)
6.  Yield on CAC
7.  CLV / CAC
8.  Monthly/Annual Recurring Revenue (MRR/ARR)
9.  Average Revenue Per User (ARPU)
10. Logo churn
11. Revenue Churn
12. Weekly/Monthly/Annual Active Users (DAU/MAU/AAU)
13. Gross Margin
14. Contribution Margin
15. Payback Period
16. Magic Number: Net new ARR divided by sales & marketing spend
17. Rule of 40: Growth rate plus profit margin should exceed 40%

## Models to Implement

- Weibull-Gamma acquisition model
- Exponential-Gamma retention model
- Point process transaction model
- Simulating order flow dynamics
- Acquisition process
- Purchase process
- Spend process

------------------------------------------------------------------------

## Getting started {#getting-started}

Prerequisites: [**uv**](https://docs.astral.sh/uv/) (Python 3.14 is pinned via `.python-version`).

``` bash
git clone https://github.com/abdullahau/customer-analytics
cd customer-analytics
uv sync                       # create the .venv and install deps + the local `utils`/`models` packages

# Render the whole site (all essays) to docs/ :
uv run quarto render

# ...or work on a single essay:
uv run quarto render notebooks/models/purchasing/bg-nbd.qmd
uv run quarto preview notebooks/models/spend/gamma-gamma.qmd   # live preview
```

Note: a full render executes every notebook, including the Stan/Bayesian fits, so it is slow. See [CLAUDE.md](CLAUDE.md) for the repository layout, the Quarto/rendering model, and coding conventions.

### Repository structure (short)

| Path | What |
|------------------------------------|------------------------------------|
| `notebooks/` | the essays — `analyses/`, `models/{acquisition,retention,purchasing,spend,clv}/`, `valuation/`, `data-prep/` |
| `lib/utils`, `lib/models` | importable Python helpers (`from utils import …`) — RFM builder, data loaders, Stan/BridgeStan wrappers, plotting |
| `stan/src`, `stan/implementations` | first-party Stan models; third-party reference implementations |
| `data/` | CDNOW, donation incidence, panel data (Kiwi Bubbles), CBCV (DISH/SIRI), retention, CAC |
| `assets/`, `docs/` | shared Quarto style; rendered HTML output (GitHub Pages) |
| `Projects/`, `references/` | the source papers, tutorials, and spreadsheets (see the reading map below) |

## Reading map (source material)

The primary papers, tutorials, and spreadsheets are under [`Projects/`](Projects/) and [`references/`](references/):

- **Taxonomy & overview** — Fader & Hardie (2009) *Probability Models for Customer-Base Analysis*; *Marketing Models for the Customer-Centric Firm*.
- **Noncontractual / continuous** — Schmittlein–Morrison–Colombo *Counting Your Customers* (Pareto/NBD); Fader–Hardie–Lee *"Counting Your Customers" the Easy Way* (BG/NBD); *A Note on an Integrated Model…* (NBD/OTB) — see `references/CDNOW/`.
- **Noncontractual / discrete** — Fader–Hardie–Berger, *Customer-Base Analysis with Discrete-Time Transaction Data* (BG/BB).
- **Contractual retention** — Fader & Hardie *How to Project Customer Retention* (sBG) and *…the Perils of Ignoring Heterogeneity*; `references/An Introduction to Probability Models for Marketing Research/`.
- **New-product forecasting** — Eskin *Dynamic Forecasts… Depth of Repeat*; Fader–Hardie–Huang *A Dynamic Changepoint Model…*; *Forecasting Repeat Buying for New Products…*; `references/Depth-of-Repeat/`.
- **Spend, RFM & CLV** — Fader–Hardie–Lee *RFM and CLV: Using Iso-Value Curves*; *Simple probability models for computing CLV and CE*; `references/PyMC-Marketing/` (Gamma-Gamma).
- **Valuation (CBCV)** — McCarthy–Fader–Hardie *Valuing Subscription-Based Businesses…*; *Customer-Based Corporate Valuation for Publicly Traded Noncontractual Firms*; *Linking Customer and Financial Metrics to Shareholder Value*; `references/CBCV/` (DISH & SiriusXM spreadsheets).
- **The customer-base audit** — `references/The Customer-Base Audit (TCBA)/`; `references/Analysing Buyer Behaviour Using Consumer Panel Data/`.

## Overview

![Reference](references/Price-Implied-Expectations-through-Unit-Economics-Simulation.png)

![Workflow Lifetimes Library — CLV Model](references/Workflow-Lifetimes-Library-CLV-Model.png)

![CBCV Infographic](references/CBCV-Infograhic.png)

## Reference

- [Bruce Hardie](https://www.brucehardie.com/)
- [Ian Frankenburg](https://ian-frankenburg.com/)
- [Theta Equity Partners](https://thetaclv.com/)
- [PyMC - Marketing](https://www.pymc-marketing.io/en/stable/)
- [lifetimes (python package)](https://github.com/CamDavidsonPilon/lifetimes)