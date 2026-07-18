import marimo

__generated_with = "0.23.14"
app = marimo.App(layout_file="layouts/customer-base-audit.grid.json")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Customer-Base Audit
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Derived from *The Customer-Base Audit: An Excel-Based Companion* (Fader, Hardie, Ross, v1.0).

    Quarterly aggregated data is provided by **Madrigal** and represents a 1% sample of data from **Q1 2016 - Q4 2019** (16 quarters) of **70,041 customers**.

    Product-dimension analyses (TCBA Ch. 8) are out of scope.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imports
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import altair as alt
    import matplotlib.pyplot as plt
    from great_tables import GT, loc, style

    # magic command not supported in marimo; please file an issue to add support
    # %config InlineBackend.figure_formats = ['svg']
    return GT, alt, loc, np, pd, plt, style


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Long Format
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `cust_data_long.csv` — one row per customer × quarter *in which the customer was active*. ~130,789 rows.

    | Column | Meaning |
    |---|---|
    | `CustomerID` | customer key |
    | `Cohort` | acquisition quarter, e.g. `y2016 q1`; also `pre y2016` for customers acquired before the observation window |
    | `YearQuarter` | `y2016 q1` … `y2019 q4` |
    | `NumTrans` | transactions in that quarter |
    | `Spend` | revenue in that quarter |
    | `Profit` | contribution profit in that quarter |

    Derive `Year` from the first 5 characters of `YearQuarter` (`y2016` … `y2019`).
    """)
    return


@app.cell
def _(pd):
    cust_data = pd.read_csv("data/madrigal/cust_data_long.csv")
    cust_data = (
        cust_data
        .assign(
            Spend=lambda x: (x["Spend"] * 100).round().astype("int64"),
            Profit=lambda x: (x["Profit"] * 100).round().astype("int64"),
        )
        .assign(
            **cust_data["YearQuarter"]
            .str.extract(r"y(\d{4})_q(\d)")
            .rename(columns={0: "Year", 1: "Quarter"})
            .astype({
                "Year": "int32", 
                "Quarter": "int8"
            })
        )
        .drop(columns="YearQuarter")
    )
    return (cust_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Wide to Long format
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three files — `cust_by_qtr_trans.csv`, `cust_by_qtr_spend.csv`, `cust_by_qtr_profit.csv` — one row per customer, one column per quarter, plus a `Cohort` column. Mostly zeros/blanks. If you use these, **do not assume the three files share the same CustomerID ordering — verify.**

    In this exercise, we will be using the long format data. However, if you only have wide format data, you can create a long format dataframe with the following steps:

    ```python
    from functools import reduce

    def wide_to_long(wide_df, value):
        long_data = wide_df.melt(
            id_vars=["CustomerID", "Cohort"],
            value_vars=wide_df.columns[2:],
            var_name="YearQuarter",
            value_name=value
        ).sort_values(
            ["CustomerID", "YearQuarter"]
        )

        if value == "NumTrans":
            long_data = long_data.query(
                "NumTrans > 0"
            ).astype({"NumTrans": "int32"})

        return long_data.reset_index(drop=True)

    trans_wide = pd.read_csv("data/madrigal/cust_by_qtr_trans.csv")
    spend_wide = pd.read_csv("data/madrigal/cust_by_qtr_spend.csv")
    profit_wide = pd.read_csv("data/madrigal/cust_by_qtr_profit.csv")

    cust_data_long = reduce(
        lambda left, right: left.merge(
            right,
            on=["CustomerID", "Cohort", "YearQuarter"],
            how="left",
        ),
        (
            wide_to_long(df, value)
            for df, value in [
                (trans_wide, "NumTrans"),
                (spend_wide, "Spend"),
                (profit_wide, "Profit"),
            ]
        ),
    )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data Conventions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **Cohort** = customers acquired in a given period (quarter or year).
    - **Cohort size** = number of customers whose acquisition period is that period (diagonal of a cohort × period active-customer matrix). Size of the `pre y2016` cohort is **unknown** — exclude it from any %-active or per-cohort-size calculation.
    - **AOF** (average order frequency) = total transactions ÷ number of active customers.
    - **AOV** (average order value) = total spend ÷ total transactions.
    - **Average margin** = total profit ÷ total spend.
    - Core multiplicative decomposition of profit:

      ```
      Profit = #customers × AOF × AOV × Margin
             = #customers × (trans/cust) × (spend/trans) × (profit/spend)
      ```

    - For cohorts in a period, the decomposition extends to:

      ```
      Cohort profit = cohort size × % cohort active × AOF × AOV × Margin
      Cohort revenue = cohort size × % cohort active × ASPAC
      ASPAC (avg spend per active cohort member) = AOF × AOV
      ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Histogram Binning Conventions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - Bins are **half-open on the left**: the `$25–50` bin counts spend in `(25, 50]`. The first bin is inclusive of its lower edge, so a customer with $0 spend falls in the first bin.
    - Behavioural distributions are heavily right-skewed (max often 10–100× the mean), so every histogram gets a **right-censoring point** — a terminal `> x` bin.
    - Choose bin width from the percentile table, not by rule of thumb. Preferred widths: 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500. Too narrow → noisy; too wide → hides the skew.
    - Choose the censoring point so the final bin isn't overloaded. If ~5% of customers exceed $578, censoring at $600 puts too much mass in the last bin; $1000 is better.
    - Plot **relative frequencies**, not counts, whenever you compare two groups of different size.
    - In Python, prefer `np.histogram` with explicit `bins=` edges, or `pd.cut(..., right=True)`. (The Excel `FREQUENCY` warning in the book is not relevant to you.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 1 — How do customers differ from one another? (single period)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Objective:** quantify variability in buying behaviour across customers within one calendar year (e.g. 2019). Answer: the "average customer" is a fiction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Working dataset
    Filter long data to `Year == y2019`, group by `CustomerID`, sum `NumTrans`, `Spend`, `Profit`. Only customers with ≥1 transaction in 2019 appear.

    **Validation targets**

    | Metric | Value |
    |---|---|
    | Active customers, 2019 | 31,855 |
    | Total transactions | 60,730 |
    | Total spend | ≈ $5,836,712 |
    | Total profit | ≈ $2,798,904 |
    | Avg transactions / active customer | 1.9 |
    | Avg spend / active customer | $183 |
    | Avg profit / active customer | $88 |
    """)
    return


@app.function
def yearly_cust_data(df, year):

    return (
        df
        .query(f"Year == {year}")
        .groupby("CustomerID", as_index=False)
        .agg(
            NumTrans=("NumTrans", "sum"),
            Spend=("Spend", "sum"),
            Profit=("Profit", "sum"),
        ).assign(
            Spend=lambda x: (x["Spend"] / 100).astype("float32").round(2),
            Profit=lambda x: (x["Profit"] / 100).astype("float32").round(2)
        )
    )


@app.cell
def _(GT, cust_data, pd):
    cust_data_2019 = yearly_cust_data(df=cust_data ,year=2019)

    summary = {
        "Active Customers": len(cust_data_2019),
        "Total Transactions": cust_data_2019["NumTrans"].sum(),
        "Total Spend": cust_data_2019["Spend"].sum(),
        "Total Profit": cust_data_2019["Profit"].sum(),
        "Avg. Transactions / Active Customer": cust_data_2019["NumTrans"].mean(),
        "Avg. Spend / Active Customer": cust_data_2019["Spend"].mean(),
        "Avg. Profit / Active Customer": cust_data_2019["Profit"].mean(),
    }

    summary = (
        pd.DataFrame(summary.items(), columns=["Metric", "Value"])
    )

    (
        GT(summary)
        .tab_header(
            title="2019 Annual Customer Summary",
            subtitle="Customer activity, revenue, and profitability metrics"
        )
        .fmt_number(
            columns="Value",
            rows=[0, 1],
            decimals=0
        ).fmt_currency(
            columns="Value",
            rows=[2, 3],
            decimals=0
        ).fmt_currency(
            columns="Value",
            rows=[4, 5, 6],
            decimals=2
        ).fmt_number(
            columns="Value",
            rows=[4],
            decimals=2
        ).tab_options(
                table_font_size="12px",
                data_row_padding="4px"
        )
    )
    return (cust_data_2019,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Foundational Plots
    """)
    return


@app.cell
def _(GT, alt, np, pd):
    def customer_descriptives(df, metric):
        s = df[metric]
        mean = s.mean()
        return {'count': s.count(), 'mean': mean, 'median': s.median(), 'std': s.std(), 'min': s.min(), 'max': s.max(), 'pct_below_mean': (s < mean).mean(), 'percentiles': s.quantile([i / 100 for i in range(5, 100, 5)])}

    def create_percentile_table(df, column, title, subtitle=None, format=None):
        percentile_table = df['percentiles'].reset_index().rename(columns={'index': 'Percentile', column: 'Value'})
        percentile_table['Percentile'] = (percentile_table['Percentile'] * 100).astype(int).astype(str) + '%'
        _gt_table = GT(percentile_table).tab_header(title=title, subtitle=subtitle).tab_options(table_font_size='12px', data_row_padding='4px')
        if format == 'currency':
            _gt_table = _gt_table.fmt_currency(columns='Value', decimals=2)
        elif format == 'pct':
            _gt_table = _gt_table.fmt_percent(columns='Value', decimals=2)
        elif format == 'float':
            _gt_table = _gt_table.fmt_number(columns='Value', decimals=2)
        return (percentile_table, _gt_table)

    def create_bins_labels(bin_width, max_cutoff, min_cutoff=None):
        if min_cutoff is None:
            min_cutoff = 0
            lower_bins = []
            lower_labels = []
        else:
            lower_bins = [-np.inf]
            lower_labels = [f'<{min_cutoff}']
        _bins = lower_bins + list(range(min_cutoff, max_cutoff + bin_width, bin_width)) + [np.inf]
        _labels = lower_labels + [f'{i}-{i + bin_width}' for i in range(min_cutoff, max_cutoff, bin_width)] + [f'{max_cutoff}+']
        return {'bins': _bins, 'labels': _labels}

    def create_distribution(df, column, bins, labels):
        distribution = pd.cut(df[column], bins=bins, labels=labels, right=False).value_counts().sort_index().reset_index().rename(columns={'count': 'Customers', column: f'{column} Range'})
        distribution['Percent'] = distribution['Customers'] / distribution['Customers'].sum()
        return distribution

    def distribution_barplot(distribution, column, title='Customer Distribution', x_title='Range', width=800, height=400, series=None, opacity=1.0):
        data = distribution.rename(columns={f'{column} Range': 'Range'}).astype({'Range': str})
        order = data['Range'].tolist()
        encodings = {'x': alt.X('Range:N', title=x_title, sort=order, axis=alt.Axis(labelAngle=-45, grid=False)), 'y': alt.Y('Percent:Q', title='Customers (%)', axis=alt.Axis(format='%', grid=False)), 'tooltip': [alt.Tooltip('Range:N', title='Range'), alt.Tooltip('Customers:Q', title='Customers', format=','), alt.Tooltip('Percent:Q', title='Customers (%)', format='.1%')]}
        if series is not None:
            data = data.assign(Series=series)
            encodings['color'] = alt.Color('Series:N', title=None)
            encodings['tooltip'] = [alt.Tooltip('Series:N', title='Series')] + encodings['tooltip']
        return alt.Chart(data).mark_bar(opacity=opacity).encode(**encodings).properties(title=title, width=width, height=height)

    def overlay_distributions(*charts, series=None, title='Customer Distribution', opacity=0.6):
        if series is None:
            series = [None] * len(charts)
        elif len(series) != len(charts):
            raise ValueError(f'got {len(series)} series labels for {len(charts)} charts')
        layers = []
        for chart, label in zip(charts, series):
            layer = chart.mark_bar(opacity=opacity).properties(title='')
            if label is not None:
                layer = layer.transform_calculate(Series=alt.expr.toString(label)).encode(color=alt.Color('Series:N', title=None), tooltip=[alt.Tooltip('Series:N', title='Series'), alt.Tooltip('Range:N', title='Range'), alt.Tooltip('Customers:Q', title='Customers', format=','), alt.Tooltip('Percent:Q', title='Customers (%)', format='.1%')])
            layers.append(layer)
        return alt.layer(*layers).properties(title=title)  # Label here rather than in distribution_barplot, so a layer only  # needs a name once it sits next to another one.

    return (
        create_bins_labels,
        create_distribution,
        create_percentile_table,
        customer_descriptives,
        distribution_barplot,
        overlay_distributions,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Distribution of Spend
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Descriptives first (min, max, mean, median, % below mean), then percentiles at 5% intervals (5%…95%), then bin.

    **Findings:** max $6,695 ≈ 37× the mean. Mean $183 > median $113. **69% of customers spend below average.** 5th pct $22.20; 10th pct $30.22; the top 5% each spent more than $578.52.

    **Bins:** width $25, censor at $1000 → 41 bins. (Width $20 → 51 bins, also defensible.)

    **Note:** two customers have exactly $0 spend in 2019; they land in the first bin.
    """)
    return


@app.cell
def _(cust_data_2019, customer_descriptives):
    spend_stats = customer_descriptives(cust_data_2019, "Spend")

    print(
        f"{'Min spend:':<15}${spend_stats['min']:,.2f}"
        f"\n{'Max spend:':<15}${spend_stats['max']:,.2f}"
        f"\n{'Mean spend:':<15}${spend_stats['mean']:,.2f}"
        f"\n{'Median spend:':<15}${spend_stats['median']:,.2f}"
        f"\n{'% below avg.:':<15}{spend_stats['pct_below_mean']:.1%}"
    )
    return (spend_stats,)


@app.cell
def _(spend_stats):
    print(
        f"Mean spend ${spend_stats['mean']:,.0f} is "
        f"{spend_stats['mean']/spend_stats['median']:.1f}× "
        f"the median spend of ${spend_stats['median']:,.0f}."
    )

    print(
        f"\n{spend_stats['pct_below_mean']:.0%} of customers "
        f"spent below the average."
    )

    p = spend_stats["percentiles"]

    print(
        f"\nThe bottom 5% of customers spent "
        f"${p.loc[0.05]:,.2f} or less."
    )

    print(
        f"\nThe bottom 10% of customers spent "
        f"${p.loc[0.10]:,.2f} or less."
    )

    print(
        f"\nThe top 5% of customers spent more than "
        f"${p.loc[0.95]:,.2f}."
    )
    return


@app.cell
def _(create_percentile_table, spend_stats):
    _, _gt_table = create_percentile_table(spend_stats, 'Spend', title='Customer Spend Distribution', subtitle='2019 annual spend percentiles', format='currency')
    _gt_table
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2019,
    distribution_barplot,
):
    distribution_barplot(
        create_distribution(
            cust_data_2019, 
            column="Spend", 
            **create_bins_labels(bin_width=25, max_cutoff=1000)
        ),
        column="Spend",
        title="Customer Spend Distribution (2019)",
        x_title="Annual Spend ($)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Distribution of Profit
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Same structure, but with an explicit **`< $0` bin** for loss-making customers.

    **Findings:** range –$652 to $3,347. Mean $88 > median $54; again **69% below average**. 5th pct $7.70; 10th pct $12.47; top 5% above $282.45.

    **Bins:** width $25, censor at $500, plus the `<0` bin. (Profit mean/median/max run ~45–50% of the corresponding spend figures, which is what motivates the lower cut-off.)
    """)
    return


@app.cell
def _(cust_data_2019, customer_descriptives):
    profit_stats = customer_descriptives(cust_data_2019, "Profit")

    print(
        f"{'Min profit:':<15}${profit_stats['min']:,.2f}"
        f"\n{'Max profit:':<15}${profit_stats['max']:,.2f}"
        f"\n{'Mean profit:':<15}${profit_stats['mean']:,.2f}"
        f"\n{'Median profit:':<15}${profit_stats['median']:,.2f}"
        f"\n{'% below avg.:':<15}{profit_stats['pct_below_mean']:.1%}"
    )
    return (profit_stats,)


@app.cell
def _(profit_stats, spend_stats):
    print(
        f"The mean profits represent {profit_stats['mean'] / spend_stats['mean'] * 100:,.2f}% of mean spend."
        f"\nThe median profits represent {profit_stats['median'] / spend_stats['median'] * 100:,.2f}% of median spend."
        f"\nThe max profits represent {profit_stats['max'] / spend_stats['max'] * 100:,.2f}% of median spend."
        f"\nThis is approximately 45-50% profit margins for corresponding spend numbers"
    )
    return


@app.cell
def _(create_percentile_table, profit_stats):
    _, _gt_table = create_percentile_table(profit_stats, 'Profit', title='Customer Profit Distribution', subtitle='2019 annual profit percentiles', format='currency')
    _gt_table
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2019,
    distribution_barplot,
):
    distribution_barplot(
        create_distribution(
            cust_data_2019, 
            column="Profit",
            **create_bins_labels(
                bin_width=25, 
                max_cutoff=500, 
                min_cutoff=0
            )
        ),
        column="Profit",
        title="Customer Profit Distribution (2019)",
        x_title="Annual Profit ($)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Distribution of Number of Transactions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Simple value-count of `NumTrans`.

    **Findings:** right-skewed (reverse-J). Max = 58 transactions. **63% of customers made exactly one purchase** (20,149 / 31,855), so the mean of 1.9 is misleading.

    **Bins:** width 1, censor at `10+`. (Censoring at 5 is too low — 6.8% of customers made ≥5 transactions.) Keep all non-terminal bins **equal width**; do not do 1 / 2–4 / 5–9 / 10+. If you want unequal groupings, use a table, not a histogram.
    """)
    return


@app.cell
def _(cust_data_2019, customer_descriptives):
    trans_stats = customer_descriptives(cust_data_2019, "NumTrans")

    print(
        f"{'Min trans.:':<15}{trans_stats['min']:,.0f}"
        f"\n{'Max trans.:':<15}{trans_stats['max']:,.0f}"
        f"\n{'Mean trans.:':<15}{trans_stats['mean']:,.2f}"
        f"\n{'Median trans.:':<15}{trans_stats['median']:,.2f}"
        f"\n{'% below avg.:':<15}{trans_stats['pct_below_mean']:.1%}"
    )
    return (trans_stats,)


@app.cell
def _(create_percentile_table, trans_stats):
    _, _gt_table = create_percentile_table(trans_stats, 'NumTrans', title='Customer Transactions Distribution', subtitle='2019 annual transactions percentiles')
    _gt_table
    return


@app.cell
def _(create_distribution, cust_data_2019, distribution_barplot, np):
    _bins = list(range(1, 10 + 1, 1)) + [np.inf]
    _labels = [str(i) for i in range(1, 10, 1)] + ['10+']
    distribution_barplot(create_distribution(cust_data_2019, column='NumTrans', bins=_bins, labels=_labels), column='NumTrans', title='Customer Transactions Distribution (2019)', x_title='Annual Transactions')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Distribution of Average Spend per Transaction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Per customer: `avg_spend = Spend / NumTrans`.

    **Bins:** width $25, censor at $500. ($20 / $300 also reasonable; the $500 cut-off shows the tail better.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Two different "average spend per transaction" numbers**

    These are **not** the same quantity and both appear in practice:

    - Average spend per customer = **$183**, average transactions per customer = **1.9** → $183 / 1.9 ≈ **$96**
    - Mean of each customer's own average spend per transaction = **$99**

    The gap isn't an error. They are different estimators.

    **AOV (Weighted-average spend per transaction value)**

    Start from the ratio of the two per-customer means. The $I$ cancels, leaving total spend over total transactions:

    $$
    \frac{\frac{1}{I}\sum_{i=1}^{I}\text{spend}_i}{\frac{1}{I}\sum_{i=1}^{I}\text{trans}_i}
    =\frac{\sum_{i=1}^{I}\text{spend}_i}{\sum_{i=1}^{I}\text{trans}_i}
    $$

    Now rewrite the numerator by multiplying and dividing each customer's spend by their transaction count:

    $$
    =\frac{\sum_{i=1}^{I}\text{trans}_i\times\dfrac{\text{spend}_i}{\text{trans}_i}}{\sum_{i=1}^{I}\text{trans}_i}
    =\sum_{i=1}^{I}\left(\frac{\text{trans}_i}{\sum_{j=1}^{I}\text{trans}_j}\right)\frac{\text{spend}_i}{\text{trans}_i}
    $$

    So it is a weighted average of individual average spend per transaction, where each customer's weight is their **share of total transactions**. Frequent buyers dominate it.

    **Unweighted mean of the per-customer average**

    $$
    \frac{1}{I}\sum_{i=1}^{I}\frac{\text{spend}_i}{\text{trans}_i}
    $$

    Every customer counts once, regardless of how much they bought. The one-and-done buyers (63% of the base) carry as much weight as the customer with 58 transactions.

    **Why it matters**

    The two coincide **only** when $\text{trans}_i$ is identical across all $I$ customers. That never happens in a real customer base, so the two numbers will always diverge — and the direction of the gap tells you something. Here $96 < 99$, meaning heavier buyers have *lower* average baskets than light buyers.

    Naming convention from the book, worth adopting so you never confuse them again:

    | Quantity | Formula | 2019 value |
    |---|---|---|
    | **AOV** (Average Order Value) | $\sum \text{spend}_i \big/ \sum \text{trans}_i$ | $96 |
    | Mean average spend per transaction | $\frac{1}{I}\sum \text{spend}_i / \text{trans}_i$ | $99 |

    "AOV" always means the transaction-weighted one. When you see an "average average spend" number in someone else's report, find out which one it is before you act on it.
    """)
    return


@app.cell
def _(cust_data_2019, customer_descriptives):
    # per-customer average spend per transaction
    cust_data_2019['AvgSpendPerTrans'] = cust_data_2019['Spend'] / cust_data_2019['NumTrans']

    avg_spend_stats = customer_descriptives(cust_data_2019, "AvgSpendPerTrans")

    print(
        f"{'Min spend:':<15}${avg_spend_stats['min']:,.2f}"
        f"\n{'Max spend:':<15}${avg_spend_stats['max']:,.2f}"
        f"\n{'Mean spend:':<15}${avg_spend_stats['mean']:,.2f}"
        f"\n{'Median spend:':<15}${avg_spend_stats['median']:,.2f}"
        f"\n{'% below avg.:':<15}{avg_spend_stats['pct_below_mean']:.1%}"
    )
    return (avg_spend_stats,)


@app.cell
def _(avg_spend_stats, create_percentile_table):
    _, _gt_table = create_percentile_table(avg_spend_stats, 'AvgSpendPerTrans', title='Average Spend per Transactions Distribution', subtitle=None, format='currency')
    _gt_table
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2019,
    distribution_barplot,
):
    distribution_barplot(
        create_distribution(
            cust_data_2019, 
            column="AvgSpendPerTrans",
            **create_bins_labels(
                bin_width=25, 
                max_cutoff=500
            )
        ),
        column="AvgSpendPerTrans",
        title="Average Spend per Transactions Distribution (2019)",
        x_title="Average Spend per Transactions ($)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Average Spend per Transaction, by Transaction Level
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Given the variability in both the number of transactions and average spend per transaction across customers, it is natural to ask whether these two quantities are related.

    Group customers by transaction count (1, 2, …, 9, `10+` — same bins as §1.3). For each group report: **mean, std dev, min, max, 5th pct, median, 95th pct** of per-customer average spend. Purpose: is average order value related to purchase frequency?
    """)
    return


@app.cell
def _(GT, cust_data_2019, np, pd):
    _bins = list(range(1, 10 + 1, 1)) + [np.inf]
    _labels = [str(i) for i in range(1, 10, 1)] + ['10+']
    cust_data_2019['TransBin'] = pd.cut(cust_data_2019['NumTrans'], bins=_bins, labels=_labels, right=False)
    avg_spend_per_trans = cust_data_2019.groupby('TransBin', as_index=False).agg(Mean=('AvgSpendPerTrans', 'mean'), Std=('AvgSpendPerTrans', 'std'), Min=('AvgSpendPerTrans', 'min'), P05=('AvgSpendPerTrans', lambda s: s.quantile(0.05)), Median=('AvgSpendPerTrans', 'median'), P95=('AvgSpendPerTrans', lambda s: s.quantile(0.95)), Max=('AvgSpendPerTrans', 'max'))
    GT(avg_spend_per_trans).tab_header(title='Analysis of Average Spend per Transaction', subtitle='Analysis of average spend per transaction by transaction level').fmt_currency(columns=list(avg_spend_per_trans.columns[1:]), decimals=2).tab_options(table_font_size='12px', data_row_padding='4px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Distribution of Average Margin
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Per customer: `margin = Profit / Spend`, defined only where `Spend > 0` (two customers have zero spend — exclude them / set NaN, don't zero-fill).

    **Caveat:** this is the *overall* margin across all of a customer's 2019 purchasing, not the average of their transaction-level margins. Transaction-level margins aren't recoverable because the source data is aggregated to the quarter.

    **Findings:** unlike the other four distributions, margin is **left-skewed**.

    **Bins:** width 5%, plus a `< 0%` bin for loss-makers. The book keeps the (85,90], (90,95], (95,100] bins visible even though they're empty — your call.
    """)
    return


@app.cell
def _(cust_data_2019, customer_descriptives):
    cust_data_2019_1 = cust_data_2019.assign(Margin=lambda x: x['Profit'] / x['Spend'] * 100)
    avg_margin_stats = customer_descriptives(cust_data_2019_1.query('Spend > 0'), 'Margin')
    print(f"{'Min margin:':<15}{avg_margin_stats['min']:,.2f}\n{'Max margin:':<15}{avg_margin_stats['max']:,.2f}\n{'Mean margin:':<15}{avg_margin_stats['mean']:,.2f}\n{'Median margin:':<15}{avg_margin_stats['median']:,.2f}\n{'% below avg.:':<15}{avg_margin_stats['pct_below_mean']:.1%}")
    return avg_margin_stats, cust_data_2019_1


@app.cell
def _(avg_margin_stats, create_percentile_table):
    _, _gt_table = create_percentile_table(avg_margin_stats, 'Margin', title='Average Margin (%) Distribution', subtitle=None, format='float')
    _gt_table
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2019_1,
    distribution_barplot,
):
    distribution_barplot(create_distribution(cust_data_2019_1.query('Spend > 0'), column='Margin', **create_bins_labels(bin_width=5, max_cutoff=100, min_cutoff=0)), column='Margin', title='Average Margin Distribution (2019)', x_title='Margin (%)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Decile analyses
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### Customer decile report — each decile = 10% of *customers*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Sort customers by 2019 profit, descending.
    2. Rank 1…N.
    3. `decile = int(10 * (rank - 1) / N) + 1` — note the `rank - 1`, which is what keeps decile 1 from being off by one customer.
    4. Aggregate by decile: customer count, total transactions, total spend, total profit.
    5. Then apply the profit decomposition to produce the report columns:

    | Column | Formula |
    |---|---|
    | % of customers | decile customers / total customers |
    | % of transactions | decile trans / total trans |
    | % of revenue | decile spend / total spend |
    | % of profit | decile profit / total profit |
    | Avg spend per customer | decile spend / decile customers |
    | Avg profit per customer | decile profit / decile customers |
    | AOF | decile trans / decile customers |
    | AOV | decile spend / decile trans |
    | Avg margin | decile profit / decile spend |

    The bottom row (totals) gives the firm-level AOF/AOV/margin.

    ```mermaid
    flowchart LR
        P["Profit"] --> X1(("×"))
        X1 --> NC["# Customers"]
        X1 --> APC["Average profit<br/>per customer"]

        APC --> X2(("×"))
        X2 --> AM["Average<br/>margin"]
        X2 --> ASC["Average spend<br/>per customer"]

        ASC --> X3(("×"))
        X3 --> AOF["Average order<br/>frequency (AOF)"]
        X3 --> AOV["Average order<br/>value (AOV)"]

        classDef box fill:#ffffff,stroke:#333,stroke-width:1.5px,color:#000
        classDef op fill:#333,stroke:#333,color:#fff
        class P,NC,APC,AM,ASC,AOF,AOV box
        class X1,X2,X3 op
    ```
    """)
    return


@app.cell
def _(GT, cust_data_2019_1, pd):
    cust_data_2019_1['ProfitRank'] = pd.qcut(cust_data_2019_1['Profit'].rank(method='first', ascending=False), q=10, labels=False) + 1
    _profit_rank = cust_data_2019_1.groupby('ProfitRank', as_index=False).agg(Customers=('CustomerID', 'count'), Transactions=('NumTrans', 'sum'), Spend=('Spend', 'sum'), Profit=('Profit', 'sum')).assign(PctCust=lambda x: x['Customers'] / x['Customers'].sum(), PctTrans=lambda x: x['Transactions'] / x['Transactions'].sum(), PctSpend=lambda x: x['Spend'] / x['Spend'].sum(), PctProfit=lambda x: x['Profit'] / x['Profit'].sum(), AvgSpendCust=lambda x: x['Spend'] / x['Customers'], AvgProfitCust=lambda x: x['Profit'] / x['Customers'], AOF=lambda x: x['Transactions'] / x['Customers'], AOV=lambda x: x['Spend'] / x['Transactions'], AvgMargin=lambda x: x['Profit'] / x['Spend']).drop(columns=['Customers', 'Transactions', 'Spend', 'Profit'])
    _fields = ['Decile', '% Cust.', '% Trans.', '% Spend', '% Profit', 'Avg Spend/Cust.', 'Avg. Profit/Cust.', 'AOF', 'AOV', 'Avg. Margin']
    _profit_rank = _profit_rank.rename(columns={old: new for old, new in zip(_profit_rank.columns, _fields)})
    GT(_profit_rank).tab_header(title='Customer Decile Report').fmt_percent(columns=_fields[1:5] + [_fields[-1]], decimals=1).fmt_currency(columns=_fields[5:7] + [_fields[8]]).fmt_number(columns=_fields[7]).tab_options(table_font_size='12px', data_row_padding='4px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Profit decile report — each decile = 10% of *profit*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Sort by profit descending, compute **cumulative profit**.
    2. Decile boundaries in cumulative-profit space: `k × (total_profit / 10)` for k = 1…9.
    3. For each boundary, find the individual customer profit value at the point the cumulative series first crosses it. These become the profit cut-offs.
    4. Assign each customer to a decile by comparing their own profit against those cut-offs.
    5. Aggregate and apply the same decomposition table as above.
    """)
    return


@app.cell
def _(np):
    def decile_labels(df, value_col="Profit", n=10):
        d = df.sort_values(value_col, ascending=False, kind="stable").reset_index(drop=True)

        cents = np.round(d[value_col].to_numpy() * 100).astype(np.int64)
        cum   = cents.cumsum()
        total = cum[-1]

        thresholds = np.arange(1, n) * total / n

        boundaries = cents[np.searchsorted(cum, thresholds, side="right")]
        # Profit cutoff
        d["ProfitDecile"] = (n - np.searchsorted(boundaries[::-1], cents, side="left")).astype("int8")
        return d, thresholds / 100, boundaries / 100

    return (decile_labels,)


@app.cell
def _(GT, cust_data_2019_1, decile_labels):
    cust_profit = decile_labels(cust_data_2019_1, 'Profit')[0]
    _profit_rank = cust_profit.groupby('ProfitDecile', as_index=False).agg(Customers=('CustomerID', 'count'), Transactions=('NumTrans', 'sum'), Spend=('Spend', 'sum'), Profit=('Profit', 'sum')).assign(PctCust=lambda x: x['Customers'] / x['Customers'].sum(), PctTrans=lambda x: x['Transactions'] / x['Transactions'].sum(), PctSpend=lambda x: x['Spend'] / x['Spend'].sum(), PctProfit=lambda x: x['Profit'] / x['Profit'].sum(), AvgSpendCust=lambda x: x['Spend'] / x['Customers'], AvgProfitCust=lambda x: x['Profit'] / x['Customers'], AOF=lambda x: x['Transactions'] / x['Customers'], AOV=lambda x: x['Spend'] / x['Transactions'], AvgMargin=lambda x: x['Profit'] / x['Spend']).drop(columns=['Customers', 'Transactions', 'Spend', 'Profit'])
    _fields = ['Decile', '% Cust.', '% Trans.', '% Spend', '% Profit', 'Avg Spend/Cust.', 'Avg. Profit/Cust.', 'AOF', 'AOV', 'Avg. Margin']
    _profit_rank = _profit_rank.rename(columns={old: new for old, new in zip(_profit_rank.columns, _fields)})
    GT(_profit_rank).tab_header(title='Profit Decile Report').fmt_percent(columns=_fields[1:5] + [_fields[-1]], decimals=2).fmt_currency(columns=_fields[5:7] + [_fields[8]]).fmt_number(columns=_fields[7]).tab_options(table_font_size='12px', data_row_padding='4px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Watch out:** cumulative profit is **not monotonic**. It peaks at **$2,802,771.95** and then *declines* to the total of **$2,798,903.68**, because **263 customers are loss-making**. Decile 1 cut-off lands at ≈ **$545.53**, decile 2 at ≈ **$345.25**. Loss-makers all end up in decile 10.

    *Variant worth building:* pull the loss-makers out as a separate 11th group rather than burying them in decile 10.

    *Variant worth building:* if you don't have cost/profit data, run the same decile analysis on **revenue**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 2 — What changed between two periods? (2018 vs 2019)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Objective:** decompose year-on-year change in firm performance into changes in customer behaviour.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Working dataset
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One row per customer active in **either** 2018 or 2019 (outer join of the two annual aggregates, zero-filled): `trans_2018, spend_2018, profit_2018, trans_2019, spend_2019, profit_2019`. **48,238 customers.**

    Add a `years` status flag:
    - `both` if active in both years
    - `2018 only`
    - `2019 only`
    """)
    return


@app.cell
def _(cust_data):
    cust_data_2018 = yearly_cust_data(cust_data, 2018)
    cust_data_2019_2 = yearly_cust_data(cust_data, 2019)
    cust_2018_2019 = cust_data_2018.merge(cust_data_2019_2, on='CustomerID', how='outer', suffixes=('_2018', '_2019'), indicator=True).assign(Status=lambda df: df['_merge'].map({'both': 'Active Both Years', 'left_only': '2018 Only (Lapsed)', 'right_only': '2019 Only (New/Reactivated)'})).drop(columns='_merge')
    return cust_2018_2019, cust_data_2018, cust_data_2019_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Headline
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | | 2018 | 2019 | Δ |
    |---|---|---|---|
    | Revenue | $4,815,502 | $5,836,712 | +21% |
    | Profit | $2,290,343 | $2,798,904 | +22% |
    | Active customers | 26,254 | 31,855 | +21% |
    """)
    return


@app.cell
def _(GT, cust_2018_2019, cust_data_2018, cust_data_2019_2, pd):
    summary_1 = pd.concat([cust_2018_2019.filter(like='_2018').sum(numeric_only=True).rename(lambda c: c.removesuffix('_2018')).rename('2018'), cust_2018_2019.filter(like='_2019').sum(numeric_only=True).rename(lambda c: c.removesuffix('_2019')).rename('2019')], axis=1)
    summary_1['Δ'] = (summary_1['2019'] - summary_1['2018']) / summary_1['2018']
    active_2018 = cust_data_2018['CustomerID'].nunique()
    active_2019 = cust_data_2019_2['CustomerID'].nunique()
    summary_1.loc['Active customers'] = [active_2018, active_2019, (active_2019 - active_2018) / active_2018]
    summary_1 = summary_1.drop(index='NumTrans').reset_index(names='')
    GT(summary_1).tab_header(title='Spend, Profit, & Active Customer YoY Summary').fmt_percent(columns=['Δ'], decimals=1).fmt_currency(columns=['2018', '2019'], decimals=0).fmt_number(columns=['2018', '2019'], rows=[2], decimals=0).tab_options(table_font_size='12px', data_row_padding='4px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Overlaid distributions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Re-run each Lens 1 distribution for 2018 and 2019 on the same axes, using **identical bin edges** and **relative frequencies** (the customer counts differ, so raw counts are not comparable).

    **Finding:** the spend distribution for 2018 actives is very close to that for 2019 actives — the shape of customer heterogeneity is stable; the customer *count* is what moved. (Repeat for profit, transactions, avg spend per transaction, margin.)
    """)
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019_2,
    distribution_barplot,
    overlay_distributions,
):
    overlay_distributions(distribution_barplot(create_distribution(cust_data_2018, column='Spend', **create_bins_labels(bin_width=25, max_cutoff=1000)), column='Spend', x_title='Annual Spend ($)'), distribution_barplot(create_distribution(cust_data_2019_2, column='Spend', **create_bins_labels(bin_width=25, max_cutoff=1000)), column='Spend', x_title='Annual Spend ($)'), series=('2018', '2019'), title='Distribution of Customer Spend (2018 vs. 2019)', opacity=0.5)
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019_2,
    distribution_barplot,
    overlay_distributions,
):
    overlay_distributions(distribution_barplot(create_distribution(cust_data_2018, column='Profit', **create_bins_labels(bin_width=25, max_cutoff=500, min_cutoff=0)), column='Profit', x_title='Annual Profit ($)'), distribution_barplot(create_distribution(cust_data_2019_2, column='Profit', **create_bins_labels(bin_width=25, max_cutoff=500, min_cutoff=0)), column='Profit', x_title='Annual Profit ($)'), series=('2018', '2019'), title='Distribution of Customer Profit (2018 vs. 2019)', opacity=0.5)
    return


@app.cell
def _(
    create_distribution,
    cust_data_2018,
    cust_data_2019_2,
    distribution_barplot,
    np,
    overlay_distributions,
):
    _bins = list(range(1, 10 + 1, 1)) + [np.inf]
    _labels = [str(i) for i in range(1, 10, 1)] + ['10+']
    overlay_distributions(distribution_barplot(create_distribution(cust_data_2018, column='NumTrans', bins=_bins, labels=_labels), column='NumTrans', x_title='Annual Transactions'), distribution_barplot(create_distribution(cust_data_2019_2, column='NumTrans', bins=_bins, labels=_labels), column='NumTrans', x_title='Annual Transactions'), series=('2018', '2019'), title='Distribution of Customer Transactions (2018 vs. 2019)', opacity=0.5)
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019_2,
    distribution_barplot,
    overlay_distributions,
):
    cust_data_2018['AvgSpendPerTrans'] = cust_data_2018['Spend'] / cust_data_2018['NumTrans']
    cust_data_2019_2['AvgSpendPerTrans'] = cust_data_2019_2['Spend'] / cust_data_2019_2['NumTrans']
    overlay_distributions(distribution_barplot(create_distribution(cust_data_2018, column='AvgSpendPerTrans', **create_bins_labels(bin_width=25, max_cutoff=500)), column='AvgSpendPerTrans', x_title='Average Spend per Transactions ($)'), distribution_barplot(create_distribution(cust_data_2019_2, column='AvgSpendPerTrans', **create_bins_labels(bin_width=25, max_cutoff=500)), column='AvgSpendPerTrans', x_title='Average Spend per Transactions ($)'), series=('2018', '2019'), title='Distribution of Average Spend per Transactions (2018 vs. 2019)', opacity=0.5)
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019_2,
    distribution_barplot,
    overlay_distributions,
):
    cust_data_2018_1 = cust_data_2018.assign(Margin=lambda x: x['Profit'] / x['Spend'] * 100)
    cust_data_2019_3 = cust_data_2019_2.assign(Margin=lambda x: x['Profit'] / x['Spend'] * 100)
    overlay_distributions(distribution_barplot(create_distribution(cust_data_2018_1.query('Spend > 0'), column='Margin', **create_bins_labels(bin_width=5, max_cutoff=100, min_cutoff=0)), column='Margin', x_title='Margin (%)'), distribution_barplot(create_distribution(cust_data_2019_3.query('Spend > 0'), column='Margin', **create_bins_labels(bin_width=5, max_cutoff=100, min_cutoff=0)), column='Margin', x_title='Margin (%)'), series=('2018', '2019'), title='Distribution of Average Margin (2018 vs. 2019)', opacity=0.5)
    return cust_data_2018_1, cust_data_2019_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Customer overlap
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | Group | Customers |
    |---|---|
    | Active 2018 | 26,254 |
    | Active 2019 | 31,855 |
    | Active both years | 9,871 |
    | 2018 only (lapsed) | 16,383 |
    | 2019 only (new/reactivated) | 21,984 |

    Repeat buyers are **38%** of 2018 actives and **31%** of 2019 actives.

    **Area-proportional Venn diagram** (see Appendix A below for the geometry — it's a small numerical solve, easy in `scipy.optimize`).
    """)
    return


@app.cell
def _(cust_2018_2019):
    summary_2 = cust_2018_2019.groupby('Status').agg(Customers=('CustomerID', 'count'))
    summary_2.loc['Active 2018'] = summary_2.loc['2018 Only (Lapsed)'] + summary_2.loc['Active Both Years']
    summary_2.loc['Active 2019'] = summary_2.loc['2019 Only (New/Reactivated)'] + summary_2.loc['Active Both Years']
    print(f"Repeat buyers are {(summary_2.loc['Active Both Years'] / summary_2.loc['Active 2018']).item() * 100:.0f}% of 2018 active customers and {(summary_2.loc['Active Both Years'] / summary_2.loc['Active 2019']).item() * 100:.0f}% of 2019 active customers")
    return (summary_2,)


@app.cell
def _(GT, summary_2):
    GT(summary_2.reset_index(names='Group')).tab_header(title='Customer Overlap').fmt_number(columns='Customers', decimals=0).tab_options(table_font_size='12px', data_row_padding='4px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Area-proportional Venn diagram**

    Venn diagrams can be created with `matplotlib`, solving it is trivial and gives you exact control.

    In order to create the Venn diagram, we need to compute the radius of each circle ($R$ and $r$), and the distance between the centers of the two circles ($d$).

    Given: 2018 actives = 26,254; 2019 actives = 31,855; both = 9,871.

    Considering the ratio of the number of active customers in 2019 to the number of customers active in 2018, we have

    $$
    \frac{31,855}{26,254} = \frac{\pi r^{2}}{\pi R^{2}}
    $$

    Set the 2018 circle radius **R = 1**. Then, requiring areas proportional to counts:

    $$
    r = \sqrt{\frac{31,855}{26,254}} \approx 1.1015
    $$

    Therefore, the area of the circle associated with 2018 is $\pi$, the area of the circle associated with 2019 is $\pi(1.1015)^2$ and the area of the overlap between the two circles is:

    $$
    A^{\star} = \pi \left(\frac{9,871}{26,254}\right) = 1.1812
    $$

    Solve numerically for the centre-to-centre distance **d** satisfying the standard [circle-circle intersection area](https://mathworld.wolfram.com/Circle-CircleIntersection.html):

    $$
    \begin{split}
    A(d) &= r^2 \cos^{-1}\left(\frac{d^2+r^2-R^2}{2dr}\right) + R^2 \cos^{-1}\left(\frac{d^2-r^2+R^2}{2dR}\right) \\
    &-\frac{1}{2} \sqrt{(d+r-R)(d-r+R)(-d+r+R)(d+r+R)}
    \end{split}
    $$

    $$
    \min
    $$

    Minimise `(A_target − A(d))²` over d. **Solution: d = 1.1469.**

    $$
    d^{\star} = \arg\min_{d}\;\bigl(A^\star - A(d)\bigr)^{2}
    \qquad \text{s.t.}\quad |R-r| \le d \le R+r
    $$

    We use an equivalent 1-D root-finder `brentq` since the objective's minimum is zero at an interior point where $A(d)$ is monotonic:

    $$
    \text{find } d^{\star} \in \bigl[\,|R-r|,\;R+r\,\bigr] \;\text{ such that }\; A(d^{\star}) - A^\star = 0
    $$

    The bound constraint is the physically valid range for $d$: at $d = |R-r|$ one circle sits fully inside the other (overlap is the smaller disc), and at $d = R+r$ the circles are externally tangent (overlap is zero). Across that interval $A(d)$ is strictly monotonically decreasing, so the root is unique and Brent's method converges on it directly — which is why the root-find is preferable to the squared-error minimization in practice.

    Draw: circle radius 1 centred at `(1, max(1, r))`; circle radius r centred at `(1 + d, max(1, r))`.
    """)
    return


@app.cell
def _(np, plt, summary_2):
    from matplotlib.patches import Circle
    from scipy.optimize import brentq
    n2018 = summary_2.loc['Active 2018'].item()
    n2019 = summary_2.loc['Active 2019'].item()
    nboth = summary_2.loc['Active Both Years'].item()
    R = 1.0
    r = np.sqrt(n2019 / n2018)
    A_target = np.pi * (nboth / n2018)

    def lens_area(d, R, r):
        """Intersection area of two circles, radii R and r, centres d apart"""
        if d >= R + r:
            return 0.0
        if d <= abs(R - r):
            return np.pi * min(R, r) ** 2
        a1 = R ** 2 * np.arccos(np.clip((d ** 2 + R ** 2 - r ** 2) / (2 * d * R), -1, 1))
        a2 = r ** 2 * np.arccos(np.clip((d ** 2 + r ** 2 - R ** 2) / (2 * d * r), -1, 1))
        a3 = 0.5 * np.sqrt(max((-d + r + R) * (d - r + R) * (d + r - R) * (d + r + R), 0.0))
        return a1 + a2 - a3
    d = brentq(lambda d: lens_area(d, R, r) - A_target, a=abs(R - r) + 1e-09, b=R + r - 1e-09)
    cy = max(R, r)
    c1, c2 = ((R, cy), (R + d, cy))
    _fig, _ax = plt.subplots(figsize=(5, 5))
    _ax.add_patch(Circle(c1, R, facecolor='#4C72B0', edgecolor='none', alpha=0.45))
    _ax.add_patch(Circle(c2, r, facecolor='#DD8452', edgecolor='none', alpha=0.45))
    x_lens = R + (d ** 2 + R ** 2 - r ** 2) / (2 * d)
    _ax.text(c1[0] - 0.45 * R, cy, f'2018 only\n{n2018 - nboth:,}', ha='center', va='center')
    _ax.text(x_lens, cy, f'Both\n{nboth:,}', ha='center', va='center')
    _ax.text(c2[0] + 0.45 * r, cy, f'2019 only\n{n2019 - nboth:,}', ha='center', va='center')
    _ax.set_xlim(-0.2, R + d + r + 0.2)
    _ax.set_ylim(cy - r - 0.2, cy + r + 0.2)
    _ax.set_aspect('equal')
    _ax.axis('off')
    _ax.set_title('Active customers: 2018 vs 2019 (area-proportional)')
    plt.tight_layout()
    plt.show()
    print(f'r = {r:.4f}   A_target = {A_target:.4f}   d = {d:.4f}')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Profit by Activity Group
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cross-tabulate `years` against 2018 profit and 2019 profit:

    | Group | 2018 profit | 2019 profit |
    |---|---|---|
    | Both years | $1,216,397 | $1,183,778 |
    | 2018 only | $1,073,946 | — |
    | 2019 only | — | $1,615,125 |
    | **Total** | **$2,290,295** | **$2,798,910** |

    **Findings:** the both-years group produces **53% of 2018 profit but only 42% of 2019 profit**, and their profit *fell* by **≈ $32,618** year on year. Growth came entirely from acquisition. Repeat customers are over-represented in profit relative to their headcount share (38%/31%) — explain that gap with the AOF × AOV × Margin decomposition applied to each of the three groups (active customers, total trans, total spend, total profit → AOF, AOV, margin per group per year).
    """)
    return


@app.cell
def _(GT, cust_2018_2019):
    summary_3 = cust_2018_2019.groupby('Status').agg(Y2018=('Profit_2018', 'sum'), Y2019=('Profit_2019', 'sum'))
    summary_3.loc['Total'] = summary_3.sum()
    GT(summary_3.reset_index(names='Group')).tab_header(title='Profit by Activity Group').fmt_currency(columns=['Y2018', 'Y2019'], decimals=0).tab_options(table_font_size='12px', data_row_padding='4px')
    return (summary_3,)


@app.cell
def _(plt, summary_3):
    both_18 = summary_3.loc['Active Both Years', 'Y2018']
    both_19 = summary_3.loc['Active Both Years', 'Y2019']
    only_18 = summary_3.loc['2018 Only (Lapsed)', 'Y2018']
    only_19 = summary_3.loc['2019 Only (New/Reactivated)', 'Y2019']
    tot_18 = summary_3.loc['Total', 'Y2018']
    tot_19 = summary_3.loc['Total', 'Y2019']
    delta_both = both_19 - both_18
    lo_both = min(both_18, both_19)
    k = 1000
    money = lambda v: f'${v / k:,.0f}'
    solid = dict(facecolor='white', edgecolor='black', linewidth=0.6)
    dotted = dict(facecolor=(0.298, 0.447, 0.69, 0.45), edgecolor='black', linewidth=0.6)
    dashed = dict(facecolor=(0.867, 0.518, 0.322, 0.45), edgecolor='black', linewidth=0.6)
    w = 0.7
    _fig, _ax = plt.subplots(dpi=100)
    _ax.bar(0, both_18 / k, w, bottom=0, **solid)
    _ax.bar(0, only_18 / k, w, bottom=both_18 / k, **dotted)
    _ax.bar(1, only_18 / k, w, bottom=both_18 / k, **dotted)
    _ax.bar(2, abs(delta_both) / k, w, bottom=lo_both / k, **solid)
    _ax.bar(3, only_19 / k, w, bottom=both_19 / k, **dashed)
    _ax.bar(4, both_19 / k, w, bottom=0, **solid)
    _ax.bar(4, only_19 / k, w, bottom=both_19 / k, **dashed)

    def hline(x0, x1, y):
        _ax.plot([x0, x1], [y / k, y / k], ls=':', color='black', lw=1)
    hline(0 + w / 2, 1 - w / 2, tot_18)
    hline(3 + w / 2, 4 - w / 2, tot_19)
    hline(0 + w / 2, 2 - w / 2, both_18)
    hline(2 + w / 2, 4 - w / 2, both_19)
    _ax.text(0, tot_18 / k, money(tot_18), ha='center', va='bottom')
    _ax.text(4, tot_19 / k, money(tot_19), ha='center', va='bottom')
    _ax.text(0, both_18 / 2 / k, 'Both\nyears', ha='center', va='center')
    _ax.text(0, (both_18 + only_18 / 2) / k, '2018\nonly', ha='center', va='center')
    _ax.text(4, both_19 / 2 / k, 'Both\nyears', ha='center', va='center')
    _ax.text(4, (both_19 + only_19 / 2) / k, '2019\nonly', ha='center', va='center')
    _ax.text(1, (both_18 + only_18 / 2) / k, money(only_18), ha='center', va='center')
    _ax.text(2, lo_both / k, f'-{money(abs(delta_both))}', ha='center', va='top')
    _ax.text(3, (both_19 + only_19 / 2) / k, money(only_19), ha='center', va='center')
    _ax.set_xticks([0, 4])
    _ax.set_xticklabels(['2018', '2019'])
    _ax.set_yticks([])
    for s in ('top', 'right', 'left'):
        _ax.spines[s].set_visible(False)
    _ax.set_ylim(0, tot_19 / k * 1.12)
    _ax.set_xlim(-0.6, 4.6)
    _ax.set_title('Decomposition of annual (customer) profit ($000)')
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(cust_2018_2019):
    flows = (
        cust_2018_2019
        .melt(
            id_vars=["CustomerID", "Status"],
            value_vars=["NumTrans_2018", "NumTrans_2019", "Spend_2018",
                          "Spend_2019", "Profit_2018", "Profit_2019"],
            var_name="MetricYear", value_name="Value"
        ).assign(
            Metric=lambda d: d["MetricYear"].str.rsplit("_", n=1).str[0],
            Year=lambda d: d["MetricYear"].str.rsplit("_", n=1).str[-1]
        )
    )

    # flows grid: sum with min_count=1 so all-NaN groups stay NaN
    g = (
        flows
        .groupby(["Status", "Metric", "Year"])["Value"].sum(min_count=1)
        .unstack("Metric")
    )        # rows = Status×Year, cols = the 3 flows

    # headcount grid + derived ratios, all vectorized on the flow columns
    g["NumCust"] = (
        flows
        .assign(active=lambda d: d["Value"].notna())
        .query("Metric == 'NumTrans'")
        .groupby(["Status", "Year"])["active"].sum()
        .where(lambda s: s > 0) # 0 → NaN in one move
    )

    g["AOF"] = g["NumTrans"] / g["NumCust"]
    g["AOV"] = g["Spend"] / g["NumTrans"]
    g["Margin"] = g["Profit"] / g["Spend"]
    return (g,)


@app.cell
def _(GT, g):
    crosstab = (
        g.stack().rename("Value")
        .unstack("Year").reset_index()
        .rename(columns={"level_1": "Metric"})
    )

    (
        GT(crosstab, groupname_col="Status", rowname_col="Metric")
        .tab_header(
            title="Performance Summary & Decomposition",
            subtitle="By Customer Group and Year"
        ).tab_options(
            table_font_size="12px", 
            data_row_padding="4px"
        ).fmt_number(
            columns=["2018", "2019"], 
            decimals=2, 
            use_seps=True
        ).fmt_number(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].isin(["NumCust", "NumTrans"]),
            decimals=0, use_seps=True
        ).fmt_currency(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].isin(["Spend", "Profit"]),
            currency="USD", decimals=0
        ).fmt_percent(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].eq("Margin"),
            decimals=1
        ).sub_missing(missing_text="")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Decile Change Analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Do high-value customers stay high-value?

    1. Compute **profit-decile boundaries separately for 2018 and 2019** (same cumulative-profit method as §1.7b).
    2. Compare them — in this dataset they come out very close. So use a **common set of cut-offs for both years**: average the two years' thresholds and round to the nearest $5, giving:
       - **545, 350, 255, 195, 150, 115, 90, 65, 40**
       - Decile 1 = profit > $545; decile 2 = (350, 545]; … decile 10 = ≤ $40 (including all negatives).

    3. Assign every customer a 2018 decile and a 2019 decile using those cut-offs. Customers inactive in a year get profit 0 → decile 10, which is harmless because you filter by `years` before tabulating.
    4. Build a 2018-decile × 2019-decile cross-tab **restricted to the `both` group** (9,871 customers).
    5. Append a **`2018 only` column** (counts by 2018 decile, 16,383 customers) and a **`2019 only` row** (counts by 2019 decile, 21,984 customers).
    6. Row totals as % of 26,254; column totals as % of 31,855.

    **Trade-off to be explicit about:** common cut-offs mean each decile no longer holds exactly 10% of each year's profit. Year-specific cut-offs preserve the 10%-of-profit property but make the transition matrix harder to read. Analyst's call.

    **Finding to expect:** heavy mass on the diagonal and just below it, plus a very large `2018 only` column concentrated in the low deciles — i.e. churn is heaviest among low-value customers, but decile 1 is not immune.
    """)
    return


@app.cell
def _(
    cust_2018_2019,
    cust_data_2018_1,
    cust_data_2019_3,
    decile_labels,
    np,
    pd,
):
    _, thresholds_2018, boundaries_2018 = decile_labels(cust_data_2018_1, 'Profit', n=10)
    _, thresholds_2019, boundaries_2019 = decile_labels(cust_data_2019_3, 'Profit', n=10)
    average_boundaries = np.round((boundaries_2019 + boundaries_2018) / 2 / 5) * 5

    def decile(s):
        v = s.to_numpy()
        out = 10 - np.searchsorted(average_boundaries[::-1], v, side='left')
        return np.where(np.isnan(v), np.nan, out)
    _tbl = cust_2018_2019.assign(Row=lambda d: decile(d['Profit_2018']), Col=lambda d: decile(d['Profit_2019'])).fillna({'Row': '2019 Only', 'Col': '2018 Only'})
    order_r = [*range(1, 11), '2019 Only']
    order_c = [*range(1, 11), '2018 Only']
    table = pd.crosstab(_tbl['Row'], _tbl['Col'], margins=True, margins_name='Total').reindex(index=[*order_r, 'Total'], columns=[*order_c, 'Total'], fill_value=0)
    return (table,)


@app.cell
def _(GT, cust_data_2018_1, cust_data_2019_3, loc, np, style, table):
    _tbl = table.copy()
    _tbl.columns = [str(c) for c in _tbl.columns]
    _tbl.index = [str(i) for i in _tbl.index]
    _tbl['% 2018'] = _tbl['Total'] / cust_data_2018_1['CustomerID'].count()
    _tbl.loc[['2019 Only', 'Total'], '% 2018'] = np.nan
    _tbl.loc['% 2019'] = _tbl.loc['Total'] / cust_data_2019_3['CustomerID'].count()
    _tbl.loc['% 2019', ['2018 Only', 'Total', '% 2018']] = np.nan
    _tbl = _tbl.reset_index(names='2018 decile')
    decile_cols = [str(c) for c in range(1, 11)]
    count_cols = decile_cols + ['2018 Only', 'Total']
    is_pct_row = lambda d: d['2018 decile'].eq('% 2019')
    is_total = lambda d: d['2018 decile'].eq('Total')
    GT(_tbl, rowname_col='2018 decile').tab_header(title='Profit Decile Change', subtitle='2018 to 2019').tab_spanner(label='2019 decile', columns=decile_cols).fmt_number(columns=count_cols, decimals=0, use_seps=True).fmt_percent(columns=count_cols, rows=is_pct_row, decimals=1).fmt_percent(columns='% 2018', decimals=1).sub_missing(missing_text='').data_color(columns=decile_cols, rows=lambda d: ~d['2018 decile'].isin(['2019 Only', 'Total', '% 2019']), palette=['#ffffff', '#c6dbef', '#4292c6', '#08306b'], na_color='white').tab_style(style=style.text(weight='bold'), locations=loc.body(rows=is_total)).tab_options(table_font_size='11px', data_row_padding='3px')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Up-down analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For the 9,871 customers active in both years, decompose profit change into its drivers.

    For each customer, build four binary flags (define **Up = 2019 value ≥ 2018 value**):
    - `profit_up`
    - `trans_up`
    - `aspt_up` — average spend per transaction (`spend/trans`)
    - `margin_up` — (`profit/spend`)

    Concatenate into a 4-bit pattern → 16 possible groups. Aggregate: customer count, total 2018 profit, total 2019 profit, and profit change per group. Add rows for `2018 only` (all profit lost) and `2019 only` (all profit new), then a total.

    **Findings and gotchas:**
    - **One customer has zero 2019 spend → undefined margin.** Drop them (analysis then covers 9,870) or force them into the Down-Down-Down-Down group.
    - Only **14 of 16 groups** appear in this 1% sample. **Up-Down-Down-Down** and **Down-Up-Up-Up** are missing — but they are *logically possible*, not impossible: a loss-making customer who becomes less unprofitable can have profit Up while all three drivers are Down, and vice versa. In the full dataset there are 29 and 38 such customers respectively. **Don't hard-code 14 groups.**
    - **The `≥` in the Up definition matters a lot for transactions.** Of the 6,524 customers labelled Up on transactions, **3,273 had the *same* transaction count in both years** — a third of the repeat base. Profit ties are rare (4 customers); spend ties are rare (41). **Recommendation: use three levels (Up / Same / Down) for transactions**, two for the rest.
    - Largest positive contribution comes from Up-Up-Up-Up (~1,836 customers, +$221k); largest negative from Down-Down-Down-Down (~931 customers, –$170k). But the dominant swing factors overall are the 2018-only (–$1.07M) and 2019-only (+$1.62M) blocks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Lens 3 — How does a cohort evolve? (Q1/2016 cohort)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Objective:** track one acquisition cohort across its lifetime. Cohort = customers whose first-ever purchase was in Q1/2016.

    **Cohort size: 2,944 customers.** (Quarterly granularity means TCBA Figures 5.1 and 5.8, which need weekly/daily data, can't be reproduced.)

    ### 3.1 Working dataset A — quarterly cohort summary
    Filter long data to `Cohort == 'y2016 q1'`, group by `YearQuarter`: number of active cohort members, total transactions, total spend, total profit. 16 rows.

    ### 3.2 Revenue decomposition over time
    ```
    Revenue_t = cohort size × %active_t × ASPAC_t
    ASPAC_t   = AOF_t × AOV_t
    ```
    Plot each component by quarter:
    - **Cohort revenue** — massive drop in the quarter *after* acquisition, then slow decline with a mild Q4 seasonal bump each year.
    - **% active** — `active_t / cohort_size`. Same cliff.
    - **ASPAC** — `spend_t / active_t`.
    - **AOF** — `trans_t / active_t`. (In the 1% sample, AOF seasonality is much weaker than in the full dataset — a sampling artefact worth noting.)
    - **AOV** — `spend_t / trans_t`.

    The point of the decomposition: revenue decay is driven overwhelmingly by **% active** collapsing, not by spend-per-active-buyer eroding.

    ### 3.3 Annual repeat-buying patterns
    Build a customer × quarter transaction matrix for the cohort, then collapse to four annual binary flags:

    - **2016 flag** = 1 if the customer made **more than one** transaction in 2016 (i.e. at least one *repeat* purchase beyond the acquisition purchase). *This year is special — do not use `> 0`.*
    - **2017 / 2018 / 2019 flags** = 1 if any transaction in that year.

    Concatenate to a 4-bit pattern → 16 groups; report count and % of cohort per pattern, sorted descending.

    **Headline finding: 45% of the Q1/2016 cohort never made a second purchase by the end of 2019.** The "always on" pattern (Y-Y-Y-Y) is ~8%.

    Present the table with Y/N rather than 1/0 — audiences parse it faster.

    ### 3.4 Time to second purchase
    From the same customer × quarter matrix, build a cumulative "has made a second-ever purchase" indicator:

    - Quarter 1 (acquisition quarter): `1 if trans_q1 > 1 else 0`
    - Quarter t > 1: `max(indicator_{t-1}, 1 if trans_t > 0 else 0)`

    Column sums ÷ cohort size → **cumulative % of cohort having made a second purchase** by end of each quarter. First differences → **% making their second purchase *in* each quarter**.

    ### 3.5 Quarterly repeat-buying rate *(optional; not in TCBA)*
    Definition: % of customers active in period *t* who are also active in period *t+1*.

    Build a customer × quarter binary activity matrix (`trans > 0`), then:
    ```
    RBR_t = Σ (active_t × active_{t+1}) / Σ active_t
    ```
    (i.e. dot product of adjacent columns over the sum of the earlier column.)

    **Conceptual distinction:** RBR is a period-to-period measure and is blind to within-period repeat purchases. A customer who bought five times in Q1/2016 and never again shows up as a repeat buyer in §3.4 but *not* in the RBR series. Both measures are needed.

    ### 3.6 Working dataset B — value to date (VTD)
    Group the cohort's records by `CustomerID` across all 16 quarters: total transactions, total spend, total profit. **VTD = total (undiscounted) profit over 2016–2019.** 2,944 rows.

    **Findings:** VTD ranges **–$23 to $3,756**. Mean **$170**, median **$78** → **72% of cohort members are below average**. 5th pct $5.56; 10th pct $12.05; top 5% above $663.09. Just over **2% have VTD > $1,000**. Total cohort VTD ≈ **$499,821**.

    **Bins:** width $25, censor at $1,000.

    ### 3.7 VTD decile analysis
    Same construction as the **profit decile report** (§1.7b), applied to VTD: each decile = 10% of the cohort's total VTD. Decile 1 cut-off ≈ **$1,373.43** (individual VTD).

    Report per decile: % of cohort, % of transactions, % of spend, % of VTD, avg spend, avg VTD, AOF, AOV, margin.

    **Key finding:** value concentration is driven by **frequency, not basket size**. AOF for decile 1 is ~**25×** decile 10's; AOV is only ~**2×**. High-value customers are high-value because they *come back*.

    ### 3.8 Annual % active by VTD decile
    Cross the VTD decile label with the annual activity flags from §3.3 (but with 2016 set to 1 for everyone — by construction every cohort member was active in their acquisition year). Report, for each decile, the % of its members active in 2016, 2017, 2018, 2019.

    This is the follow-through on §3.7: the top deciles stay alive; the bottom deciles vanish after year one.

    ### 3.9 RFM analysis
    Computed at the end of the 4-year window, on the cohort.

    - **R (recency)** = index of the last quarter with a transaction, 1 (Q1/2016) … 16 (Q4/2019).
    - **F (frequency)** = total transactions over the four years.
    - **M (monetary value)** = **average profit per transaction** = total profit / total transactions. *(Note: this is the book's definition. Other definitions exist — state yours.)*

    Bins:
    | Dim | Bins |
    |---|---|
    | R | 1 = Q1/2016 only; 2 = Q2/2016–Q4/2017 (q2–q8); 3 = Q1/2018–Q3/2019 (q9–q15); 4 = Q4/2019 |
    | F | 1 = one purchase; 2 = 2–4; 3 = 5–10; 4 = 11+ |
    | M | 1 = ≤ $25; 2 = ($25, $50]; 3 = ($50, $75]; 4 = > $75 |

    Cross-tab: rows = R × M, columns = F.

    **Structural note:** 4×4×4 = 64 cells, but only **52 are feasible** — a customer with F = 1 made their only purchase in the acquisition quarter, so **F = 1 implies R = 1**. Twelve cells (F=1 with R ∈ {2,3,4}) are structurally empty. Don't treat them as zeros to be explained.

    Bin boundaries are judgment calls. The two that are near-mandatory: a **standalone F = 1 bin**, and **standalone recency bins for the first and last periods**.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Lens 4 — Comparing cohorts

    **Objective:** compare and contrast the performance of different acquisition cohorts, controlling for cohort size.

    ### Working dataset
    Four **cohort × quarter** matrices (17 quarterly cohorts incl. `pre 2016`, by 16 quarters):
    1. number of active customers
    2. total transactions
    3. total spend
    4. total profit

    **Cohort size** = the diagonal of matrix (1) — the acquisition quarter's active count. **Exclude the `pre 2016` row** from anything requiring cohort size.

    Then derive three more matrices:
    - **% active** = active / cohort size *(quarterly cohorts only)*
    - **AOF** = trans / active *(all cohorts, incl. pre-2016)*
    - **AOV** = spend / trans
    - **Avg margin** = profit / spend

    ### 4.1 Cohort comparison workflow (Q3/2016 vs Q4/2016)
    Cohort sizes: **Q3/2016 = 2,842**, **Q4/2016 = 6,162** — more than 2× apart, so raw comparison is meaningless.

    1. **Plot raw quarterly profit** for both cohorts. Q4 dominates simply because it's bigger.
    2. **Index each cohort's profit to its own acquisition-quarter profit** (= 100). This normalises for size — but it still tells you *nothing about why* one decays faster than the other.
    3. **Decompose.** Plot, for each cohort, on the same axes:
       - % cohort active by quarter
       - AOF by quarter
       - AOV by quarter
       - average margin by quarter

       This is where the actual insight lives. The decomposition tells you whether a cohort underperforms because fewer of them come back, because they come back less often, because they spend less per order, or because they buy lower-margin goods. Those are four completely different problems with four completely different responses.

    4. Repeat for **Q4/2016 vs Q4/2017** — a like-for-like seasonal comparison across years.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Lens 5 — Health of the customer base

    **Objective:** firm-level view. Are we growing because the base is healthy, or because we're outrunning churn with acquisition?

    ### Working datasets
    Annual cohorts: **pre-2016, 2016, 2017, 2018, 2019**. Derive each customer's `CohortYear` from their `Cohort` label (keep `pre y2016` as its own level; otherwise take the year part).

    Four **annual cohort × calendar year** matrices (5 × 4):
    1. **Number active** — count of cohort members with ≥1 transaction in that year. *(This is the awkward one: build a customer × year activity indicator first, then group by cohort year and sum.)*
    2. **Total transactions**
    3. **Total spend**
    4. **Total profit**

    Also keep a per-customer table: `CustomerID, trans_2016..trans_2019, CohortYear` — several later analyses need it.

    **Validation targets — active customers by year:** 2016 = 20,673; 2017 = 21,434; 2018 = 26,254; 2019 = 31,855.

    **Validation targets — total profit by year:** 2016 = $1,871,911; 2017 = $1,953,229; 2018 ≈ $2,290,343; 2019 ≈ $2,798,904.

    ### 5.1 Annual performance
    - Bar chart: annual revenue and profit.
    - **Stacked bar: annual profit by acquisition cohort.** This is the single most important picture in the audit.
    - Bar chart: **new customers acquired each year** (the diagonal of matrix 1).

    ### 5.2 The two percentages that matter
    For the profit-by-cohort stack, annotate two different ratios — they answer different questions.

    **(a) Share of a year's profit from that year's new customers.**
    2016: $1,193,524 / $1,871,911 = **64%** → 36% of 2016 profit came from customers acquired earlier.

    **(b) Year-on-year retention of profit from existing cohorts.**
    Profit in 2017 from all cohorts acquired *before* 2017 = $1,953,229 – $964,671 = $988,558.
    That's **53%** of what those same cohorts delivered in 2016 ($1,871,911).

    And per-cohort:
    - The 2016 cohort delivered $1,193,524 in 2016 and $451,670 in 2017 → **38%** retention of profit.
    - The pre-2016 cohort delivered $678,387 in 2016 and $536,888 in 2017 → **79%** retention.

    **The story:** new cohorts decay fast (38% in year two); old, self-selected surviving cohorts are far stickier (79%). Growth in total profit is being bought with acquisition, while the profit contributed by each existing cohort falls roughly by half annually. Repeat the same annotation for the active-customer stack.

    ### 5.3 Time to second purchase, by annual cohort
    Cumulative % of each annual cohort that has made a second-ever purchase by end of each year.

    Logic per customer × year cell:
    - 0 if the year precedes the cohort year
    - if year == cohort year: `1 if trans > 1 else 0` (repeat beyond the acquisition purchase)
    - if year > cohort year: `max(previous_flag, 1 if trans > 0 else 0)`

    Sum by cohort year, divide by cohort size. **Exclude the `pre 2016` cohort** — its size is unknown and its "acquisition year" is outside the window.

    Result is a triangular table (each cohort's series starts in its acquisition year).

    ### 5.4 Annual repeat-buying rate
    ```
    RBR(cohort, x→x+1) = # cohort members active in BOTH year x and x+1
                         ÷ # cohort members active in year x
    ```
    Build pairwise activity indicators (16/17, 17/18, 18/19) at the customer level, sum by cohort year, then divide by the corresponding column of matrix (1).

    Report per cohort **and** overall (all customers, not split by cohort).

    Rows: pre-2016, 2016, 2017, 2018, Overall. **There is no 2019 row** — you'd need 2020 data. Expect the pre-2016 cohort's RBR to be substantially higher than any new cohort's: survivorship, not superiority.

    ### 5.5 Full cohort decomposition by year
    For each annual cohort × year:

    | Table | Formula |
    |---|---|
    | **% active** | active / cohort size *(2016–2019 cohorts only; NaN for pre-2016)* |
    | **Avg annual profit per active member** | profit / active |
    | **Annual AOF** | trans / active |
    | **Annual AOV** | spend / trans |
    | **Annual avg margin** | profit / spend |

    Plot each as a line chart, one line per cohort. Add a **Total** row (all customers) to each — the totals row of the last three gives you the **overall AOF, AOV and margin by year**, which is the firm-level summary of whether the business is changing shape.

    **Note on plotting:** cells before a cohort exists must be **missing (NaN), not zero** — a zero will be plotted and will distort the line.

    ### 5.6 Quarterly version
    Same three pictures, at quarterly granularity using quarterly cohorts (reuse the Lens 4 matrices):
    1. Quarterly revenue and profit (column totals of the spend and profit matrices).
    2. Quarterly profit **stacked by quarterly cohort** — the fine-grained version of §5.1.
    3. Number of customers acquired each quarter (the diagonal).

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Appendix B — Implementation checklist

    - [ ] Load long CSV once; derive `Year`; keep as the single source of truth.
    - [ ] Write one reusable `describe_and_bin(series, width, cutoff, neg_bin=False)` helper — six of the histograms in Lens 1/3 are the same function with different arguments.
    - [ ] Write one reusable `decile_report(df, value_col, method='customer'|'value')` — Lens 1 uses it twice, Lens 3 once.
    - [ ] Write one reusable `decompose(df_grouped)` returning %cust / %trans / %spend / %profit / avg spend / avg profit / AOF / AOV / margin. Used in Lens 1, 2, 3, 4, 5.
    - [ ] Guard every ratio against zero denominators (`Spend == 0` → margin undefined; `NumTrans == 0` → ASPT undefined). Two customers in 2019, one in the Lens 2 both-group. Do not silently zero-fill.
    - [ ] Keep pre-2016 cohort in transaction/spend/profit aggregates but **out of** every cohort-size-denominated ratio.
    - [ ] Use NaN (not 0) for cohort-year cells that pre-date the cohort's existence.
    - [ ] Cross-check totals at every stage: 31,855 / 60,730 / $5.84M / $2.80M for 2019; 48,238 customers in the Lens 2 frame; 2,944 in the Q1/2016 cohort.
    """)
    return


if __name__ == "__main__":
    app.run()
