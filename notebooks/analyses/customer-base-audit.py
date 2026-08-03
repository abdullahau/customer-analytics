import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


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
    This notebook reproduces the five "lenses" of a customer-base audit, as set
    out in *The Customer-Base Audit* (Fader, Hardie and Ross) and its
    Excel-based companion. A customer-base audit is a structured review of how a
    firm's customers buy. It answers two questions: **how do customers differ
    from one another**, and **how does their behaviour change over time**.

    The data come from **Madrigal**. They are a 1% sample of the transaction
    records of 70,041 customers, aggregated to the quarter, for the 16 quarters
    from Q1 2016 to Q4 2019. Product-level analysis (TCBA Chapter 8) is out of
    scope.

    The audit is descriptive. Each lens is a way to look at the same
    transaction data. The numbers are specific to Madrigal, but the **patterns
    generalize**: they appear in almost every non-contractual customer base.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imports & Helper Functions
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.io as pio
    from great_tables import GT, loc, style
    from scipy.optimize import brentq

    return GT, brentq, go, loc, np, pd, pio, style


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data Descriptive Helpers
    """)
    return


@app.cell
def _(GT, pd, style_table):
    def customer_descriptives(df, metric):
        s = df[metric]
        mean = s.mean()
        return {
            "count": s.count(),
            "mean": mean,
            "median": s.median(),
            "std": s.std(),
            "min": s.min(),
            "max": s.max(),
            "pct_below_mean": (s < mean).mean(),
            "percentiles": s.quantile([i / 100 for i in range(5, 100, 5)]),
        }

    def stat_badges(stats, label, money=True, pct=False):
        if money:
            fmt = lambda v: f"${v:,.2f}"
        elif pct:
            fmt = lambda v: f"{v:.2f}%"
        else:
            fmt = lambda v: f"{v:,.2f}"
        t = pd.DataFrame(
            {
                "Statistic": ["Minimum", "Maximum", "Mean", "Median", "% below mean"],
                label: [
                    fmt(stats["min"]),
                    fmt(stats["max"]),
                    fmt(stats["mean"]),
                    fmt(stats["median"]),
                    f"{stats['pct_below_mean']:.1%}",
                ],
            }
        )
        return GT(t).cols_align("right", columns=label).pipe(style_table)

    def create_percentile_table(stats, column, title, subtitle=None, fmt=None):
        t = (
            stats["percentiles"]
            .reset_index()
            .rename(columns={"index": "Percentile", column: "Value"})
        )
        t["Percentile"] = (t["Percentile"] * 100).astype(int).astype(str) + "%"
        gt = GT(t).tab_header(title=title, subtitle=subtitle).pipe(style_table)
        if fmt == "currency":
            gt = gt.fmt_currency(columns="Value", decimals=2)
        elif fmt == "pct":
            gt = gt.fmt_percent(columns="Value", decimals=2)
        elif fmt == "float":
            gt = gt.fmt_number(columns="Value", decimals=2)
        return gt

    return create_percentile_table, customer_descriptives, stat_badges


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Decile Summary Table
    """)
    return


@app.cell
def _(GT, np, style_table):
    DECILE_FIELDS = [
        "Decile",
        "% Cust.",
        "% Trans.",
        "% Spend",
        "% Profit",
        "Avg Spend/Cust.",
        "Avg. Profit/Cust.",
        "AOF",
        "AOV",
        "Avg. Margin",
    ]

    def decile_labels(df, value_col="Profit", n=10):
        d = df.sort_values(value_col, ascending=False, kind="stable")
        cents = np.round(d[value_col].to_numpy() * 100).astype(np.int64)
        cum = cents.cumsum()
        total = cum[-1]
        thresholds = np.arange(1, n) * total / n
        boundaries = cents[np.searchsorted(cum, thresholds, side="right")]
        d["ProfitDecile"] = (
            n - np.searchsorted(boundaries[::-1], cents, side="left")
        ).astype("int8")
        return d, thresholds / 100, boundaries / 100

    def decile_report(df, decile_col, profit_pct_name="% Profit"):
        rep = (
            df.groupby(decile_col, as_index=False)
            .agg(
                Customers=("CustomerID", "count"),
                Transactions=("NumTrans", "sum"),
                Spend=("Spend", "sum"),
                Profit=("Profit", "sum"),
            )
            .assign(
                PctCust=lambda x: x["Customers"] / x["Customers"].sum(),
                PctTrans=lambda x: x["Transactions"] / x["Transactions"].sum(),
                PctSpend=lambda x: x["Spend"] / x["Spend"].sum(),
                PctProfit=lambda x: x["Profit"] / x["Profit"].sum(),
                AvgSpendCust=lambda x: x["Spend"] / x["Customers"],
                AvgProfitCust=lambda x: x["Profit"] / x["Customers"],
                AOF=lambda x: x["Transactions"] / x["Customers"],
                AOV=lambda x: x["Spend"] / x["Transactions"],
                AvgMargin=lambda x: x["Profit"] / x["Spend"],
            )
            .drop(columns=["Customers", "Transactions", "Spend", "Profit"])
        )
        fields = [f if f != "% Profit" else profit_pct_name for f in DECILE_FIELDS]
        rep.columns = fields
        return rep, fields

    def decile_report_gt(rep, fields, title, pct_decimals=1):
        return (
            GT(rep)
            .tab_header(title=title)
            .fmt_percent(columns=fields[1:5] + [fields[-1]], decimals=pct_decimals)
            .fmt_currency(columns=fields[5:7] + [fields[8]])
            .fmt_number(columns=fields[7])
            .pipe(style_table)
        )

    return DECILE_FIELDS, decile_labels, decile_report, decile_report_gt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Binning & Distribution
    """)
    return


@app.cell
def _(np, pd):
    def create_bins_labels(bin_width, max_cutoff, min_cutoff=None):
        if min_cutoff is None:
            min_cutoff, lower_bins, lower_labels = 0, [], []
        else:
            lower_bins, lower_labels = [-np.inf], [f"<{min_cutoff}"]
        bins = (
            lower_bins
            + list(range(min_cutoff, max_cutoff + bin_width, bin_width))
            + [np.inf]
        )
        labels = (
            lower_labels
            + [f"{i}-{i + bin_width}" for i in range(min_cutoff, max_cutoff, bin_width)]
            + [f"{max_cutoff}+"]
        )
        return {"bins": bins, "labels": labels}

    def create_distribution(df, column, bins, labels):
        dist = (
            pd.cut(df[column], bins=bins, labels=labels, right=False)
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={"count": "Customers", column: f"{column} Range"})
        )
        dist["Percent"] = dist["Customers"] / dist["Customers"].sum()
        return dist

    return create_bins_labels, create_distribution


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plotly Theme
    """)
    return


@app.cell
def _(go, pio):
    # Consultant / academic palette: navy primary, ochre secondary.
    INK, MUTED, GRID = "#1f2328", "#6b7280", "#ececec"
    ACCENT, ACCENT2 = "#1f3a5f", "#c4703a"
    CAT = ["#1f3a5f", "#c4703a", "#4c8b6f", "#6b7280", "#8a6bb0", "#b0563b", "#c9a227"]
    SEQ = ["#0d3b66", "#2b5f8f", "#4a86b8", "#7aa9d0", "#a3c7e8"]  # dark→light blue
    FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
    W, H = 820, 400

    # One font object shared by tick labels AND axis titles, so they always
    # match in family / size / colour / weight across every chart.
    _axis_font = dict(family=FONT, size=12, color=MUTED)
    # Shared axis styling; `fixedrange` bakes in "no zoom / no pan" for every figure.
    _axis = dict(
        showline=True,
        linecolor=MUTED,
        linewidth=1,
        ticks="outside",
        tickcolor=MUTED,
        ticklen=4,
        tickfont=_axis_font,
        # standoff adds breathing room between the tick labels and the axis
        # title; automargin then grows the outer margin to fit both.
        title=dict(font=_axis_font, standoff=16),
        zeroline=False,
        fixedrange=True,
        automargin=True,
    )
    _tpl = go.layout.Template()
    _tpl.layout = go.Layout(
        font=dict(family=FONT, size=13, color=INK),
        title=dict(
            font=dict(size=15, color=INK),
            # xref="paper" aligns the title with the left edge of the plotting
            # area (inset by the left margin) rather than the image edge; pad.b
            # adds breathing room below it, and the larger top margin above it.
            x=0.0,
            xanchor="left",
            xref="paper",
            pad=dict(b=8),
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=CAT,
        margin=dict(l=66, r=26, t=66, b=58),
        xaxis={**_axis, "showgrid": False},
        yaxis={
            **_axis,
            "showline": False,
            "showgrid": True,
            "gridcolor": GRID,
            "gridwidth": 1,
        },
        legend=dict(
            title=dict(font=dict(size=11)), font=dict(size=11), bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(font=dict(family=FONT, size=12), bgcolor="white"),
    )
    pio.templates["cba"] = _tpl
    pio.templates.default = "cba"

    # Hide the modebar, scroll/pinch-zoom and the plotly logo for every bare figure.
    # marimo reads a figure's render config from the default renderer (forced to
    # "browser" in-session), so setting it there locks down all charts at once.
    _LOCK = {"displayModeBar": False, "scrollZoom": False, "displaylogo": False}
    for _r in ("browser", "notebook", "notebook_connected", "plotly_mimetype"):
        if _r in pio.renderers:
            pio.renderers[_r].config = _LOCK
    return ACCENT, ACCENT2, FONT, GRID, H, INK, MUTED, SEQ, W


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Table & text style
    """)
    return


@app.cell
def _(mo):
    # Unify the notebook's text/dashboard font with the charts and tables via
    # marimo's font CSS variables.
    mo.Html(
        "<style>:root{"
        "--marimo-text-font:'Helvetica Neue',Helvetica,Arial,sans-serif;"
        "--marimo-heading-font:'Helvetica Neue',Helvetica,Arial,sans-serif;"
        "}</style>"
    )
    return


@app.cell
def _(ACCENT, FONT, INK, MUTED, loc, style):
    def style_table(gt, font_size="12px", row_padding="4px"):
        # One consultant look for every great-tables table: navy header with
        # white labels, the chart font, light row striping, hairline borders.
        return gt.tab_style(
            style=style.text(color="white", weight="bold"),
            locations=loc.column_labels(),
        ).tab_options(
            table_font_names=[s.strip() for s in FONT.split(",")],
            table_font_size=font_size,
            table_font_color=INK,
            data_row_padding=row_padding,
            column_labels_background_color=ACCENT,
            column_labels_border_bottom_color=ACCENT,
            column_labels_border_bottom_width="2px",
            heading_background_color="white",
            heading_border_bottom_color=MUTED,
            row_striping_include_table_body=True,
            row_striping_background_color="#f3f6fa",
            table_border_top_style="none",
            table_border_bottom_color=MUTED,
            table_border_bottom_width="1px",
        )

    return (style_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plotly Charts
    """)
    return


@app.cell
def _(ACCENT, ACCENT2, H, W, go):
    # ==================================================== Plotly chart helpers
    def _range_col(dist):
        col = next(c for c in dist.columns if str(c).endswith("Range"))
        return dist.rename(columns={col: "Range"}).astype({"Range": str})

    def _thin_ticks(order, max_ticks=12):
        # With 20-40 bins the axis crowds; label only ~max_ticks of them (the
        # tooltip carries every bar's exact range). Always keep the last bucket.
        n = len(order)
        if n <= max_ticks:
            return {}
        stride = -(-n // max_ticks)
        shown = list(order[::stride])
        if order[-1] not in shown:
            shown.append(order[-1])
        return {"tickmode": "array", "tickvals": shown, "ticktext": shown}

    def bar_distribution(
        dist,
        title="Customer distribution",
        x_title="Range",
        color=ACCENT,
        width=W,
        height=H,
    ):
        d = _range_col(dist)
        order = list(d["Range"])
        fig = go.Figure(
            go.Bar(
                x=d["Range"],
                y=d["Percent"],
                marker_color=color,
                marker_line_width=0,
                customdata=d[["Customers"]],
                hovertemplate="%{x}<br>Customers: %{customdata[0]:,}<br>Share: %{y:.1%}<extra></extra>",
            )
        )
        fig.update_layout(
            template="cba", title=title, width=width, height=height, bargap=0.12
        )
        fig.update_xaxes(
            title=x_title,
            tickangle=-45,
            automargin=True,
            categoryorder="array",
            categoryarray=order,
            **_thin_ticks(order),
        )
        fig.update_yaxes(title="Customers (%)", tickformat=".0%", automargin=True)
        return fig

    def overlay_bar_distribution(
        dists,
        labels,
        title="Customer distribution",
        x_title="Range",
        colors=(ACCENT, ACCENT2),
        width=W,
        height=H,
    ):
        fig = go.Figure()
        order = None
        for dist, label, col in zip(dists, labels, colors):
            d = _range_col(dist)
            if order is None:
                order = list(d["Range"])
            fig.add_bar(
                x=d["Range"],
                y=d["Percent"],
                name=str(label),
                marker_color=col,
                marker_line_width=0,
                customdata=d[["Customers"]],
                hovertemplate=f"{label} · %{{x}}<br>Customers: %{{customdata[0]:,}}<br>Share: %{{y:.1%}}<extra></extra>",
            )
        # Grouped (dodged) bars offset left/right of each range — no opacity, so
        # the look matches every other chart in the notebook.
        fig.update_layout(
            template="cba",
            title=title,
            width=width,
            height=height,
            barmode="group",
            bargap=0.2,
            bargroupgap=0.05,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0
            ),
        )
        fig.update_xaxes(
            title=x_title,
            tickangle=-45,
            automargin=True,
            categoryorder="array",
            categoryarray=order,
            **_thin_ticks(order),
        )
        fig.update_yaxes(title="Customers (%)", tickformat=".0%", automargin=True)
        return fig

    def line_chart(
        df,
        x,
        y,
        title,
        y_title,
        x_title="Quarters since acquisition",
        tickformat=None,
        x_categorical=False,
        color=ACCENT,
        width=760,
        height=320,
    ):
        fig = go.Figure(
            go.Scatter(
                x=df[x],
                y=df[y],
                mode="lines+markers",
                line=dict(width=1.8, color=color),
                marker=dict(size=6, color=color),
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
        fig.update_layout(template="cba", title=title, width=width, height=height)
        if x_categorical:
            fig.update_xaxes(title=x_title, type="category", tickangle=-45)
        else:
            fig.update_xaxes(title=x_title, dtick=1)
        fig.update_yaxes(title=y_title, tickformat=tickformat)
        return fig

    return bar_distribution, line_chart, overlay_bar_distribution


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The master dataset is `cust_data_long.csv`. It has one row for each customer
    and each quarter **in which that customer was active**. Each row records the
    number of transactions, the spend, and the profit for that customer-quarter.

    | Column | Meaning |
    |---|---|
    | `CustomerID` | customer key |
    | `Cohort` | acquisition quarter, for example `y2016_q1`; customers acquired before the window are `pre_y2016` |
    | `YearQuarter` | `y2016_q1` … `y2019_q4` |
    | `NumTrans` | transactions in that quarter |
    | `Spend` | revenue in that quarter |
    | `Profit` | contribution profit in that quarter |

    The `Year` and `Quarter` fields come from `YearQuarter`. Spend and profit are
    held as integer cents during aggregation to avoid floating-point drift, then
    converted back to dollars.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Definitions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - A **cohort** is the set of customers acquired in one period.
    - The **cohort size** is the number of customers acquired in that period. The
      size of the `pre_y2016` cohort is unknown. Exclude that cohort from every
      calculation that divides by cohort size.
    - **AOF** (average order frequency) is transactions divided by active
      customers.
    - **AOV** (average order value) is spend divided by transactions.
    - **Margin** is profit divided by spend.

    Profit factors into four terms. This identity is the backbone of the audit:

    $$
    \text{Profit} \;=\; N_c \,\times\, \text{AOF} \,\times\, \text{AOV} \,\times\, \text{Margin}
    \;=\; N_c \times \frac{\text{trans}}{\text{cust}} \times \frac{\text{spend}}{\text{trans}} \times \frac{\text{profit}}{\text{spend}}
    $$

    where $N_c$ is the number of active customers. For a cohort in a period,
    decompose number of active customers into cohort size and fraction of the cohort that is active:

    $$
    \text{Cohort profit} \;=\; (\text{cohort size}) \times (\%\,\text{cohort active}) \times \text{AOF} \times \text{AOV} \times \text{Margin}
    $$

    This structure lets you trace any change in profit to a specific cause: **fewer
    customers**, **less frequent orders**, **smaller orders**, or **thinner margins**.

    Similarly, revenue factors three terms.

    $$
    \text{Revenue} \;=\; N_c \,\times\, \text{AOF} \,\times\, \text{AOV}
    \;=\; N_c \times \frac{\text{trans}}{\text{cust}} \times \frac{\text{spend}}{\text{trans}}
    $$

    where $\text{AOF} \times \text{AOV}$ is average spend per active customer,

    $$
    \text{ASPAC} \;=\; \text{AOF} \times \text{AOV}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load Long Format Data
    """)
    return


@app.cell
def _(pd):
    cust_data = pd.read_csv("data/madrigal/cust_data_long.csv")
    cust_data = cust_data.assign(
        Spend=lambda x: (x["Spend"] * 100).round().astype("int64"),
        Profit=lambda x: (x["Profit"] * 100).round().astype("int64"),
    ).assign(
        **cust_data["YearQuarter"]
        .str.extract(r"y(\d{4})_q(\d)")
        .rename(columns={0: "Year", 1: "Quarter"})
        .astype({"Year": "int32", "Quarter": "int8"})
    )
    return (cust_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Convert Wide to Long Format Data
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
    ### Binning rules for the distributions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Most behavioural quantities are heavily right-skewed. The maximum is often 10
    to 100 times the mean. Follow four rules for every histogram:

    1. Make each bin **half-open on the left**. The \$25–50 bin holds spend in the
       interval $(25, 50]$. The first bin includes its lower edge, so a customer
       with \$0 falls in the first bin.
    2. Add a **right-censoring bin** ("greater than $x$") to hold the long tail.
    3. Set the bin width from the percentile table, not from a rule of thumb.
       Use one of 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500. A narrow width
       gives a noisy plot. A wide width hides the skew.
    4. Plot **relative frequencies**, not counts, when you compare two groups of
       different size.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 1 — How do customers differ from one another?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 1 looks at one calendar year (2019) and measures how much customers
    differ inside that year. The central result is that the **"average customer"
    does not describe anyone**. Every behavioural quantity is skewed, so the mean
    sits far above the median and most customers fall below the mean.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Keep the rows for 2019, group by `CustomerID`, and sum transactions, spend,
    and profit. Only customers with at least one 2019 transaction appear. The
    totals below are fixed reference points for the rest of Lens 1.
    """)
    return


@app.cell
def _(np):
    def annual_customer_totals(df, year):
        return (
            df.query(f"Year == {year}")
            .groupby("CustomerID", as_index=False)
            .agg(
                NumTrans=("NumTrans", "sum"),
                Spend=("Spend", "sum"),
                Profit=("Profit", "sum"),
            )
            .assign(
                Spend=lambda x: (x["Spend"] / 100).astype("float32").round(2),
                Profit=lambda x: (x["Profit"] / 100).astype("float32").round(2),
            )
        )

    def add_customer_ratios(df):
        # Add per-customer average spend per transaction and margin once, at creation.
        return df.assign(
            AvgSpendPerTrans=lambda x: x["Spend"] / x["NumTrans"],
            Margin=lambda x: np.where(
                x["Spend"] > 0, x["Profit"] / x["Spend"] * 100, np.nan
            ),
        )

    return add_customer_ratios, annual_customer_totals


@app.cell
def _(
    GT,
    add_customer_ratios,
    annual_customer_totals,
    cust_data,
    pd,
    style_table,
):
    cust_data_2019 = add_customer_ratios(annual_customer_totals(cust_data, 2019))
    cust_data_2018 = add_customer_ratios(annual_customer_totals(cust_data, 2018))

    _summary = pd.DataFrame(
        {
            "Metric": [
                "Active customers",
                "Total transactions",
                "Total spend",
                "Total profit",
                "Transactions / customer",
                "Spend / customer",
                "Profit / customer",
            ],
            "Value": [
                len(cust_data_2019),
                cust_data_2019["NumTrans"].sum(),
                cust_data_2019["Spend"].sum(),
                cust_data_2019["Profit"].sum(),
                cust_data_2019["NumTrans"].mean(),
                cust_data_2019["Spend"].mean(),
                cust_data_2019["Profit"].mean(),
            ],
        }
    )
    (
        GT(_summary)
        .tab_header(title="2019 annual customer summary")
        .fmt_number(columns="Value", rows=[0, 1], decimals=0)
        .fmt_currency(columns="Value", rows=[2, 3], decimals=0)
        .fmt_number(columns="Value", rows=[4], decimals=2)
        .fmt_currency(columns="Value", rows=[5, 6], decimals=2)
        .pipe(style_table)
    )
    return cust_data_2018, cust_data_2019


@app.cell
def _(cust_data_2019, customer_descriptives):
    spend_stats = customer_descriptives(cust_data_2019, "Spend")
    profit_stats = customer_descriptives(cust_data_2019, "Profit")
    trans_stats = customer_descriptives(cust_data_2019, "NumTrans")
    avg_spend_stats = customer_descriptives(cust_data_2019, "AvgSpendPerTrans")
    avg_margin_stats = customer_descriptives(
        cust_data_2019.query("Spend > 0"), "Margin"
    )
    return (
        avg_margin_stats,
        avg_spend_stats,
        profit_stats,
        spend_stats,
        trans_stats,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Distribution of spend
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The spend distribution is strongly right-skewed. The maximum (\$6,695) is
    about 37 times the mean (\$183), and the mean is well above the median
    (\$113). As a result, **69% of customers spend below the average**. The
    bottom 5% spend \$22 or less; the top 5% each spend more than \$579.

    The mean is therefore a poor summary of a typical customer. Read the median
    and the percentiles instead. The percentile table also sets the bin width: a
    width of \$25 with censoring at \$1,000 gives 41 bins and shows the skew
    without noise.

    Two customers have exactly \$0 spend in 2019. They fall in the first bin.
    """)
    return


@app.cell
def _(spend_stats, stat_badges):
    stat_badges(spend_stats, "Spend")
    return


@app.cell
def _(create_percentile_table, spend_stats):
    create_percentile_table(
        spend_stats,
        "Spend",
        "Customer spend percentiles",
        "2019 annual spend",
        fmt="currency",
    )
    return


@app.cell
def _(
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(cust_data_2019, "Spend", **create_bins_labels(25, 1000)),
        title="Customer spend distribution (2019)",
        x_title="Annual spend ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Distribution of profit
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Profit has the same right-skewed shape as spend. The values run from −\$652
    to \$3,347. The mean (\$88) is above the median (\$54), and again **69% of
    customers fall below the mean**. Profit runs at roughly 45–50% of the
    corresponding spend figures, so the plot uses a lower censoring point
    (\$500). A separate `< 0` bin holds the loss-making customers.
    """)
    return


@app.cell
def _(profit_stats, stat_badges):
    stat_badges(profit_stats, "Profit")
    return


@app.cell
def _(
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(cust_data_2019, "Profit", **create_bins_labels(25, 500, 0)),
        title="Customer profit distribution (2019)",
        x_title="Annual profit ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Distribution of the number of transactions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The transaction count is a reverse-J distribution. The maximum is 58, but
    **63% of customers made exactly one purchase** (20,149 of 31,855). The mean of
    1.9 therefore describes almost no one.

    Keep every non-terminal bin at width 1 and censor at `10+`. Do not merge bins
    into unequal groups (for example 1 / 2–4 / 5–9) in a histogram. If you need
    unequal groups, use a table.
    """)
    return


@app.cell
def _(stat_badges, trans_stats):
    stat_badges(trans_stats, "Transactions", money=False)
    return


@app.cell
def _(bar_distribution, create_distribution, cust_data_2019, np):
    _bins = list(range(1, 11)) + [np.inf]
    _labels = [str(i) for i in range(1, 10)] + ["10+"]
    bar_distribution(
        create_distribution(cust_data_2019, "NumTrans", bins=_bins, labels=_labels),
        title="Customer transactions distribution (2019)",
        x_title="Annual transactions",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Distribution of average spend per transaction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For each customer, average spend per transaction is $\text{spend}/\text{trans}$.
    Bin at width \$25 and censor at \$500.

    #### Two different "average transaction" numbers

    Two quantities are both called "average spend per transaction". They are not
    equal, and both appear in practice.

    - **Ratio of totals (AOV).** Divide total spend by total transactions. For
      2019 this is about \$96.
    - **Mean of per-customer averages.** Average each customer's own spend per
      transaction, then take the mean across customers. For 2019 this is about
      \$99.

    Start from the ratio of the two per-customer means. The count $I$ cancels,
    which leaves total spend over total transactions:

    $$
    \frac{\frac{1}{I}\sum_{i=1}^{I}\text{spend}_i}{\frac{1}{I}\sum_{i=1}^{I}\text{trans}_i}
    = \frac{\sum_{i=1}^{I}\text{spend}_i}{\sum_{i=1}^{I}\text{trans}_i}
    = \sum_{i=1}^{I}\left(\frac{\text{trans}_i}{\sum_{j}\text{trans}_j}\right)\frac{\text{spend}_i}{\text{trans}_i}
    $$

    The last form shows that **AOV is a transaction-weighted average** of the
    per-customer values. Each customer's weight is that customer's share of total
    transactions, so frequent buyers dominate it.

    The mean of per-customer averages gives every customer equal weight:

    $$
    \frac{1}{I}\sum_{i=1}^{I}\frac{\text{spend}_i}{\text{trans}_i}
    $$

    The one-and-done buyers (63% of the base) count as much as the customer with
    58 transactions.

    The two numbers are equal **only** when every customer makes the same number
    of transactions. That never happens in a real customer base, so the two always
    differ. The direction of the gap carries information. Here \$96 is below \$99,
    which means heavier buyers have **smaller** average baskets than light buyers.

    Use one name for each quantity and keep it fixed. "AOV" always means the
    transaction-weighted ratio of totals.
    """)
    return


@app.cell
def _(avg_spend_stats, stat_badges):
    stat_badges(avg_spend_stats, "Avg spend / transaction")
    return


@app.cell
def _(
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019, "AvgSpendPerTrans", **create_bins_labels(25, 500)
        ),
        title="Average spend per transaction (2019)",
        x_title="Average spend per transaction ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Average spend per transaction, by transaction level
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Both the number of transactions and the average spend per transaction vary
    across customers. The natural next question is whether the two are related.
    Group customers by transaction count (1, 2, …, 9, `10+`) and report the spread
    of average spend inside each group. The result confirms the finding above:
    average basket size does not rise with purchase frequency.
    """)
    return


@app.cell
def _(GT, cust_data_2019, np, pd, style_table):
    _bins = list(range(1, 11)) + [np.inf]
    _labels = [str(i) for i in range(1, 10)] + ["10+"]
    _binned = cust_data_2019.assign(
        TransBin=lambda d: pd.cut(
            d["NumTrans"], bins=_bins, labels=_labels, right=False
        )
    )
    aspt_by_level = _binned.groupby("TransBin", as_index=False, observed=True).agg(
        Mean=("AvgSpendPerTrans", "mean"),
        Std=("AvgSpendPerTrans", "std"),
        Min=("AvgSpendPerTrans", "min"),
        P05=("AvgSpendPerTrans", lambda s: s.quantile(0.05)),
        Median=("AvgSpendPerTrans", "median"),
        P95=("AvgSpendPerTrans", lambda s: s.quantile(0.95)),
        Max=("AvgSpendPerTrans", "max"),
    )
    (
        GT(aspt_by_level.rename(columns={"TransBin": "Transactions"}))
        .tab_header(title="Average spend per transaction, by transaction level")
        .fmt_currency(columns=list(aspt_by_level.columns[1:]), decimals=2)
        .pipe(style_table)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Distribution of average margin
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For each customer, margin is $\text{profit}/\text{spend}$. It is defined only
    where spend is greater than 0, so exclude the two zero-spend customers rather
    than fill them with 0. This is the **overall** margin across all of a
    customer's 2019 purchases, not the average of transaction-level margins;
    transaction-level margins cannot be recovered from quarter-level data.

    Unlike the other four quantities, margin is **left-skewed**. Bin at width 5%
    and add a `< 0%` bin for loss-makers.
    """)
    return


@app.cell
def _(avg_margin_stats, stat_badges):
    stat_badges(avg_margin_stats, "Margin", money=False, pct=True)
    return


@app.cell
def _(
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019.query("Spend > 0"), "Margin", **create_bins_labels(5, 100, 0)
        ),
        title="Average margin distribution (2019)",
        x_title="Margin (%)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Decile analyses
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A decile report splits the customer base into ten groups and applies the
    profit identity to each group. It shows how concentrated value is, and which
    of the four factors drives that concentration. Two versions exist, and they
    answer different questions.

    **Customer decile** — each decile holds 10% of *customers*, ranked by profit.
    This shows how much of total profit the top-ranked tenth of customers
    produces.

    **Profit decile** — each decile holds 10% of *profit*. The top decile
    contains the few customers who together make the first 10% of profit, so it
    holds far fewer than 10% of customers. This version shows the size of the most
    valuable group.

    Read the report by column: `% Cust.` against `% Profit` measures
    concentration; `AOF`, `AOV` and `Avg. Margin` show which factor separates the
    top deciles from the bottom.
    """)
    return


@app.cell
def _(DECILE_FIELDS, cust_data_2019, decile_report, decile_report_gt, pd):
    _ranked = cust_data_2019.assign(
        CustDecile=lambda d: (
            pd.qcut(
                d["Profit"].rank(method="first", ascending=False), q=10, labels=False
            )
            + 1
        )
    )
    cust_decile_rep, _f = decile_report(_ranked, "CustDecile")
    decile_report_gt(cust_decile_rep, DECILE_FIELDS, "Customer decile report")
    return


@app.cell
def _(
    DECILE_FIELDS,
    cust_data_2019,
    decile_labels,
    decile_report,
    decile_report_gt,
):
    _labelled = decile_labels(cust_data_2019, "Profit")[0]
    profit_decile_rep, _f = decile_report(_labelled, "ProfitDecile")
    decile_report_gt(
        profit_decile_rep, DECILE_FIELDS, "Profit decile report", pct_decimals=2
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two points need care in the profit decile report:

    1. **Cumulative profit is not monotonic.** It rises to about \$2,802,772, then
       falls back to the total of \$2,798,904, because 263 customers are
       loss-making. Every loss-maker lands in decile 10. The decile-1 cut-off is
       about \$546 of individual profit; the decile-2 cut-off is about \$345.
    2. **A revenue version is a useful fallback.** If you do not have cost data,
       run the same decile report on spend. A variant that pulls the loss-makers
       into a separate 11th group is also worth building.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 2 — What changed between two periods?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 2 compares 2018 with 2019 and traces the change in firm performance to
    changes in customer behaviour. The working dataset has one row for each
    customer active in **either** year (an outer join of the two annual
    aggregates, with zeros filled in). It covers 48,238 customers. A `Status`
    field marks each customer as active in both years, in 2018 only (lapsed), or
    in 2019 only (new or reactivated).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Venn diagram
    """)
    return


@app.cell
def _(ACCENT, ACCENT2, brentq, go, np):
    def venn_two(n_a, n_b, n_both, label_a, label_b, title, width=560, height=460):
        R = 1.0
        r = np.sqrt(n_b / n_a)
        a_target = np.pi * (n_both / n_a)

        def lens_area(d):
            if d >= R + r:
                return 0.0
            if d <= abs(R - r):
                return np.pi * min(R, r) ** 2
            p1 = R**2 * np.arccos(np.clip((d**2 + R**2 - r**2) / (2 * d * R), -1, 1))
            p2 = r**2 * np.arccos(np.clip((d**2 + r**2 - R**2) / (2 * d * r), -1, 1))
            p3 = 0.5 * np.sqrt(
                max((-d + r + R) * (d - r + R) * (d + r - R) * (d + r + R), 0.0)
            )
            return p1 + p2 - p3

        d = brentq(lambda x: lens_area(x) - a_target, abs(R - r) + 1e-9, R + r - 1e-9)
        cy = max(R, r)
        cx1, cx2 = R, R + d
        xlens = R + (d**2 + R**2 - r**2) / (2 * d)
        fig = go.Figure()
        fig.add_shape(
            type="circle",
            x0=cx1 - R,
            y0=cy - R,
            x1=cx1 + R,
            y1=cy + R,
            line_color=ACCENT,
            fillcolor=ACCENT,
            layer="below",
        )
        fig.add_shape(
            type="circle",
            x0=cx2 - r,
            y0=cy - r,
            x1=cx2 + r,
            y1=cy + r,
            line_color=ACCENT2,
            fillcolor=ACCENT2,
            layer="below",
        )

        _th = np.linspace(0, 2 * np.pi, 361)
        _c1 = np.column_stack([cx1 + R * np.cos(_th), cy + R * np.sin(_th)])
        _c1 = _c1[(_c1[:, 0] - cx2) ** 2 + (_c1[:, 1] - cy) ** 2 <= r**2]
        _c2 = np.column_stack([cx2 + r * np.cos(_th), cy + r * np.sin(_th)])
        _c2 = _c2[(_c2[:, 0] - cx1) ** 2 + (_c2[:, 1] - cy) ** 2 <= R**2]
        _lens = np.vstack([_c1, _c2])
        _ctr = _lens.mean(axis=0)
        _lens = _lens[
            np.argsort(np.arctan2(_lens[:, 1] - _ctr[1], _lens[:, 0] - _ctr[0]))
        ]
        _rgb = tuple(int(ACCENT[k : k + 2], 16) for k in (1, 3, 5))
        fig.add_scatter(
            x=_lens[:, 0],
            y=_lens[:, 1],
            fill="toself",
            mode="lines",
            line=dict(width=0),
            fillcolor=f"rgba{(*_rgb, 0.55)}",
            hoverinfo="skip",
            showlegend=False,
        )
        for x, txt in [
            (cx1 - 0.45 * R, f"{label_a}<br>{n_a - n_both:,}"),
            (xlens, f"Both<br>{n_both:,}"),
            (cx2 + 0.45 * r, f"{label_b}<br>{n_b - n_both:,}"),
        ]:
            fig.add_annotation(
                x=x,
                y=cy,
                text=txt,
                showarrow=False,
                font=dict(size=13, color="white"),
                align="center",
            )
        fig.update_layout(
            template="cba",
            title=title,
            width=width,
            height=height,
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=54, b=10),
        )
        fig.update_xaxes(visible=False, range=[-0.25, R + d + r + 0.25])
        fig.update_yaxes(
            visible=False,
            range=[cy - r - 0.25, cy + r + 0.25],
            scaleanchor="x",
            scaleratio=1,
        )
        return fig

    return (venn_two,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Profit bridge (waterfall)
    """)
    return


@app.cell
def _(ACCENT, ACCENT2, INK, MUTED, go):
    def profit_bridge_chart(pbg, width=760, height=460, scale=1_000):
        both18 = pbg.loc["Active Both Years", "Y2018"] / scale
        both19 = pbg.loc["Active Both Years", "Y2019"] / scale
        only18 = pbg.loc["2018 Only (Lapsed)", "Y2018"] / scale
        only19 = pbg.loc["2019 Only (New/Reactivated)", "Y2019"] / scale
        tot18 = pbg.loc["Total", "Y2018"] / scale
        tot19 = pbg.loc["Total", "Y2019"] / scale
        delta = both19 - both18
        lo = min(both18, both19)
        money = lambda v: f"${v:,.0f}K"
        fig = go.Figure()
        # Solid consultant fills (no borders, no opacity): slate for the
        # carried-over base, navy for the 2018 flow, ochre for the 2019 flow.
        # All three are dark enough for white in-bar labels.
        _both = dict(marker_color="#64748b")
        _b18 = dict(marker_color=ACCENT, marker_line=dict(color="white", width=1))
        _b19 = dict(marker_color=ACCENT2, marker_line=dict(color="white", width=1))
        w = 0.62
        fig.add_bar(x=[0], y=[both18], base=0, width=w, showlegend=False, **_both)
        fig.add_bar(x=[0], y=[only18], base=both18, width=w, showlegend=False, **_b18)
        fig.add_bar(x=[1], y=[only18], base=both18, width=w, showlegend=False, **_b18)
        fig.add_bar(x=[2], y=[abs(delta)], base=lo, width=w, showlegend=False, **_both)
        fig.add_bar(x=[3], y=[only19], base=both19, width=w, showlegend=False, **_b19)
        fig.add_bar(x=[4], y=[both19], base=0, width=w, showlegend=False, **_both)
        fig.add_bar(x=[4], y=[only19], base=both19, width=w, showlegend=False, **_b19)

        def hline(x0, x1, y):
            fig.add_shape(
                type="line",
                x0=x0,
                x1=x1,
                y0=y,
                y1=y,
                line=dict(color=MUTED, width=1, dash="dot"),
            )

        hline(0 + w / 2, 1 - w / 2, tot18)
        hline(3 + w / 2, 4 - w / 2, tot19)
        hline(0 + w / 2, 2 - w / 2, both18)
        hline(2 + w / 2, 4 - w / 2, both19)

        def ann(x, y, t, yshift=0, yanchor="middle", color="white"):
            fig.add_annotation(
                x=x,
                y=y,
                text=t,
                showarrow=False,
                yshift=yshift,
                yanchor=yanchor,
                font=dict(size=12, color=color),
            )

        # In-bar labels are white; the three that float over the white canvas
        # (the two year totals and the delta) stay dark so they stay readable.
        ann(0, tot18, money(tot18), yshift=10, yanchor="bottom", color=INK)
        ann(4, tot19, money(tot19), yshift=10, yanchor="bottom", color=INK)
        ann(0, both18 / 2, "Both<br>years")
        ann(0, both18 + only18 / 2, "2018<br>only")
        ann(4, both19 / 2, "Both<br>years")
        ann(4, both19 + only19 / 2, "2019<br>only")
        ann(1, both18 + only18 / 2, money(only18))
        ann(2, lo, f"−{money(abs(delta))}", yshift=-8, yanchor="top", color=INK)
        ann(3, both19 + only19 / 2, money(only19))
        fig.update_layout(
            template="cba",
            title="Decomposition of annual customer profit",
            width=width,
            height=height,
            barmode="overlay",
            bargap=0.35,
        )
        fig.update_xaxes(
            tickvals=[0, 4],
            ticktext=["2018", "2019"],
            range=[-0.7, 4.7],
            showline=True,
            linecolor=MUTED,
        )
        fig.update_yaxes(visible=False, range=[0, tot19 * 1.14])
        return fig

    return (profit_bridge_chart,)


@app.cell
def _(cust_data_2018, cust_data_2019):
    cust_2018_2019 = (
        cust_data_2018.merge(
            cust_data_2019,
            on="CustomerID",
            how="outer",
            suffixes=("_2018", "_2019"),
            indicator=True,
        )
        .assign(
            Status=lambda df: df["_merge"].map(
                {
                    "both": "Active Both Years",
                    "left_only": "2018 Only (Lapsed)",
                    "right_only": "2019 Only (New/Reactivated)",
                }
            )
        )
        .drop(columns="_merge")
    )
    return (cust_2018_2019,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Headline
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Spend and profit both grew, and the active count grew with them. The question
    for the rest of Lens 2 is whether that growth came from existing customers
    buying more, or from acquisition outrunning churn.
    """)
    return


@app.cell
def _(GT, cust_2018_2019, cust_data_2018, cust_data_2019, pd, style_table):
    _yoy = pd.concat(
        [
            (
                cust_2018_2019.filter(like="_2018")
                .sum(numeric_only=True)
                .rename(lambda c: c.removesuffix("_2018"))
                .rename("2018")
            ),
            (
                cust_2018_2019.filter(like="_2019")
                .sum(numeric_only=True)
                .rename(lambda c: c.removesuffix("_2019"))
                .rename("2019")
            ),
        ],
        axis=1,
    )
    _yoy["Δ"] = (_yoy["2019"] - _yoy["2018"]) / _yoy["2018"]
    _a18 = cust_data_2018["CustomerID"].nunique()
    _a19 = cust_data_2019["CustomerID"].nunique()
    _yoy.loc["Active customers"] = [_a18, _a19, (_a19 - _a18) / _a18]
    _yoy = _yoy.drop(index="NumTrans").reset_index(names="")
    (
        GT(_yoy)
        .tab_header(
            title="Spend, profit and active-customer summary", subtitle="2018 to 2019"
        )
        .fmt_percent(columns=["Δ"], decimals=1)
        .fmt_currency(columns=["2018", "2019"], decimals=0)
        .fmt_number(columns=["2018", "2019"], rows=[2], decimals=0)
        .pipe(style_table)
    )
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
    Re-draw each Lens 1 distribution for 2018 and 2019 on the same axes, with the
    same bin edges and relative frequencies. The two years overlap almost exactly.
    The **shape** of customer heterogeneity is stable across years; what moved is
    the **number** of customers, not how a typical customer behaves. This is a
    general property of a healthy base: the distribution is a structural feature,
    not a yearly event.
    """)
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    overlay_bar_distribution,
):
    overlay_bar_distribution(
        [
            create_distribution(
                cust_data_2018, "Spend", **create_bins_labels(25, 1000)
            ),
            create_distribution(
                cust_data_2019, "Spend", **create_bins_labels(25, 1000)
            ),
        ],
        labels=("2018", "2019"),
        title="Customer spend, 2018 vs 2019",
        x_title="Annual spend ($)",
    )
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    overlay_bar_distribution,
):
    overlay_bar_distribution(
        [
            create_distribution(
                cust_data_2018, "Profit", **create_bins_labels(25, 500, 0)
            ),
            create_distribution(
                cust_data_2019, "Profit", **create_bins_labels(25, 500, 0)
            ),
        ],
        labels=("2018", "2019"),
        title="Customer profit, 2018 vs 2019",
        x_title="Annual profit ($)",
    )
    return


@app.cell
def _(
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    np,
    overlay_bar_distribution,
):
    _bins = list(range(1, 11)) + [np.inf]
    _labels = [str(i) for i in range(1, 10)] + ["10+"]
    overlay_bar_distribution(
        [
            create_distribution(cust_data_2018, "NumTrans", bins=_bins, labels=_labels),
            create_distribution(cust_data_2019, "NumTrans", bins=_bins, labels=_labels),
        ],
        labels=("2018", "2019"),
        title="Transactions, 2018 vs 2019",
        x_title="Annual transactions",
    )
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    overlay_bar_distribution,
):
    overlay_bar_distribution(
        [
            create_distribution(
                cust_data_2018, "AvgSpendPerTrans", **create_bins_labels(25, 500)
            ),
            create_distribution(
                cust_data_2019, "AvgSpendPerTrans", **create_bins_labels(25, 500)
            ),
        ],
        labels=("2018", "2019"),
        title="Average spend per transaction, 2018 vs 2019",
        x_title="Average spend per transaction ($)",
    )
    return


@app.cell
def _(
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    overlay_bar_distribution,
):
    overlay_bar_distribution(
        [
            create_distribution(
                cust_data_2018.query("Spend > 0"),
                "Margin",
                **create_bins_labels(5, 100, 0),
            ),
            create_distribution(
                cust_data_2019.query("Spend > 0"),
                "Margin",
                **create_bins_labels(5, 100, 0),
            ),
        ],
        labels=("2018", "2019"),
        title="Average margin, 2018 vs 2019",
        x_title="Margin (%)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Customer overlap
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Split the two years into three groups: active in both years, 2018 only, and
    2019 only. Of the 26,254 customers active in 2018, only 9,871 returned in
    2019. Repeat buyers are 38% of the 2018 base and 31% of the 2019 base. The
    area-proportional Venn diagram below shows the three groups to scale;
    Appendix A gives the geometry.
    """)
    return


@app.cell
def _(GT, cust_2018_2019, style_table):
    overlap = cust_2018_2019.groupby("Status").agg(Customers=("CustomerID", "count"))
    overlap.loc["Active 2018"] = (
        overlap.loc["2018 Only (Lapsed)"] + overlap.loc["Active Both Years"]
    )
    overlap.loc["Active 2019"] = (
        overlap.loc["2019 Only (New/Reactivated)"] + overlap.loc["Active Both Years"]
    )
    (
        GT(overlap.reset_index(names="Group"))
        .tab_header(title="Customer overlap")
        .fmt_number(columns="Customers", decimals=0)
        .pipe(style_table)
    )
    return (overlap,)


@app.cell
def _(overlap, venn_two):
    venn_two(
        int(overlap.loc["Active 2018", "Customers"]),
        int(overlap.loc["Active 2019", "Customers"]),
        int(overlap.loc["Active Both Years", "Customers"]),
        "2018 only",
        "2019 only",
        "Active customers: 2018 vs 2019 (area-proportional)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Profit by activity group and the profit bridge
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Split profit by the three activity groups. The both-years group made 53% of
    2018 profit but only 42% of 2019 profit, and its profit **fell** by about
    \$33,000. All of the growth came from acquisition: the 2019-only group added
    about \$1.6 million, while the 2018-only group took about \$1.1 million with
    it when it lapsed.

    The bridge chart below reads left to right. It starts at 2018 total profit,
    removes the profit of the lapsed group, applies the small change in the
    both-years group, adds the profit of the new group, and arrives at 2019 total
    profit. The picture makes the source of growth explicit: **the firm grows by
    replacing lost customers with new ones, not by growing the retained base.**
    """)
    return


@app.cell
def _(GT, cust_2018_2019, style_table):
    profit_by_group = cust_2018_2019.groupby("Status").agg(
        Y2018=("Profit_2018", lambda s: s.sum(min_count=1)),
        Y2019=("Profit_2019", lambda s: s.sum(min_count=1)),
    )
    profit_by_group.loc["Total"] = profit_by_group.sum(min_count=1)
    (
        GT(profit_by_group.reset_index(names="Group"))
        .tab_header(title="Profit by activity group")
        .fmt_currency(columns=["Y2018", "Y2019"], decimals=0)
        .cols_label(Y2018="2018 profit", Y2019="2019 profit")
        .pipe(style_table)
    )
    return (profit_by_group,)


@app.cell
def _(profit_bridge_chart, profit_by_group):
    profit_bridge_chart(profit_by_group)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Performance decomposition by group
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Apply the profit identity to each group in each year. This shows **why** the
    retained group is over-represented in profit relative to its headcount: it
    buys more often (higher AOF) and spends more per order (higher AOV) than the
    one-year-only groups. The table reports active customers, transactions, spend,
    profit, and the derived AOF, AOV, and margin.
    """)
    return


@app.cell
def _(GT, cust_2018_2019, style_table):
    _flows = cust_2018_2019.melt(
        id_vars=["CustomerID", "Status"],
        value_vars=[
            "NumTrans_2018",
            "NumTrans_2019",
            "Spend_2018",
            "Spend_2019",
            "Profit_2018",
            "Profit_2019",
        ],
        var_name="MetricYear",
        value_name="Value",
    ).assign(
        Metric=lambda d: d["MetricYear"].str.rsplit("_", n=1).str[0],
        Year=lambda d: d["MetricYear"].str.rsplit("_", n=1).str[-1],
    )
    _g = (
        _flows.groupby(["Status", "Metric", "Year"])["Value"]
        .sum(min_count=1)
        .unstack("Metric")
    )
    _g["NumCust"] = (
        _flows.assign(active=lambda d: d["Value"].notna())
        .query("Metric == 'NumTrans'")
        .groupby(["Status", "Year"])["active"]
        .sum()
        .where(lambda s: s > 0)
    )
    _g["AOF"] = _g["NumTrans"] / _g["NumCust"]
    _g["AOV"] = _g["Spend"] / _g["NumTrans"]
    _g["Margin"] = _g["Profit"] / _g["Spend"]
    _crosstab = (
        _g.stack()
        .rename("Value")
        .unstack("Year")
        .reset_index()
        .rename(columns={"level_1": "Metric"})
    )
    (
        GT(_crosstab, groupname_col="Status", rowname_col="Metric")
        .tab_header(
            title="Performance summary and decomposition", subtitle="by group and year"
        )
        .fmt_number(columns=["2018", "2019"], decimals=2)
        .fmt_number(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].isin(["NumCust", "NumTrans"]),
            decimals=0,
        )
        .fmt_currency(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].isin(["Spend", "Profit"]),
            decimals=0,
        )
        .fmt_percent(
            columns=["2018", "2019"],
            rows=lambda d: d["Metric"].eq("Margin"),
            decimals=1,
        )
        .sub_missing(missing_text="")
        .pipe(style_table)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Decile change analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Do high-value customers stay high-value? Compute profit-decile cut-offs
    separately for 2018 and 2019. In this base they are close, so use one common
    set of cut-offs for both years (the average of the two, rounded to the nearest
    \$5). Assign each customer a 2018 decile and a 2019 decile, then cross-tabulate
    the both-years group. Append a `2018 Only` column and a `2019 Only` row for the
    customers present in one year only.

    The mass sits on and just below the diagonal, so most customers hold their
    rank. The large `2018 Only` column is concentrated in the low deciles: churn
    is heaviest among low-value customers, but decile 1 is not immune. A common set
    of cut-offs makes the matrix readable but means each decile no longer holds
    exactly 10% of a year's profit; year-specific cut-offs keep that property at
    the cost of readability.
    """)
    return


@app.cell
def _(
    GT,
    cust_2018_2019,
    cust_data_2018,
    cust_data_2019,
    decile_labels,
    loc,
    np,
    pd,
    style,
    style_table,
):
    _, _t18, _b18 = decile_labels(cust_data_2018, "Profit", n=10)
    _, _t19, _b19 = decile_labels(cust_data_2019, "Profit", n=10)
    _avg_bnd = np.round((_b19 + _b18) / 2 / 5) * 5

    def _decile(s):
        v = s.to_numpy()
        out = 10 - np.searchsorted(_avg_bnd[::-1], v, side="left")
        return np.where(np.isnan(v), np.nan, out)

    _dc = cust_2018_2019.assign(
        Row=lambda d: _decile(d["Profit_2018"]), Col=lambda d: _decile(d["Profit_2019"])
    ).fillna({"Row": "2019 Only", "Col": "2018 Only"})
    _or = [*range(1, 11), "2019 Only"]
    _oc = [*range(1, 11), "2018 Only"]
    _tbl = pd.crosstab(
        _dc["Row"], _dc["Col"], margins=True, margins_name="Total"
    ).reindex(index=[*_or, "Total"], columns=[*_oc, "Total"], fill_value=0)
    _tbl.columns = [str(c) for c in _tbl.columns]
    _tbl.index = [str(i) for i in _tbl.index]
    _tbl["% 2018"] = _tbl["Total"] / cust_data_2018["CustomerID"].count()
    _tbl.loc[["2019 Only", "Total"], "% 2018"] = np.nan
    _tbl.loc["% 2019"] = _tbl.loc["Total"] / cust_data_2019["CustomerID"].count()
    _tbl.loc["% 2019", ["2018 Only", "Total", "% 2018"]] = np.nan
    _tbl = _tbl.reset_index(names="2018 decile")

    _dcols = [str(c) for c in range(1, 11)]
    _ccols = _dcols + ["2018 Only", "Total"]
    _is_pct = lambda d: d["2018 decile"].eq("% 2019")
    _is_total = lambda d: d["2018 decile"].eq("Total")
    (
        GT(_tbl, rowname_col="2018 decile")
        .tab_header(title="Profit decile change", subtitle="2018 to 2019")
        .tab_spanner(label="2019 decile", columns=_dcols)
        .fmt_number(columns=_ccols, decimals=0, use_seps=True)
        .fmt_percent(columns=_ccols, rows=_is_pct, decimals=1)
        .fmt_percent(columns="% 2018", decimals=1)
        .sub_missing(missing_text="")
        .data_color(
            columns=_dcols,
            rows=lambda d: ~d["2018 decile"].isin(["2019 Only", "Total", "% 2019"]),
            palette=["#ffffff", "#c6dbef", "#4292c6", "#08306b"],
            na_color="white",
        )
        .tab_style(style=style.text(weight="bold"), locations=loc.body(rows=_is_total))
        .tab_style(
            style=style.text(weight="bold"), locations=loc.body(columns=["Total"])
        )
        .pipe(style_table, font_size="11px", row_padding="3px")
    )
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
    For the 9,871 customers active in both years, mark each of four quantities as
    up or down from 2018 to 2019: profit, transactions, average spend per
    transaction, and margin. The four flags give up to 16 groups. Add rows for the
    lapsed and new customers, whose entire profit is lost or new.

    Read this as a diagnosis of the both-years block. The largest positive group is
    up-up-up-up; the largest negative group is down-down-down-down. But both are
    small next to the two one-year blocks: the 2018-only block removes about
    \$1.1M and the 2019-only block adds about \$1.6M. **Acquisition and churn, not
    the movement of retained customers, dominate the change in profit.**

    Three points guide the build:

    - **Handle undefined margin.** One customer has zero 2019 spend, so margin is
      undefined. Drop that customer (the count becomes 9,870).
    - **Do not hard-code the number of groups.** This 1% sample shows 14 of the 16
      logically possible groups, but the two missing groups are possible, not
      impossible; the full dataset contains them.
    - **Use three states for transactions.** With a "≥" rule, 3,273 of the 6,524
      customers marked "up" on transactions in fact had the **same** count in both
      years. Split transactions into up / same / down, and keep two states for the
      other three quantities. (Ties are rare for profit and spend.)
    """)
    return


@app.cell
def _(GT, cust_2018_2019, np, pd, style_table):
    _both = (
        cust_2018_2019.query("Status == 'Active Both Years'")
        .query("Spend_2018 > 0 and Spend_2019 > 0")
        .assign(
            profit_up=lambda d: d["Profit_2019"] >= d["Profit_2018"],
            trans_state=lambda d: np.sign(
                d["NumTrans_2019"] - d["NumTrans_2018"]
            ).astype("int8"),
            aspt_up=lambda d: (
                d["Spend_2019"] / d["NumTrans_2019"]
                >= d["Spend_2018"] / d["NumTrans_2018"]
            ),
            margin_up=lambda d: (
                d["Profit_2019"] / d["Spend_2019"] >= d["Profit_2018"] / d["Spend_2018"]
            ),
        )
    )
    _flags = ["profit_up", "trans_state", "aspt_up", "margin_up"]
    _grp = (
        _both.groupby(_flags, as_index=False)
        .agg(
            NumCust=("CustomerID", "count"),
            P2018=("Profit_2018", "sum"),
            P2019=("Profit_2019", "sum"),
        )
        .sort_values(_flags, ascending=False)
        .assign(Change=lambda d: d["P2019"] - d["P2018"])
    )
    _bmap = {True: "Up", False: "Down"}
    _tmap = {1: "Up", 0: "Same", -1: "Down"}
    _lbl = _grp[_flags].assign(
        profit_up=lambda d: d["profit_up"].map(_bmap),
        trans_state=lambda d: d["trans_state"].map(_tmap),
        aspt_up=lambda d: d["aspt_up"].map(_bmap),
        margin_up=lambda d: d["margin_up"].map(_bmap),
    )
    _body = pd.concat([_lbl, _grp[["NumCust", "P2018", "P2019", "Change"]]], axis=1)
    _body.columns = [
        "Profit",
        "# Trans",
        "ASPT",
        "Avg Marg",
        "# Customers",
        "2018",
        "2019",
        "Change",
    ]

    _o18n = (cust_2018_2019["Status"] == "2018 Only (Lapsed)").sum()
    _o19n = (cust_2018_2019["Status"] == "2019 Only (New/Reactivated)").sum()
    _o18p = cust_2018_2019.loc[
        cust_2018_2019["Status"] == "2018 Only (Lapsed)", "Profit_2018"
    ].sum()
    _o19p = cust_2018_2019.loc[
        cust_2018_2019["Status"] == "2019 Only (New/Reactivated)", "Profit_2019"
    ].sum()
    _blank = {"Profit": "", "# Trans": "", "ASPT": ""}
    _tail = pd.DataFrame(
        [
            {
                **_blank,
                "Avg Marg": "",
                "# Customers": _body["# Customers"].sum(),
                "2018": _body["2018"].sum(),
                "2019": _body["2019"].sum(),
                "Change": _body["Change"].sum(),
            },
            {
                **_blank,
                "Avg Marg": "2018 only",
                "# Customers": _o18n,
                "2018": _o18p,
                "2019": np.nan,
                "Change": -_o18p,
            },
            {
                **_blank,
                "Avg Marg": "2019 only",
                "# Customers": _o19n,
                "2018": np.nan,
                "2019": _o19p,
                "Change": _o19p,
            },
        ]
    )
    _tail.loc[3] = {
        **_blank,
        "Avg Marg": "Total",
        "# Customers": _tail["# Customers"].sum(),
        "2018": _tail["2018"].sum(),
        "2019": _tail["2019"].sum(),
        "Change": _tail["Change"].sum(),
    }
    _tbl = pd.concat([_body, _tail], ignore_index=True)
    _nb = len(_body)
    (
        GT(_tbl)
        .tab_header(
            title="Up-down analysis", subtitle="Customers active in both 2018 and 2019"
        )
        .tab_spanner(label="Profit", columns=["2018", "2019", "Change"])
        .fmt_number(columns="# Customers", decimals=0, use_seps=True)
        .fmt_currency(columns=["2018", "2019", "Change"], currency="USD", decimals=0)
        .sub_missing(missing_text="")
        .cols_align(align="center", columns=["Profit", "# Trans", "ASPT", "Avg Marg"])
        .pipe(style_table, font_size="11px", row_padding="3px")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 3 — How does a cohort evolve?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 3 follows one acquisition cohort across its life. The cohort is the 2,944
    customers whose first purchase was in Q1 2016. Because the data are quarterly,
    the finest time step is a quarter.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Time-to-second-purchase chart
    """)
    return


@app.cell
def _(ACCENT, ACCENT2, GRID, go):
    def second_purchase_chart(sp, width=None, height=360):
        fig = go.Figure()
        fig.add_bar(
            x=sp["Period"],
            y=sp["inc_pct"],
            name="Incremental",
            marker_color=ACCENT,
            marker_line_width=0,
            yaxis="y",
            hovertemplate="%{x}<br>Incremental: %{y:.1%}<extra></extra>",
        )
        fig.add_scatter(
            x=sp["Period"],
            y=sp["cum_pct"],
            name="Cumulative",
            mode="lines+markers",
            line=dict(width=1.8, color=ACCENT2),
            marker=dict(size=6, color=ACCENT2),
            yaxis="y2",
            hovertemplate="%{x}<br>Cumulative: %{y:.1%}<extra></extra>",
        )
        # width=None + autosize lets the figure fill the cell; automargin keeps
        # each axis title clear of its tick labels as the width changes. Axis
        # titles are tinted to match their series (navy bars, ochre line).
        fig.update_layout(
            template="cba",
            title="Percent of cohort making a second purchase, by quarter",
            autosize=True,
            width=width,
            height=height,
            bargap=0.25,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0
            ),
            yaxis=dict(
                title="Incremental",
                tickformat=".0%",
                showgrid=True,
                gridcolor=GRID,
                fixedrange=True,
                automargin=True,
            ),
            yaxis2=dict(
                title="Cumulative",
                tickformat=".0%",
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, 1],
                fixedrange=True,
                automargin=True,
            ),
        )
        fig.update_xaxes(type="category", tickangle=-45, automargin=True)
        return fig

    return (second_purchase_chart,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Revenue decomposition over time

    Cohort revenue in each quarter factors as:

    $$
    \text{Revenue}_t \;=\; (\text{cohort size}) \times (\%\,\text{active}_t) \times \text{ASPAC}_t,
    \qquad \text{ASPAC}_t = \text{AOF}_t \times \text{AOV}_t
    $$

    where ASPAC is the average spend per active member. Plot each factor by
    quarter. Revenue drops sharply in the quarter **after** acquisition, then
    declines slowly with a small Q4 bump each year. The key result: **the decline
    is driven almost entirely by the fall in the fraction active, not by any
    erosion in spend per active buyer.** ASPAC, AOF, and AOV stay broadly flat.
    The customers who remain keep behaving normally; the base shrinks because
    fewer of them remain.
    """)
    return


@app.cell
def _(cust_data):
    _s = (
        cust_data.query("Cohort == 'y2016_q1'")
        .groupby(["Year", "Quarter"])
        .agg(
            ActiveCust=("CustomerID", "count"),
            TotalTrans=("NumTrans", "sum"),
            TotalSpend=("Spend", "sum"),
            TotalProfit=("Profit", "sum"),
        )
    )
    _size = _s.xs((2016, 1))["ActiveCust"]
    cohort_q1_decomp = (
        _s.assign(
            Pct_Active=_s["ActiveCust"] / _size,
            ASPAC=_s["TotalSpend"] / _s["ActiveCust"] / 100,
            AOF=_s["TotalTrans"] / _s["ActiveCust"],
            AOV=_s["TotalSpend"] / _s["TotalTrans"] / 100,
        )
        .reset_index()
        .assign(
            Period=lambda d: (d["Year"] - 2016) * 4 + (d["Quarter"] - 1),
            TotalSpend=lambda d: d["TotalSpend"] / 100,
        )
    )
    return (cohort_q1_decomp,)


@app.cell
def _(cohort_q1_decomp, line_chart):
    line_chart(
        cohort_q1_decomp,
        "Period",
        "TotalSpend",
        "Cohort revenue by quarter",
        "Total spend ($)",
        tickformat="$,.0f",
    )
    return


@app.cell
def _(cohort_q1_decomp, line_chart):
    line_chart(
        cohort_q1_decomp,
        "Period",
        "Pct_Active",
        "Percent active by quarter",
        "% active",
        tickformat=".0%",
    )
    return


@app.cell
def _(cohort_q1_decomp, line_chart):
    line_chart(
        cohort_q1_decomp,
        "Period",
        "ASPAC",
        "Average spend per active member",
        "ASPAC ($)",
        tickformat="$,.0f",
    )
    return


@app.cell
def _(cohort_q1_decomp, line_chart):
    line_chart(
        cohort_q1_decomp,
        "Period",
        "AOV",
        "Average order value by quarter",
        "AOV ($)",
        tickformat="$,.0f",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual repeat-buying patterns
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Reduce each customer to four annual flags. The 2016 flag is set only if the
    customer made **more than one** transaction in 2016, so it records a repeat
    purchase beyond acquisition. The 2017–2019 flags record any activity in the
    year. The four flags give 16 patterns.

    The headline: **45% of the cohort never made a second purchase** by the end of
    2019. The always-active pattern (Y-Y-Y-Y) is about 8%. Most acquired customers
    buy once and do not return. This one-and-done majority is the defining feature
    of a non-contractual base.
    """)
    return


@app.cell
def _(GT, cust_data, pd, style_table):
    _m = cust_data.query("Cohort == 'y2016_q1'").pivot_table(
        index="CustomerID",
        columns="Year",
        values="NumTrans",
        aggfunc="sum",
        fill_value=0,
    )
    _first = _m.columns.min()
    _thr = pd.Series(1, index=_m.columns).mask(_m.columns != _first, 0)
    _flags = _m.gt(_thr).rename(columns=str)
    _years = list(_flags.columns)
    _rp = (
        _flags.reset_index()
        .groupby(_years, as_index=False)
        .agg(NumCust=("CustomerID", "count"))
        .sort_values(_years, ascending=False)
        .reset_index(drop=True)
        .assign(Pct=lambda d: d["NumCust"] / d["NumCust"].sum())
    )
    _body = pd.concat(
        [_rp[_years].replace({True: "Y", False: "N"}), _rp[["NumCust", "Pct"]]], axis=1
    )
    _tail = pd.DataFrame(
        [
            {
                **{c: "" for c in _years[:-1]},
                _years[-1]: "Total",
                "NumCust": _body["NumCust"].sum(),
                "Pct": _body["Pct"].sum(),
            }
        ]
    )
    _tbl = pd.concat([_body, _tail], ignore_index=True)
    (
        GT(_tbl)
        .tab_header(
            title="Cohort annual repeat-buying patterns",
            subtitle="Customers acquired in Q1 2016 (n = 2,944)",
        )
        .tab_spanner(label="Active in year", columns=_years)
        .fmt_number(columns="NumCust", decimals=0)
        .fmt_percent(columns="Pct", decimals=1)
        .cols_label(NumCust="# Customers", Pct="% of cohort")
        .cols_align(align="center", columns=_years)
        .pipe(style_table, font_size="11px", row_padding="3px")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Time to second purchase
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    From the customer-by-quarter matrix, build a latching "has made a second
    purchase" indicator. It turns on in the quarter of a customer's second
    ever purchase and stays on. The column means give the **cumulative** share of
    the cohort that has made a second purchase; the first differences give the
    **incremental** share in each quarter. Most second purchases that ever happen
    happen early. The cumulative curve rises fast, then flattens: a customer who
    has not returned within a few quarters is unlikely to return at all.
    """)
    return


@app.cell
def _(cust_data, pd):
    _m = (
        cust_data.query("Cohort == 'y2016_q1'")
        .sort_values(["Year", "Quarter"])
        .pivot_table(
            index="CustomerID",
            columns=["Year", "Quarter"],
            values="NumTrans",
            aggfunc="sum",
            fill_value=0,
        )
    )
    _first = _m.columns.min()
    _thr = pd.Series(1, index=_m.columns).mask(_m.columns != _first, 0)
    _latched = _m.gt(_thr).rename(columns=str).cummax(axis=1)
    second_purchase = pd.DataFrame(
        {
            "Period": [f"Y{y}Q{q}" for y, q in _m.columns],
            "cum_fr": _latched.sum().to_numpy(),
            "cum_pct": _latched.mean().to_numpy(),
        }
    )
    second_purchase["inc_pct"] = (
        second_purchase["cum_pct"].diff().fillna(second_purchase["cum_pct"].iloc[0])
    )
    return (second_purchase,)


@app.cell
def _(second_purchase, second_purchase_chart):
    second_purchase_chart(second_purchase)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Quarter-to-quarter repeat-buying rate
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The repeat-buying rate for quarter $t$ is the share of customers active in $t$
    who are also active in $t+1$:

    $$
    \text{RBR}_t \;=\; \frac{\#\{\text{active in } t \text{ and } t+1\}}{\#\{\text{active in } t\}}
    $$

    This is a period-to-period measure. It ignores repeat purchases **within** a
    quarter, so it differs from the annual repeat-buying patterns above. A customer
    who bought five times in Q1 2016 and never again counts as a repeat buyer in
    the pattern table but not in this series. Both measures are needed.
    """)
    return


@app.cell
def _(cust_data, line_chart):
    _a = (
        cust_data.query("Cohort == 'y2016_q1'")
        .sort_values(["Year", "Quarter"])
        .pivot_table(
            index="CustomerID",
            columns=["Year", "Quarter"],
            values="NumTrans",
            aggfunc="count",
            fill_value=0,
        )
        .gt(0)
    )
    _both = (_a & _a.shift(-1, axis=1)).sum().iloc[:-1]
    _rbr = (
        (_both / _a.sum().iloc[:-1])
        .rename("Rate")
        .rename_axis(["Year", "Quarter"])
        .reset_index()
        .assign(
            Period=lambda d: (
                "Y" + d["Year"].astype(str) + "Q" + d["Quarter"].astype(str)
            )
        )
    )
    line_chart(
        _rbr,
        "Period",
        "Rate",
        "Quarter-to-quarter repeat-buying rate (Q1 2016 cohort)",
        "Repeat rate",
        x_title="Quarter",
        tickformat=".0%",
        x_categorical=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Value to date (VTD) and its concentration
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Value to date is a customer's total undiscounted profit over the four years.
    It runs from −\$23 to \$3,756, with a mean of \$170 and a median of \$78, so
    **72% of the cohort is below average VTD**. Just over 2% exceed \$1,000. Total
    cohort VTD is about \$499,821.

    The VTD decile report shows **where** that value comes from. The top decile
    buys about 25 times as often as the bottom decile (AOF), but its average order
    value is only about twice as large. **Value concentration is driven by
    frequency, not basket size: high-value customers are high-value because they
    come back.** The final table confirms the mechanism — the top deciles stay
    active across all four years, while the bottom deciles disappear after year
    one.
    """)
    return


@app.cell
def _(bar_distribution, create_bins_labels, create_distribution, cust_data):
    vtd_df = (
        cust_data.query("Cohort == 'y2016_q1'")
        .groupby("CustomerID")
        .agg(
            NumTrans=("NumTrans", "sum"),
            TotalSpend=("Spend", lambda s: s.sum() / 100),
            TotalProfit=("Profit", lambda s: s.sum() / 100),
        )
    )
    bar_distribution(
        create_distribution(vtd_df, "TotalProfit", **create_bins_labels(25, 1000, 0)),
        title="Distribution of Q1 2016 cohort value to date",
        x_title="Value to date ($)",
    )
    return (vtd_df,)


@app.cell
def _(GT, decile_labels, style_table, vtd_df):
    vtd_decile = decile_labels(vtd_df, "TotalProfit")[0].reset_index()
    _rep = (
        vtd_decile.groupby("ProfitDecile", as_index=False)
        .agg(
            Customers=("CustomerID", "count"),
            Transactions=("NumTrans", "sum"),
            Spend=("TotalSpend", "sum"),
            Profit=("TotalProfit", "sum"),
        )
        .assign(
            PctCust=lambda x: x["Customers"] / x["Customers"].sum(),
            PctTrans=lambda x: x["Transactions"] / x["Transactions"].sum(),
            PctSpend=lambda x: x["Spend"] / x["Spend"].sum(),
            PctVTD=lambda x: x["Profit"] / x["Profit"].sum(),
            AvgSpendCust=lambda x: x["Spend"] / x["Customers"],
            AvgVTDCust=lambda x: x["Profit"] / x["Customers"],
            AOF=lambda x: x["Transactions"] / x["Customers"],
            AOV=lambda x: x["Spend"] / x["Transactions"],
            AvgMargin=lambda x: x["Profit"] / x["Spend"],
        )
        .drop(columns=["Customers", "Transactions", "Spend", "Profit"])
    )
    _fields = [
        "Decile",
        "% Cust.",
        "% Trans.",
        "% Spend",
        "% VTD",
        "Avg Spend/Cust.",
        "Avg. VTD/Cust.",
        "AOF",
        "AOV",
        "Avg. Margin",
    ]
    _rep.columns = _fields
    (
        GT(_rep)
        .tab_header(title="Cohort behaviour by VTD decile")
        .fmt_percent(columns=_fields[1:5] + [_fields[-1]], decimals=2)
        .fmt_currency(columns=_fields[5:7] + [_fields[8]])
        .fmt_number(columns=_fields[7])
        .pipe(style_table)
    )
    return (vtd_decile,)


@app.cell
def _(GT, cust_data, style_table, vtd_decile):
    _a = (
        cust_data.query("Cohort == 'y2016_q1'")
        .pivot_table(
            index="CustomerID",
            columns="Year",
            values="NumTrans",
            aggfunc="sum",
            fill_value=0,
        )
        .gt(0)
    )
    _a.columns = _a.columns.astype(str)
    _yr = list(_a.columns)
    _g = _a.join(
        vtd_decile.set_index("CustomerID")["ProfitDecile"], how="right"
    ).groupby("ProfitDecile")
    _counts = _g[_yr].sum().assign(NumCust=_g.size())
    _counts.loc["Total"] = _counts.sum()
    _tbl = (
        _counts[_yr]
        .div(_counts["NumCust"], axis=0)
        .assign(
            **{
                "% Cohort": _counts["NumCust"]
                .div(_counts.loc["Total", "NumCust"])
                .mask(_counts.index == "Total")
            }
        )
        .reset_index(names="Decile")
    )
    (
        GT(_tbl, rowname_col="Decile")
        .tab_header(title="Annual % active by VTD decile", subtitle="Q1 2016 cohort")
        .tab_spanner(label="% active", columns=_yr)
        .fmt_percent(columns=["% Cohort"] + _yr, decimals=1)
        .sub_missing(missing_text="")
        .pipe(style_table)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### RFM analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compute recency, frequency, and monetary value at the end of the window.
    Recency is the index of the last active quarter (1 = Q1 2016 … 16 = Q4 2019).
    Frequency is total transactions. Monetary value is average profit per
    transaction (total profit / total transactions). State the monetary
    definition, because several are in use.

    The cross-tab has 64 cells, but only 52 are structurally possible: a customer
    with frequency 1 made that single purchase in the acquisition quarter, so
    **frequency 1 forces recency Q1**. The 12 cells with frequency 1 and later
    recency are impossible, not empty; do not read them as zeros. The two
    near-mandatory bin choices are a standalone frequency-1 bin and standalone
    recency bins for the first and last periods.
    """)
    return


@app.cell
def _(GT, cust_data, np, pd, style_table):
    _r = (
        cust_data.query("Cohort == 'y2016_q1'")
        .assign(Period=lambda d: (d["Year"] - 2016) * 4 + d["Quarter"])
        .groupby("CustomerID")
        .agg(
            Recency=("Period", "max"),
            Frequency=("NumTrans", "sum"),
            SumProfit=("Profit", "sum"),
        )
        .assign(Monetary=lambda d: d["SumProfit"] / 100 / d["Frequency"])
        .drop(columns="SumProfit")
    )
    _ro = ["Q1", "Q2-Q8", "Q9-Q15", "Q16"]
    _mo = ["<$25", "$25-50", "$50-75", "$75+"]
    _fo = ["1", "2-4", "5-10", "11+"]
    _r = _r.assign(
        R=lambda d: pd.Categorical(
            np.select(
                [d["Recency"].eq(1), d["Recency"].le(8), d["Recency"].le(15)],
                ["Q1", "Q2-Q8", "Q9-Q15"],
                default="Q16",
            ),
            categories=_ro,
            ordered=True,
        ),
        F=lambda d: pd.Categorical(
            np.select(
                [d["Frequency"].eq(1), d["Frequency"].le(4), d["Frequency"].le(10)],
                ["1", "2-4", "5-10"],
                default="11+",
            ),
            categories=_fo,
            ordered=True,
        ),
        M=lambda d: pd.Categorical(
            np.select(
                [d["Monetary"].le(25), d["Monetary"].le(50), d["Monetary"].le(75)],
                ["<$25", "$25-50", "$50-75"],
                default="$75+",
            ),
            categories=_mo,
            ordered=True,
        ),
    )
    _tbl = (
        pd.crosstab([_r["R"], _r["M"]], _r["F"], dropna=False)
        .replace(0, pd.NA)
        .reset_index()
        .rename(columns={"R": "Recency", "M": "Avg profit/trans"})
    )
    (
        GT(_tbl, groupname_col="Recency", rowname_col="Avg profit/trans")
        .tab_header(title="RFM summary", subtitle="Q1 2016 cohort")
        .tab_spanner(label="Frequency", columns=_fo)
        .fmt_number(columns=_fo, decimals=0)
        .sub_missing(missing_text="")
        .cols_align(align="right", columns=_fo)
        .pipe(style_table, row_padding="3px")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 4 — Comparing cohorts
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 4 compares acquisition cohorts, controlling for their size. The working
    dataset is a cohort-by-quarter grid of active customers, transactions, spend,
    and profit, plus the derived % active, AOF, AOV, and margin. Cohort size is the
    diagonal (the acquisition-quarter count). Exclude the `pre y2016` cohort from
    anything that needs cohort size.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Cohort trajectory lines
    """)
    return


@app.cell
def _(go):
    def _sample_colorscale(n, scale=("#0d3b66", "#6aa5d9")):
        # Consultant blue ramp (navy → medium blue) for ordinal cohort series.
        import plotly.colors as pc

        if n == 1:
            return [pc.sample_colorscale(scale, [0.0])[0]]
        return pc.sample_colorscale(scale, [i / (n - 1) for i in range(n)])

    def _q_index(s, base_year, pattern=r"y(\d{4})_q([1-4])"):
        parts = s.str.extract(pattern)
        year, qtr = parts[0].astype("float"), parts[1].astype("float")
        return (year - base_year) * 4 + qtr - 1

    def cohort_lines(
        df,
        metric,
        cohorts=None,
        align=False,
        index=False,
        tickformat=None,
        title=None,
        width=740,
        height=360,
        pattern=r"y(\d{4})_q([1-4])",
    ):
        d = df.reset_index()
        if cohorts is not None:
            d = d[d["Cohort"].isin(cohorts)]
        d = d.sort_values(["Cohort", "YearQuarter"]).copy()
        base_year = d["YearQuarter"].str.extract(pattern)[0].astype("float").min()
        d["Age"] = _q_index(d["YearQuarter"], base_year, pattern) - _q_index(
            d["Cohort"], base_year, pattern
        )
        if index:
            d[metric] = d[metric] / d.groupby("Cohort")[metric].transform("first") * 100
        order = [
            c
            for c in ["pre y2016", *sorted(d["YearQuarter"].unique())]
            if c in set(d["Cohort"])
        ]
        colors = dict(zip(order, _sample_colorscale(len(order))))
        tickformat = tickformat or (",.0f" if index else ",.2f")
        y_title = f"{metric} (acq. qtr = 100)" if index else metric
        if title is None:
            _bits = [
                b for b in ("aligned" if align else "", "indexed" if index else "") if b
            ]
            title = f"{metric} by cohort" + (f" ({', '.join(_bits)})" if _bits else "")
        fig = go.Figure()
        for c in order:
            dc = d[d["Cohort"] == c]
            if align:
                dc = dc.dropna(subset=["Age"])
                x = dc["Age"].astype(int)
            else:
                x = dc["YearQuarter"]
            fig.add_scatter(
                x=x,
                y=dc[metric],
                mode="lines+markers",
                name=c.replace("_", " "),
                line=dict(width=1.6, color=colors[c]),
                marker=dict(size=5, color=colors[c]),
                hovertemplate=f"{c} · %{{x}}<br>%{{y}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            title=title,
            width=width,
            height=height,
            legend=dict(title="Cohort"),
        )
        if align:
            fig.update_xaxes(title="Quarters since acquisition", dtick=1)
        else:
            fig.update_xaxes(title=None, tickangle=-45, type="category")
        fig.update_yaxes(title=y_title, tickformat=tickformat)
        return fig

    return (cohort_lines,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Workflow

    Cohorts differ in size, so raw comparison is misleading. The Q3 2016 cohort
    has 2,842 members and the Q4 2016 cohort has 6,162: the Q4 cohort produces more
    profit only because it is larger. Follow three steps:

    1. Plot **raw** quarterly profit. The larger cohort dominates.
    2. **Index** each cohort's profit to its own acquisition-quarter value (= 100).
       This removes size but does not explain the difference in decay.
    3. **Decompose.** Plot % active, AOF, AOV, and margin for each cohort on the
       same axes. This is where the insight is: it tells you whether a cohort
       underperforms because fewer return, they return less often, they spend less
       per order, or they buy lower-margin goods. Those are four different problems
       with four different responses.

    Repeat step 3 for a like-for-like seasonal pair (Q4 2016 vs Q4 2017), aligned
    by quarters since acquisition.
    """)
    return


@app.cell
def _(cust_data):
    cohort_df = (
        cust_data.groupby(["Cohort", "YearQuarter"])
        .agg(
            TotalCust=("CustomerID", "nunique"),
            TotalTrans=("NumTrans", "sum"),
            TotalSpend=("Spend", lambda s: s.sum() / 100),
            TotalProfit=("Profit", lambda s: s.sum() / 100),
        )
        .assign(
            AOF=lambda d: d["TotalTrans"] / d["TotalCust"],
            AOV=lambda d: d["TotalSpend"] / d["TotalTrans"],
            AvgMargin=lambda d: d["TotalProfit"] / d["TotalSpend"],
        )
    )
    _idx = cohort_df.index
    _csize = (
        cohort_df["TotalCust"]
        .loc[_idx.get_level_values("Cohort") == _idx.get_level_values("YearQuarter")]
        .droplevel("YearQuarter")
    )
    cohort_df = cohort_df.assign(
        PctActive=lambda d: d["TotalCust"].div(_csize, level="Cohort")
    )
    return (cohort_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Q3 2016 vs Q4 2016 — raw profit, then indexed, then decomposed
    """)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "TotalProfit", cohorts=["y2016_q3", "y2016_q4"], tickformat="$,.0f"
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "TotalProfit", cohorts=["y2016_q3", "y2016_q4"], index=True)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "PctActive", cohorts=["y2016_q3", "y2016_q4"], tickformat=".0%"
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "AOV", cohorts=["y2016_q3", "y2016_q4"], tickformat="$,.0f")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Q4 2016 vs Q4 2017 — like-for-like, aligned by quarters since acquisition
    """)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "TotalProfit",
        cohorts=["y2016_q4", "y2017_q4"],
        align=True,
        tickformat="$,.0f",
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "PctActive",
        cohorts=["y2016_q4", "y2017_q4"],
        align=True,
        tickformat=".0%",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### All cohorts, aligned by quarters since acquisition
    """)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "PctActive", align=True, tickformat=".0%")
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "AOV", align=True, tickformat="$,.0f")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lens 5 — Health of the customer base
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 5 takes the firm-level view. It asks whether growth comes from a healthy
    base or from acquisition outrunning churn. The working dataset groups customers
    into annual cohorts (pre-2016, 2016, 2017, 2018, 2019) and builds an annual
    cohort-by-year grid of active customers, transactions, spend, and profit.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Annual summary bars
    """)
    return


@app.cell
def _(ACCENT, ACCENT2, go):
    def acquisitions_bar_chart(df, width=520, height=340):
        d = df.reset_index()
        d = d[d["CohortYear"].astype(str) == d["Year"].astype(str)]
        fig = go.Figure(
            go.Bar(
                x=d["Year"].astype(str),
                y=d["NumActive"],
                marker_color=ACCENT,
                hovertemplate="%{x}<br>New: %{y:,}<extra></extra>",
            )
        )
        fig.update_layout(
            template="cba",
            title="Acquisitions by year",
            width=width,
            height=height,
            bargap=0.4,
        )
        fig.update_yaxes(title="New customers", tickformat=",.0f")
        fig.update_xaxes(type="category")
        return fig

    def active_customers_bar_chart(df, width=520, height=340):
        d = df.groupby("Year", observed=True)["NumActive"].sum().reset_index()
        fig = go.Figure(
            go.Bar(
                x=d["Year"].astype(str),
                y=d["NumActive"],
                marker_color=ACCENT,
                hovertemplate="%{x}<br>Active: %{y:,}<extra></extra>",
            )
        )
        fig.update_layout(
            template="cba",
            title="Active customers by year",
            width=width,
            height=height,
            bargap=0.4,
        )
        fig.update_yaxes(title="Active customers", tickformat=",.0f")
        fig.update_xaxes(type="category")
        return fig

    def spend_profit_bar_chart(df, width=560, height=360):
        d = (
            df.reset_index()
            .melt(
                id_vars=["CohortYear", "Year"],
                value_vars=["TotalSpend", "TotalProfit"],
                var_name="Metric",
                value_name="Value",
            )
            .groupby(["Year", "Metric"], observed=True, as_index=False)["Value"]
            .sum()
        )
        d["Year"] = d["Year"].astype(str)
        fig = go.Figure()
        for metric, col, name in [
            ("TotalSpend", ACCENT, "Spend"),
            ("TotalProfit", ACCENT2, "Profit"),
        ]:
            dm = d[d["Metric"] == metric]
            fig.add_bar(
                x=dm["Year"],
                y=dm["Value"],
                name=name,
                marker_color=col,
                hovertemplate=f"{name} · %{{x}}<br>%{{y:$,.0f}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            title="Spend and profit by year",
            barmode="group",
            width=width,
            height=height,
            bargap=0.35,
            bargroupgap=0.08,
        )
        fig.update_yaxes(title=None, tickformat="$,.0f")
        fig.update_xaxes(type="category")
        return fig

    return (
        acquisitions_bar_chart,
        active_customers_bar_chart,
        spend_profit_bar_chart,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Cohort stack and flow
    """)
    return


@app.cell
def _(SEQ, go, pd):
    ANNUAL_ORDER = ["pre_2016", "2016", "2017", "2018", "2019"]

    def _hex_rgba(hexc, a):
        h = hexc.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{a})"

    def cohort_flow_data(df, metric, scale=1.0, order=tuple(ANNUAL_ORDER)):
        # Prepare every number the flow chart draws, so it can be reviewed as
        # plain tables before plotting. Returns a dict of frames keyed by role.
        order = list(order)
        P = df[metric].unstack("Year").reindex(order).div(scale)
        P.columns = P.columns.astype(str)
        years = list(P.columns)
        totals = P.sum(axis=0)
        share = P.div(totals, axis=1)
        bottoms = P.cumsum(axis=0) - P
        gaps = [f"{years[i]}\u2192{years[i + 1]}" for i in range(len(years) - 1)]
        # Per-cohort retention: a cohort's value next year / its value this year.
        cohort_retention = pd.DataFrame(
            {gaps[i]: P[years[i + 1]] / P[years[i]] for i in range(len(gaps))},
            index=order,
        )
        # Base retention (TCBA 6.2): of a year's whole base, the share still
        # delivered next year (the newest cohort of the next year is excluded).
        base = {}
        for i, g in enumerate(gaps):
            y0, y1 = years[i], years[i + 1]
            new_next = P.loc[y1, y1] if y1 in P.index else 0.0
            new_next = 0.0 if pd.isna(new_next) else new_next
            base[g] = (
                (totals[y1] - new_next) / totals[y0] if totals[y0] else float("nan")
            )
        base_retention = pd.Series(base, name="base_retention")
        return {
            "values": P,
            "totals": totals,
            "share": share,
            "bottoms": bottoms,
            "cohort_retention": cohort_retention,
            "base_retention": base_retention,
            "years": years,
            "gaps": gaps,
        }

    def cohort_flow_chart(
        data, y_title="", total_fmt="{:.2f}", flows=True, width=820, height=520
    ):
        # Pure renderer: every number comes from `data` (see cohort_flow_data).
        P, years, gaps = data["values"], data["years"], data["gaps"]
        totals, share, bottoms = data["totals"], data["share"], data["bottoms"]
        cohort_ret, base_ret = data["cohort_retention"], data["base_retention"]
        order = list(P.index)
        colors = dict(zip(order, SEQ[: len(order)]))
        text_color = {c: ("white" if i < 3 else "#22303f") for i, c in enumerate(order)}
        xpos = list(range(len(years)))
        hw = (1 - 0.45) / 2  # half bar width in x-units (bargap=0.45)
        fig = go.Figure()
        # Ribbons first, so the bars render on top of them.
        if flows:
            for c in order:
                for i in range(len(years) - 1):
                    v1, v2 = P.loc[c, years[i]], P.loc[c, years[i + 1]]
                    if pd.isna(v1) or pd.isna(v2) or v1 == 0 or v2 == 0:
                        continue
                    b1, b2 = bottoms.loc[c, years[i]], bottoms.loc[c, years[i + 1]]
                    fig.add_scatter(
                        x=[i + hw, i + 1 - hw, i + 1 - hw, i + hw],
                        y=[b1 + v1, b2 + v2, b2, b1],
                        fill="toself",
                        mode="lines",
                        line=dict(width=0),
                        fillcolor=_hex_rgba(colors[c], 0.22),
                        hoverinfo="skip",
                        showlegend=False,
                    )
        for c in order:
            y_vals = [None if pd.isna(v) else float(v) for v in P.loc[c]]
            fig.add_bar(
                name=c.replace("_", " "),
                x=xpos,
                y=y_vals,
                marker=dict(color=colors[c], line=dict(color="white", width=1)),
                hovertemplate=f"{c.replace('_', ' ')} \u00b7 %{{x}}<br>{y_title}: %{{y:,.2f}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            barmode="stack",
            bargap=0.45,
            title=f"{y_title.split(' (')[0]} by acquisition cohort",
            autosize=True,
            width=width,
            height=height,
            legend=dict(title="Cohort", traceorder="reversed"),
        )
        # In-segment share-of-year labels.
        for c in order:
            for i, yr in enumerate(years):
                v = P.loc[c, yr]
                if pd.isna(v) or v == 0 or share.loc[c, yr] < 0.03:
                    continue
                fig.add_annotation(
                    x=i,
                    y=float(bottoms.loc[c, yr] + v / 2),
                    text=f"{share.loc[c, yr]:.0%}",
                    showarrow=False,
                    font=dict(size=10, color=text_color[c]),
                )
        # Per-year totals on top.
        for i, yr in enumerate(years):
            fig.add_annotation(
                x=i,
                y=float(totals[yr]),
                yshift=12,
                text=total_fmt.format(totals[yr]),
                showarrow=False,
                font=dict(size=12),
            )
        if flows:
            # Middle labels: each cohort's own retention on its ribbon.
            for c in order:
                for i in range(len(years) - 1):
                    v1, v2 = P.loc[c, years[i]], P.loc[c, years[i + 1]]
                    if pd.isna(v1) or pd.isna(v2) or v1 == 0 or v2 == 0:
                        continue
                    if share.loc[c, years[i]] < 0.05:
                        continue
                    b1, b2 = bottoms.loc[c, years[i]], bottoms.loc[c, years[i + 1]]
                    fig.add_annotation(
                        x=i + 0.5,
                        y=float(0.5 * ((b1 + v1 / 2) + (b2 + v2 / 2))),
                        text=f"{cohort_ret.loc[c, gaps[i]]:.0%}",
                        showarrow=False,
                        font=dict(size=9, color="#374151"),
                    )
            # Top label: base retention between bars (TCBA 6.2), boxed.
            for i, g in enumerate(gaps):
                if pd.isna(base_ret[g]):
                    continue
                base_top = totals[years[i]]
                retained = base_top * base_ret[g]
                fig.add_annotation(
                    x=i + 0.5,
                    y=float(0.5 * (base_top + retained)),
                    text=f"{base_ret[g]:.0%}",
                    showarrow=False,
                    font=dict(size=11, color="#374151"),
                    bgcolor="rgba(255,255,255,0.82)",
                    bordercolor="#c9d3df",
                    borderpad=2,
                )
        fig.update_yaxes(title=y_title, rangemode="tozero", automargin=True)
        fig.update_xaxes(tickvals=xpos, ticktext=years, automargin=True)
        return fig

    return cohort_flow_chart, cohort_flow_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual performance

    The three charts below use the same function, `cohort_flow_chart`. One chart
    shows active customers. One chart shows profit. One chart shows spend.

    Each chart has one bar for each year. Each bar is a stack of colored bands.
    Each band is one acquisition cohort. The height of a band is the part of the
    year total that comes from that cohort. The dark band at the bottom is the
    oldest cohort.

    A ribbon connects each cohort band to the same cohort band in the next year.
    The left end of a ribbon has the height of the cohort in the first year. The
    right end has the height in the next year. The ribbon becomes narrow when the
    cohort gives less value. A narrow ribbon shows a fast fall in the value from
    that cohort.

    The label in each band is the share of that year from the cohort. The label
    above each bar is the year total. The number between two bars is the
    retention of the base. It is the part of one year's value that the cohorts
    from that year still give in the next year. It leaves out the customers who
    join in the next year.

    Read the three charts with the acquisition bar chart and the active-customer
    bar chart above. The charts show one fact. A healthy firm keeps profit and
    customers from old cohorts. A weak firm replaces lost customers with new
    customers each year.
    """)
    return


@app.cell
def _(cust_data, pd):
    _order = ["pre_2016", "2016", "2017", "2018", "2019"]
    _annual = cust_data.assign(
        CohortYear=lambda d: pd.Categorical(
            d["Cohort"].str.extract(r"y(\d{4})_q\d", expand=False).fillna("pre_2016"),
            categories=_order,
            ordered=True,
        )
    )
    annual_cohort_combined = _annual.groupby(["CohortYear", "Year"], observed=True).agg(
        NumActive=("CustomerID", "nunique"),
        TotalTrans=("NumTrans", "sum"),
        TotalSpend=("Spend", lambda s: s.sum() / 100),
        TotalProfit=("Profit", lambda s: s.sum() / 100),
    )
    return (annual_cohort_combined,)


@app.cell
def _(acquisitions_bar_chart, annual_cohort_combined):
    acquisitions_bar_chart(annual_cohort_combined)
    return


@app.cell
def _(active_customers_bar_chart, annual_cohort_combined):
    active_customers_bar_chart(annual_cohort_combined)
    return


@app.cell
def _(annual_cohort_combined, spend_profit_bar_chart):
    spend_profit_bar_chart(annual_cohort_combined)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Prepared flow data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The numbers for the three flow charts are computed first, as tables, so you
    can review them before plotting. `cohort_flow_data` returns the values, the
    per-year totals, the share of each year, the per-cohort year-to-year
    retention, and the base retention. The plot function only draws them.
    """)
    return


@app.cell
def _(annual_cohort_combined, cohort_flow_data):
    flow_active = cohort_flow_data(annual_cohort_combined, "NumActive", scale=1e3)
    flow_profit = cohort_flow_data(annual_cohort_combined, "TotalProfit", scale=1e6)
    flow_spend = cohort_flow_data(annual_cohort_combined, "TotalSpend", scale=1e6)
    return flow_active, flow_profit, flow_spend


@app.cell
def _(flow_profit):
    # Review: each cohort's year-to-year retention for profit (%).
    (flow_profit["cohort_retention"] * 100).round(0)
    return


@app.cell
def _(cohort_flow_chart, flow_active):
    cohort_flow_chart(
        flow_active, y_title="Active customers (000s)", total_fmt="{:.1f}"
    )
    return


@app.cell
def _(cohort_flow_chart, flow_profit):
    cohort_flow_chart(flow_profit, y_title="Profit ($ MM)", total_fmt="{:.2f}")
    return


@app.cell
def _(cohort_flow_chart, flow_spend):
    cohort_flow_chart(flow_spend, y_title="Spend ($ MM)", total_fmt="{:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Two ratios that matter
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Annotate the profit-by-cohort stack with two different ratios. They answer
    different questions.

    **(a) Share of a year's profit from that year's new customers.** In 2016,
    \$1,193,524 of \$1,871,911 (64%) came from the 2016 cohort, so 36% came from
    customers acquired earlier.

    **(b) Year-on-year retention of profit from existing cohorts.** Profit in 2017
    from cohorts acquired before 2017 was \$988,558, which is 53% of what the same
    cohorts delivered in 2016. Per cohort: the 2016 cohort delivered \$1,193,524 in
    2016 and \$451,670 in 2017 (38% retention); the pre-2016 cohort delivered
    \$678,387 then \$536,888 (79% retention).

    The pattern generalizes. **New cohorts decay fast; old, self-selected
    survivors are far stickier.** Each existing cohort's profit falls by roughly
    half per year, and total growth is bought with acquisition. Survivorship, not
    superiority, explains why older cohorts look loyal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Further Lens 5 analyses (specifications)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The following analyses complete Lens 5. They are specified here and left for a
    later pass. Each reuses grids already built above.

    **Time to second purchase, by annual cohort.** For each customer and year, set
    the flag to 0 before the cohort year; in the cohort year set it to 1 if
    transactions exceed 1 (a repeat beyond acquisition); after the cohort year
    latch it on if the customer is active. Sum by cohort year and divide by cohort
    size. Exclude `pre 2016`, whose size is unknown. The result is a triangular
    table, one series per cohort.

    **Annual repeat-buying rate.** For each cohort and adjacent year pair:

    $$
    \text{RBR}(c,\, x \to x{+}1) \;=\; \frac{\#\{c \text{ active in year } x \text{ and } x{+}1\}}{\#\{c \text{ active in year } x\}}
    $$

    Report per cohort and overall. There is no 2019 row, because it needs 2020
    data. Expect the pre-2016 cohort to show the highest rate: survivorship, not
    superiority.

    **Full cohort decomposition by year.** For each annual cohort and year, tabulate
    % active, average annual profit per active member, annual AOF, annual AOV, and
    annual margin. Plot each as a line chart with one line per cohort, and add a
    firm-level total line. Use missing (not zero) for years before a cohort exists,
    so the lines do not dip to zero.

    **Quarterly version.** Repeat the annual pictures at quarterly granularity,
    reusing the Lens 4 grids: quarterly revenue and profit, quarterly profit
    stacked by quarterly cohort, and customers acquired per quarter.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Appendix A — Area-proportional Venn diagram
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The Venn diagram in Lens 2 is area-proportional: each region's area is
    proportional to its customer count. Set the 2018 circle radius to $R = 1$. The
    2019 radius follows from the area ratio:

    $$
    \frac{A_{2019}}{A_{2018}} = \frac{\pi r^2}{\pi R^2} = \frac{31{,}855}{26{,}254}
    \;\Rightarrow\; r = \sqrt{\tfrac{31{,}855}{26{,}254}} \approx 1.1015
    $$

    The overlap must have area proportional to the both-years count:

    $$
    A^{\star} = \pi\left(\frac{9{,}871}{26{,}254}\right) \approx 1.1812
    $$

    The intersection area of two circles a distance $d$ apart is:

    $$
    \begin{split}
    A(d) &= r^2 \cos^{-1}\left(\frac{d^2+r^2-R^2}{2dr}\right) + R^2 \cos^{-1}\left(\frac{d^2-r^2+R^2}{2dR}\right) \\
    &-\frac{1}{2} \sqrt{(d+r-R)(d-r+R)(-d+r+R)(d+r+R)}
    \end{split}
    $$

    Solve $A(d) = A^{\star}$ for $d$ on the interval $|R - r| \le d \le R + r$. At
    $d = |R - r|$ one circle sits inside the other; at $d = R + r$ the circles
    touch and the overlap is 0. $A(d)$ decreases across this interval, so the root
    is unique. A one-dimensional root finder (`brentq`) converges directly and is
    preferred over minimizing the squared error. The solution is $d \approx 1.1469$.


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Appendix B — Implementation checklist
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - Load the long CSV once. Derive `Year`. Keep it as the single source of truth.
    - Reuse one distribution helper for the histograms. Six of them differ only in
      their arguments.
    - Reuse one decile-report helper for the customer, profit, and VTD reports.
    - Reuse one decomposition helper that returns % customers, % transactions, %
      spend, % profit, average spend, average profit, AOF, AOV, and margin.
    - Guard every ratio against a zero denominator. Margin is undefined when spend
      is 0; average spend per transaction is undefined when transactions are 0. Do
      not fill these with 0.
    - Keep the `pre 2016` cohort in the spend and profit totals, but exclude it from
      every ratio that divides by cohort size.
    - Use missing values, not 0, for cohort-year cells before a cohort exists.
    - Cross-check the totals at each stage: 31,855 customers, 60,730 transactions,
      \$5.84M spend, and \$2.80M profit for 2019; 48,238 customers in the Lens 2
      frame; and 2,944 in the Q1 2016 cohort.
    """)
    return


if __name__ == "__main__":
    app.run()
