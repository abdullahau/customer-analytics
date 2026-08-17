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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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

    def stat_badges(
        stats, label, money=True, pct=False, title=None, subtitle=None
    ):
        if money:
            fmt = lambda v: f"${v:,.2f}"
        elif pct:
            fmt = lambda v: f"{v:.2f}%"
        else:
            fmt = lambda v: f"{v:,.2f}"
        t = pd.DataFrame(
            {
                "Statistic": [
                    "Minimum",
                    "Maximum",
                    "Mean",
                    "Median",
                    "% below mean",
                ],
                label: [
                    fmt(stats["min"]),
                    fmt(stats["max"]),
                    fmt(stats["mean"]),
                    fmt(stats["median"]),
                    f"{stats['pct_below_mean']:.1%}",
                ],
            }
        )
        gt = GT(t).cols_align("right", columns=label)
        if title:
            gt = gt.tab_header(title=title, subtitle=subtitle)
        return gt.pipe(style_table)

    def create_percentile_table(
        stats, column, title, subtitle=None, fmt=None
    ):
        t = (
            stats["percentiles"]
            .reset_index()
            .rename(columns={"index": "Percentile", column: "Value"})
        )
        t["Percentile"] = (t["Percentile"] * 100).astype(int).astype(
            str
        ) + "%"
        gt = (
            GT(t).tab_header(title=title, subtitle=subtitle).pipe(style_table)
        )
        if fmt == "currency":
            gt = gt.fmt_currency(columns="Value", decimals=2)
        elif fmt == "pct":
            gt = gt.fmt_percent(
                columns="Value", decimals=2, scale_values=False
            )
        elif fmt == "float":
            gt = gt.fmt_number(columns="Value", decimals=2)
        return gt

    return create_percentile_table, customer_descriptives, stat_badges


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Binning & Distribution
    """)
    return


@app.cell(hide_code=True)
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
            + [
                f"{i}-{i + bin_width}"
                for i in range(min_cutoff, max_cutoff, bin_width)
            ]
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
    ### Decile Summary Table
    """)
    return


@app.cell(hide_code=True)
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
                PctTrans=lambda x: (
                    x["Transactions"] / x["Transactions"].sum()
                ),
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
        fields = [
            f if f != "% Profit" else profit_pct_name for f in DECILE_FIELDS
        ]
        rep.columns = fields
        return rep, fields

    def decile_report_gt(rep, fields, title, pct_decimals=1):
        return (
            GT(rep)
            .tab_header(title=title)
            .fmt_percent(
                columns=fields[1:5] + [fields[-1]], decimals=pct_decimals
            )
            .fmt_currency(columns=fields[5:7] + [fields[8]])
            .fmt_number(columns=fields[7])
            .pipe(style_table)
        )

    return DECILE_FIELDS, decile_labels, decile_report, decile_report_gt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plotly Theme
    """)
    return


@app.cell(hide_code=True)
def _(go, pio):
    # Consultant / academic palette: navy primary, ochre secondary.
    INK, MUTED, GRID = "#1f2328", "#6b7280", "#ececec"
    ACCENT, ACCENT2 = "#1f3a5f", "#c4703a"
    CAT = [
        "#1f3a5f",
        "#c4703a",
        "#4c8b6f",
        "#6b7280",
        "#8a6bb0",
        "#b0563b",
        "#c9a227",
    ]
    SEQ = [
        "#0d3b66",
        "#2b5f8f",
        "#4a86b8",
        "#7aa9d0",
        "#a3c7e8",
    ]  # dark→light blue
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
            title=dict(font=dict(size=11)),
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(font=dict(family=FONT, size=12), bgcolor="white"),
    )
    pio.templates["cba"] = _tpl
    pio.templates.default = "cba"

    # Hide the modebar, scroll/pinch-zoom and the plotly logo for every bare figure.
    # marimo reads a figure's render config from the default renderer (forced to
    # "browser" in-session), so setting it there locks down all charts at once.
    _LOCK = {
        "displayModeBar": False,
        "scrollZoom": False,
        "displaylogo": False,
    }
    for _r in (
        "browser",
        "notebook",
        "notebook_connected",
        "plotly_mimetype",
    ):
        if _r in pio.renderers:
            pio.renderers[_r].config = _LOCK
    return ACCENT, ACCENT2, FONT, GRID, H, INK, MUTED, SEQ, W


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Table & text style
    """)
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _(ACCENT, FONT, GT, INK, MUTED, loc, style):
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
            table_body_hlines_style="none",
            table_border_top_style="none",
            table_border_bottom_color=MUTED,
            table_border_bottom_width="1px",
        )

    def accent_stub(gt):
        return gt.tab_style(
            style=[
                style.fill(color=ACCENT),
                style.text(color="white", weight="bold"),
            ],
            locations=loc.stub(),
        ).tab_options(stub_border_style="none")

    def crosstab_table(
        tbl,
        title,
        subtitle=None,
        spanner=None,
        stubhead=None,
        lead_cols=(),
        percent=True,
        fmt=None,
        decimals=1,
        font_size="12px",
        row_padding="4px",
    ):
        # `lead_cols` stand outside the periods, so the spanner skips them.
        # A two-level index means the outer level groups the rows.
        t = tbl.reset_index()
        group, stub = (
            (None, t.columns[0])
            if tbl.index.nlevels == 1
            else (t.columns[0], t.columns[1])
        )
        vals = [c for c in t.columns if c not in (group, stub)]
        out = (
            GT(t, rowname_col=stub, groupname_col=group)
            .tab_header(title=title, subtitle=subtitle)
            .tab_stubhead(label=stubhead or stub)
            .sub_missing(missing_text="")
            .cols_align(align="right", columns=vals)
        )
        # `fmt` overrides the legacy `percent` bool: "percent" (default),
        # "currency", or "number".
        fmt = fmt or ("percent" if percent else "number")
        if fmt == "percent":
            out = out.fmt_percent(columns=vals, decimals=decimals)
        elif fmt == "currency":
            out = out.fmt_currency(columns=vals, decimals=decimals)
        else:
            out = out.fmt_number(columns=vals, decimals=decimals)
        if spanner:
            out = out.tab_spanner(
                label=spanner, columns=[c for c in vals if c not in lead_cols]
            )
        return out.pipe(accent_stub).pipe(
            style_table, font_size=font_size, row_padding=row_padding
        )

    def bold_totals(gt, stub, names=("Total", "All", "Overall")):
        # Bold any body row whose stub label is a total/summary line (bottom or
        # left), so totals read apart from the detail rows. Consulting-table norm.
        return gt.tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(
                rows=lambda d: d[stub].astype(str).isin(names)
            ),
        )

    return accent_stub, bold_totals, crosstab_table, style_table


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Label & explainer helpers
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    def pretty_cohort(label):
        # Render an internal cohort key as a reader-facing label:
        # "y2016_q1" -> "Y2016 Q1"; "pre y2016" -> "Pre Y2016"; else tidy underscores.
        s = str(label)
        if s.startswith("y") and "_q" in s:
            yr, q = s[1:].split("_q")
            return f"Y{yr} Q{q}"
        if s.startswith("pre "):
            return "Pre Y" + s.rsplit("y", 1)[-1]
        return s.replace("_", " ")

    def how(body):
        # Collapsible "How this is done" block: an info callout in ASD-STE100
        # Simplified Technical English, placed above a calculation/summary cell.
        return mo.accordion(
            {"How this is done": mo.callout(mo.md(body), kind="info")}
        )

    return how, pretty_cohort


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plotly Charts
    """)
    return


@app.cell(hide_code=True)
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

    def _titleblk(text, subtitle=None):
        # Consulting-style exhibit title: a descriptive Title-Case main line, with
        # an optional "so-what"/context subtitle underneath.
        return (
            dict(text=text, subtitle=dict(text=subtitle))
            if subtitle
            else text
        )

    def bar_distribution(
        dist,
        title="Customer distribution",
        x_title="Range",
        subtitle=None,
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
            template="cba",
            title=_titleblk(title, subtitle),
            width=width,
            height=height,
            bargap=0.12,
        )
        fig.update_xaxes(
            title=x_title,
            type="category",
            tickangle=-45,
            automargin=True,
            categoryorder="array",
            categoryarray=order,
            **_thin_ticks(order),
        )
        fig.update_yaxes(
            title="Customers (%)", tickformat=".0%", automargin=True
        )
        return fig

    def overlay_bar_distribution(
        dists,
        labels,
        title="Customer distribution",
        x_title="Range",
        subtitle=None,
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
            title=_titleblk(title, subtitle),
            width=width,
            height=height,
            barmode="group",
            bargap=0.2,
            bargroupgap=0.05,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
            ),
        )
        fig.update_xaxes(
            title=x_title,
            type="category",
            tickangle=-45,
            automargin=True,
            categoryorder="array",
            categoryarray=order,
            **_thin_ticks(order),
        )
        fig.update_yaxes(
            title="Customers (%)", tickformat=".0%", automargin=True
        )
        return fig

    def line_chart(
        df,
        x,
        y,
        title,
        y_title,
        x_title="Quarters Since Acquisition",
        subtitle=None,
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
        fig.update_layout(
            template="cba",
            title=_titleblk(title, subtitle),
            width=width,
            height=height,
        )
        if x_categorical:
            fig.update_xaxes(title=x_title, type="category", tickangle=-45)
        else:
            fig.update_xaxes(title=x_title, dtick=1)
        fig.update_yaxes(title=y_title, tickformat=tickformat)
        return fig

    def dual_line_chart(
        df,
        x,
        series,
        title,
        y_title=None,
        x_title="Quarter",
        subtitle=None,
        tickformat="$,.0f",
        colors=(ACCENT, ACCENT2),
        width=820,
        height=380,
    ):
        # `series` maps a legend name to the column it plots; two lines share
        # one categorical x-axis (e.g. quarterly sales vs. profit).
        fig = go.Figure()
        for (name, col), color in zip(series.items(), colors):
            fig.add_scatter(
                x=df[x],
                y=df[col],
                mode="lines+markers",
                name=name,
                line=dict(width=1.8, color=color),
                marker=dict(size=6, color=color),
                hovertemplate=f"{name} · %{{x}}<br>%{{y:{tickformat}}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            title=_titleblk(title, subtitle),
            width=width,
            height=height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
            ),
        )
        fig.update_xaxes(title=x_title, type="category", tickangle=-45)
        fig.update_yaxes(
            title=y_title, tickformat=tickformat, rangemode="tozero"
        )
        return fig

    return bar_distribution, dual_line_chart, line_chart, overlay_bar_distribution


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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Read `data/madrigal/cust_data_long.csv`, customer long form data. One row is one customer in one quarter.
    2. Multiply `Spend` and `Profit` by 100, round, and hold them as `int64` cents.
    3. Read `Year` and `Quarter` out of the `YearQuarter` text with the pattern `y(\d{4})_q(\d)`.

    **Purpose:** Give every lens one base table.

    **Result:** One row for each customer-quarter with a purchase, plus `Year` and `Quarter`.

    **Watch:** A quarter with no purchase has no row. Money stays in cents until a display step divides by 100.
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
    ### Analysis parameters
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Set the current year, the prior year, and the key of the focus cohort.
    2. Make two label forms for that cohort: `Y2016 Q1` for legends, `Q1 2016` for prose.
    3. Count the distinct customers in the cohort.

    **Purpose:** Hold every year and cohort the audit names in one cell.

    **Result:** Five constants. Titles and subtitles read them, so one edit re-labels the notebook.
    """)
    return


@app.cell
def _(cust_data, pretty_cohort):
    # Single source of truth for the years and focus cohort the audit reports on.
    YEAR_CURR = 2019  # the "current" year Lens 1 audits
    YEAR_PRIOR = 2018  # the comparison year for Lens 2
    FOCUS_COHORT = "y2016_q1"  # the acquisition cohort followed in Lens 3

    FOCUS_COHORT_LABEL = pretty_cohort(
        FOCUS_COHORT
    )  # "Y2016 Q1" (legend/label form)
    FOCUS_COHORT_QTR = (
        f"Q{FOCUS_COHORT[-1]} {FOCUS_COHORT[1:5]}"  # "Q1 2016" (prose form)
    )
    FOCUS_COHORT_N = int(
        cust_data.loc[
            cust_data["Cohort"] == FOCUS_COHORT, "CustomerID"
        ].nunique()
    )
    return FOCUS_COHORT_N, FOCUS_COHORT_QTR, YEAR_CURR, YEAR_PRIOR


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Optional: Convert Wide to Long Format Data
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
    ---
    # Lens 1 — How do customers differ from one another?
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
    ## Data prep
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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. `annual_customer_totals`: keep the rows of one year, group by `CustomerID`, and add `NumTrans`, `Spend`, and `Profit`. Divide the cents back to dollars.
    2. `add_customer_ratios`: add spend per transaction (`Spend / NumTrans`) and margin (`Profit / Spend`, as a percent).

    **Purpose:** Reduce the year to one row for each customer.

    **Result:** One row for each customer active in the year, with five per-customer quantities.

    **Watch:** Margin is undefined where spend is 0. Keep it missing. Do not fill it with 0.
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
                Profit=lambda x: (
                    (x["Profit"] / 100).astype("float32").round(2)
                ),
            )
        )

    def add_customer_ratios(df):
        # per-customer average spend per transaction (equal-weight ingredient; not the ratio-of-totals AOV) and margin
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
    YEAR_CURR,
    add_customer_ratios,
    annual_customer_totals,
    cust_data,
    pd,
    style_table,
):
    cust_data_2019 = add_customer_ratios(
        annual_customer_totals(cust_data, 2019)
    )
    cust_data_2018 = add_customer_ratios(
        annual_customer_totals(cust_data, 2018)
    )

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
        .tab_header(title=f"{YEAR_CURR} Annual Customer Summary")
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
    avg_spend_stats = customer_descriptives(
        cust_data_2019, "AvgSpendPerTrans"
    )
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
    ## Distribution of spend
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
def _(YEAR_CURR, spend_stats, stat_badges):
    stat_badges(
        spend_stats, "Spend", title=f"Spend per Customer ({YEAR_CURR})"
    )
    return


@app.cell
def _(YEAR_CURR, create_percentile_table, spend_stats):
    create_percentile_table(
        spend_stats,
        "Spend",
        "Customer Spend Percentiles",
        f"Annual Spend · {YEAR_CURR}",
        fmt="currency",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019, "Spend", **create_bins_labels(25, 1000)
        ),
        title=f"Annual Customer Spend Distribution ({YEAR_CURR})",
        x_title="Annual Spend ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distribution of profit
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
def _(YEAR_CURR, profit_stats, stat_badges):
    stat_badges(
        profit_stats, "Profit", title=f"Profit per Customer ({YEAR_CURR})"
    )
    return


@app.cell
def _(YEAR_CURR, create_percentile_table, profit_stats):
    create_percentile_table(
        profit_stats,
        "Profit",
        "Customer Profit Percentiles",
        f"Annual Profit · {YEAR_CURR}",
        fmt="currency",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019, "Profit", **create_bins_labels(25, 500, 0)
        ),
        title=f"Annual Customer Profit Distribution ({YEAR_CURR})",
        x_title="Annual Profit ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distribution of the number of transactions
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
def _(YEAR_CURR, stat_badges, trans_stats):
    stat_badges(
        trans_stats,
        "Transactions",
        money=False,
        title=f"Transactions per Customer ({YEAR_CURR})",
    )
    return


@app.cell
def _(YEAR_CURR, create_percentile_table, trans_stats):
    create_percentile_table(
        trans_stats,
        "Transactions",
        "Customer Transactions Percentiles",
        f"Annual Transactions · {YEAR_CURR}",
    )
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Set the bin edges 1 to 10, then infinity. Each bin is half-open: `[i, i+1)`.
    2. Count the customers in each bin. All counts of 10 or more go in the `10+` bin.
    3. Divide each count by the total to get a share.

    **Purpose:** Show how the transaction counts spread across customers.

    **Result:** One row for each bin, with the count and the share.
    """)
    return


@app.cell
def _(YEAR_CURR, bar_distribution, create_distribution, cust_data_2019, np):
    _bins = list(range(1, 11)) + [np.inf]
    _labels = [str(i) for i in range(1, 10)] + ["10+"]
    bar_distribution(
        create_distribution(
            cust_data_2019, "NumTrans", bins=_bins, labels=_labels
        ),
        title=f"Annual Transaction-Count Distribution ({YEAR_CURR})",
        x_title="Annual Transactions",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distribution of average spend per transaction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For each customer, average spend per transaction is $\text{spend}/\text{trans}$.
    Bin at width \$25 and censor at \$500.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Two different "average transaction" numbers
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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
    =\frac{\sum_{i=1}^{I}\text{spend}_i}{\sum_{i=1}^{I}\text{trans}_i}
    $$

    Now rewrite the numerator by multiplying and dividing each customer's spend by their transaction count:

    $$
    =\frac{\sum_{i=1}^{I}\text{trans}_i\times\dfrac{\text{spend}_i}{\text{trans}_i}}{\sum_{i=1}^{I}\text{trans}_i}
    =\sum_{i=1}^{I}\left(\frac{\text{trans}_i}{\sum_{j=1}^{I}\text{trans}_j}\right)\frac{\text{spend}_i}{\text{trans}_i}
    $$

    The last form shows that **AOV is a transaction-weighted average** of the
    per-customer values. Each customer's weight is that customer's share of total
    transactions, so frequent buyers dominate it.

    The mean of per-customer averages gives every customer equal weight:

    $$
    \frac{1}{I}\sum_{i=1}^{I}\frac{\text{spend}_i}{\text{trans}_i}
    $$

    The one-and-done-in-2019 buyers (63% of the base, i.e. exactly one transaction
    that year) count as much as the customer with
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
def _(YEAR_CURR, avg_spend_stats, stat_badges):
    stat_badges(
        avg_spend_stats,
        "Avg spend / transaction",
        title=f"Average Spend per Transaction ({YEAR_CURR})",
    )
    return


@app.cell
def _(YEAR_CURR, avg_spend_stats, create_percentile_table):
    create_percentile_table(
        avg_spend_stats,
        "AvgSpendPerTrans",
        "Average Spend per Transactions Percentiles",
        f"Annual Transactions · {YEAR_CURR}",
        fmt="currency",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019, "AvgSpendPerTrans", **create_bins_labels(25, 500)
        ),
        title=f"Average Spend per Transaction ({YEAR_CURR})",
        x_title="Average Spend per Transaction ($)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Average spend per transaction, by transaction level
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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Put each customer in the same transaction-count bin as the chart above.
    2. Group by the bin.
    3. For each bin, find the mean, the standard deviation, the minimum, the 5th percentile, the median, the 95th percentile, and the maximum of the spend per transaction.

    **Purpose:** Test whether the basket grows with the purchase frequency.

    **Result:** One row for each transaction level, with seven statistics.
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
    aspt_by_level = _binned.groupby(
        "TransBin", as_index=False, observed=True
    ).agg(
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
        .tab_header(
            title="Average Spend per Transaction, by Transaction Level"
        )
        .fmt_currency(columns=list(aspt_by_level.columns[1:]), decimals=2)
        .pipe(style_table)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distribution of average margin
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
def _(YEAR_CURR, avg_margin_stats, stat_badges):
    stat_badges(
        avg_margin_stats,
        "Margin",
        money=False,
        pct=True,
        title=f"Average Margin ({YEAR_CURR})",
    )
    return


@app.cell
def _(YEAR_CURR, avg_margin_stats, create_percentile_table):
    create_percentile_table(
        avg_margin_stats,
        "Margin",
        "Average Margin (%) Percentiles",
        f"Annual Marging (%) · {YEAR_CURR}",
        fmt="pct",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data_2019,
):
    bar_distribution(
        create_distribution(
            cust_data_2019.query("Spend > 0"),
            "Margin",
            **create_bins_labels(5, 100, 0),
        ),
        title=f"Average Margin Distribution ({YEAR_CURR})",
        x_title="Margin (%)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Decile analyses
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A decile report splits the customer base into ten groups and applies the
    profit identity to each group. It shows how concentrated value is, and which
    of the four factors drives that concentration.

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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.mermaid(
        """
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
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two versions exist, and they answer different questions.

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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Rank the customers by profit, high to low. Ties keep their row order.
    2. Cut the ranks into 10 groups of equal size. Group 1 is the most profitable tenth.
    3. For each decile, add the customers, the transactions, the spend, and the profit.
    4. Divide to get the four shares, the two averages, AOF, AOV, and margin.

    **Purpose:** Show how much each tenth of the customers contributes.

    **Result:** 10 rows, one for each decile, with the nine profit-identity columns.

    **Watch:** Each group holds a tenth of the *customers*. The report below cuts on cumulative profit instead, so its groups hold a tenth of the *profit*.
    """)
    return


@app.cell
def _(DECILE_FIELDS, cust_data_2019, decile_report, decile_report_gt, pd):
    _ranked = cust_data_2019.assign(
        CustDecile=lambda d: (
            pd.qcut(
                d["Profit"].rank(method="first", ascending=False),
                q=10,
                labels=False,
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
        profit_decile_rep,
        DECILE_FIELDS,
        "Profit decile report",
        pct_decimals=2,
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
    ---
    # Lens 2 — What changed between two periods?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 2 compares 2018 with 2019 and traces the change in firm performance to
    changes in customer behaviour. The working dataset has one row for each
    customer active in **either** year (an outer join of the two annual
    aggregates; the year a customer is absent stays missing, not zero). It
    covers 48,238 customers. A `Status` field marks each customer as active in
    both years, in 2018 only (lapsed), or in 2019 only (new or reactivated).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data prep
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Merge the prior-year table and the current-year table on `CustomerID` with an outer join. Add the suffixes `_2018` and `_2019`.
    2. Read the merge indicator and set `Status`: active both years, prior year only, or current year only.

    **Purpose:** Pair each customer across the two years.

    **Result:** One row for each customer active in either year (48,238).

    **Watch:** The year a customer is absent stays **missing, not zero**. Sums use `min_count=1`, so a group with no data prints blank instead of $0.
    """)
    return


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
    ## Headline
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Spend and profit both grew, and the active count grew with them. The question
    for the rest of Lens 2 is whether that growth came from existing customers
    buying more, or from acquisition outrunning lapse.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. For each year, take the columns with that year's suffix. Add the transactions, the spend, and the profit; average the spend per transaction and the margin.
    2. Count the distinct active customers in each year.
    3. Find the change: (current − prior) / prior.

    **Purpose:** Show the firm-level move between the two years.

    **Result:** Six rows and three columns: prior year, current year, and the percent change.

    **Watch:** The two averages skip the missing values, so each is over the customers active in that year, not over all 48,238.
    """)
    return


@app.cell
def _(
    GT,
    YEAR_CURR,
    YEAR_PRIOR,
    cust_2018_2019,
    cust_data_2018,
    cust_data_2019,
    pd,
    style_table,
):
    _func_cols = {
        "NumTrans": "sum",
        "Spend": "sum",
        "Profit": "sum",
        "AvgSpendPerTrans": "mean",
        "Margin": "mean",
    }

    def _summarize(df, year):
        suffix = f"_{year}"
        sub = df.filter(like=suffix)
        funcs = {c: _func_cols[c.removesuffix(suffix)] for c in sub.columns}
        return (
            sub.agg(funcs)
            .rename(lambda c: c.removesuffix(suffix))
            .rename(str(year))
        )

    _yoy = pd.concat(
        [_summarize(cust_2018_2019, y) for y in (2018, 2019)], axis=1
    )
    _yoy["Δ"] = (_yoy["2019"] - _yoy["2018"]) / _yoy["2018"]
    _a18 = cust_data_2018["CustomerID"].nunique()
    _a19 = cust_data_2019["CustomerID"].nunique()
    _yoy.loc["Active customers"] = [_a18, _a19, (_a19 - _a18) / _a18]
    (
        GT(_yoy.reset_index(names=""))
        .tab_header(
            title="Spend, Profit and Active-Customer Summary",
            subtitle=f"{YEAR_PRIOR} to {YEAR_CURR}",
        )
        .fmt_percent(columns=["Δ"], decimals=1)
        .fmt_currency(columns=["2018", "2019"], decimals=0)
        .fmt_currency(columns=["2018", "2019"], rows=[3], decimals=2)
        .fmt_number(columns=["2018", "2019"], rows=[0, -1], decimals=0)
        .fmt_percent(
            columns=["2018", "2019"],
            rows=[-2],
            decimals=2,
            scale_values=False,
        )
        .pipe(style_table)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Overlaid distributions
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
    YEAR_CURR,
    YEAR_PRIOR,
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
        title=f"Customer Spend Distribution ({YEAR_PRIOR} vs {YEAR_CURR})",
        x_title="Annual Spend ($)",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    YEAR_PRIOR,
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
        title=f"Customer Profit Distribution ({YEAR_PRIOR} vs {YEAR_CURR})",
        x_title="Annual Profit ($)",
    )
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Build the same bin edges for both years.
    2. Count the customers in each bin, one count for each year.
    3. Divide each count by that year's customer total.

    **Purpose:** Compare the shape of the two years on one axis.

    **Result:** Two frames with the same bins. The chart draws them side by side.

    **Watch:** Plot shares, not counts. The two years hold different numbers of customers.
    """)
    return


@app.cell
def _(
    YEAR_CURR,
    YEAR_PRIOR,
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
            create_distribution(
                cust_data_2018, "NumTrans", bins=_bins, labels=_labels
            ),
            create_distribution(
                cust_data_2019, "NumTrans", bins=_bins, labels=_labels
            ),
        ],
        labels=("2018", "2019"),
        title=f"Transaction-Count Distribution ({YEAR_PRIOR} vs {YEAR_CURR})",
        x_title="Annual Transactions",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    YEAR_PRIOR,
    create_bins_labels,
    create_distribution,
    cust_data_2018,
    cust_data_2019,
    overlay_bar_distribution,
):
    overlay_bar_distribution(
        [
            create_distribution(
                cust_data_2018,
                "AvgSpendPerTrans",
                **create_bins_labels(25, 500),
            ),
            create_distribution(
                cust_data_2019,
                "AvgSpendPerTrans",
                **create_bins_labels(25, 500),
            ),
        ],
        labels=("2018", "2019"),
        title=f"Average Spend per Transaction ({YEAR_PRIOR} vs {YEAR_CURR})",
        x_title="Average Spend per Transaction ($)",
    )
    return


@app.cell
def _(
    YEAR_CURR,
    YEAR_PRIOR,
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
        title=f"Average Margin Distribution ({YEAR_PRIOR} vs {YEAR_CURR})",
        x_title="Margin (%)",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Customer overlap
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Split the two years into three groups: active in both years, 2018 only, and
    2019 only. Of the 26,254 customers active in 2018, only 9,871 returned in 2019.
    Repeat buyers are 38% of the 2018 base and 31% of the 2019 base. The
    area-proportional Venn diagram below shows the three groups to scale;
    Appendix A gives the geometry.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Count the rows in each of the three status groups.
    2. Add "both years" to "prior year only" to get the prior-year active count.
    3. Add "both years" to "current year only" to get the current-year active count.

    **Purpose:** Measure how much the two yearly customer sets overlap.

    **Result:** Five rows: three groups and the two year totals. They set the three areas of the Venn diagram.
    """)
    return


@app.cell
def _(GT, cust_2018_2019, style_table):
    overlap = cust_2018_2019.groupby("Status").agg(
        Customers=("CustomerID", "count")
    )
    overlap.loc["Active 2018"] = (
        overlap.loc["2018 Only (Lapsed)"] + overlap.loc["Active Both Years"]
    )
    overlap.loc["Active 2019"] = (
        overlap.loc["2019 Only (New/Reactivated)"]
        + overlap.loc["Active Both Years"]
    )
    (
        GT(overlap.reset_index(names="Group"))
        .tab_header(title="Customer Overlap")
        .fmt_number(columns="Customers", decimals=0)
        .pipe(style_table)
    )
    return (overlap,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Venn diagram
    """)
    return


@app.cell(hide_code=True)
def _(ACCENT, ACCENT2, brentq, go, np):
    def venn_two(
        n_a, n_b, n_both, label_a, label_b, title, width=560, height=460
    ):
        R = 1.0
        r = np.sqrt(n_b / n_a)
        a_target = np.pi * (n_both / n_a)

        def lens_area(d):
            if d >= R + r:
                return 0.0
            if d <= abs(R - r):
                return np.pi * min(R, r) ** 2
            p1 = R**2 * np.arccos(
                np.clip((d**2 + R**2 - r**2) / (2 * d * R), -1, 1)
            )
            p2 = r**2 * np.arccos(
                np.clip((d**2 + r**2 - R**2) / (2 * d * r), -1, 1)
            )
            p3 = 0.5 * np.sqrt(
                max(
                    (-d + r + R) * (d - r + R) * (d + r - R) * (d + r + R),
                    0.0,
                )
            )
            return p1 + p2 - p3

        d = brentq(
            lambda x: lens_area(x) - a_target, abs(R - r) + 1e-9, R + r - 1e-9
        )
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
            np.argsort(
                np.arctan2(_lens[:, 1] - _ctr[1], _lens[:, 0] - _ctr[0])
            )
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
    ## Profit by activity group and the profit bridge
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
    replacing lost customers with new ones, not by growing the returning base.**
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Group the paired table by `Status`.
    2. Add the prior-year profit and the current-year profit in each group.
    3. Append a Total row.

    **Purpose:** Show where the profit sits across the three groups.

    **Result:** Four rows and two columns.

    **Watch:** `min_count=1` keeps the impossible cells blank. A lapsed customer has no current-year profit, which is not the same as $0.
    """)
    return


@app.cell
def _(GT, bold_totals, cust_2018_2019, style_table):
    profit_by_group = cust_2018_2019.groupby("Status").agg(
        Y2018=("Profit_2018", lambda s: s.sum(min_count=1)),
        Y2019=("Profit_2019", lambda s: s.sum(min_count=1)),
    )
    profit_by_group.loc["Total"] = profit_by_group.sum(min_count=1)
    (
        GT(profit_by_group.reset_index(names="Group"))
        .tab_header(title="Profit by Activity Group")
        .fmt_currency(columns=["Y2018", "Y2019"], decimals=0)
        .cols_label(Y2018="2018 profit", Y2019="2019 profit")
        .pipe(bold_totals, "Group")
        .pipe(style_table)
    )
    return (profit_by_group,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Profit bridge (waterfall)
    """)
    return


@app.cell(hide_code=True)
def _(ACCENT, ACCENT2, INK, MUTED, YEAR_CURR, go):
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
        _b18 = dict(
            marker_color=ACCENT, marker_line=dict(color="white", width=1)
        )
        _b19 = dict(
            marker_color=ACCENT2, marker_line=dict(color="white", width=1)
        )
        w = 0.62
        fig.add_bar(
            x=[0], y=[both18], base=0, width=w, showlegend=False, **_both
        )
        fig.add_bar(
            x=[0], y=[only18], base=both18, width=w, showlegend=False, **_b18
        )
        fig.add_bar(
            x=[1], y=[only18], base=both18, width=w, showlegend=False, **_b18
        )
        fig.add_bar(
            x=[2], y=[abs(delta)], base=lo, width=w, showlegend=False, **_both
        )
        fig.add_bar(
            x=[3], y=[only19], base=both19, width=w, showlegend=False, **_b19
        )
        fig.add_bar(
            x=[4], y=[both19], base=0, width=w, showlegend=False, **_both
        )
        fig.add_bar(
            x=[4], y=[only19], base=both19, width=w, showlegend=False, **_b19
        )

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
        ann(
            2,
            lo,
            f"−{money(abs(delta))}",
            yshift=-8,
            yanchor="top",
            color=INK,
        )
        ann(3, both19 + only19 / 2, money(only19))
        fig.update_layout(
            template="cba",
            title=f"Decomposition of Annual Customer Profit ({YEAR_CURR})",
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
def _(profit_bridge_chart, profit_by_group):
    profit_bridge_chart(profit_by_group)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Performance decomposition by group
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Apply the profit identity to each group in each year. This shows **why** the
    returning group is over-represented in profit relative to its headcount: it
    buys more often (higher AOF) and spends more per order (higher AOV) than the
    one-year-only groups. The table reports active customers, transactions, spend,
    profit, and the derived AOF, AOV, and margin.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Melt the six metric-year columns to long form: customer, status, metric, year, value.
    2. Group by status, metric, and year, and add the values.
    3. Count the active customers as the rows where the transaction value is present.
    4. Divide to get AOF (trans / customers), AOV (spend / trans), and margin (profit / spend).
    5. Turn the metrics into rows and the years into columns.

    **Purpose:** Apply the profit identity to each group in each year.

    **Result:** One block for each status: seven metric rows and two year columns.
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
            title="Performance Summary and Decomposition",
            subtitle="By Group and Year",
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
    ## Decile change analysis
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
    rank. The large `2018 Only` column is concentrated in the low deciles: lapse
    is heaviest among low-value customers, but decile 1 is not immune. A common set
    of cut-offs makes the matrix readable but means each decile no longer holds
    exactly 10% of a year's profit; year-specific cut-offs keep that property at
    the cost of readability.
    """)
    return


@app.cell
def _(
    GT,
    YEAR_CURR,
    YEAR_PRIOR,
    accent_stub,
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
        Row=lambda d: _decile(d["Profit_2018"]),
        Col=lambda d: _decile(d["Profit_2019"]),
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

    _tbl.loc["% 2019"] = (
        _tbl.loc["Total"] / cust_data_2019["CustomerID"].count()
    )
    _tbl.loc["% 2019", ["2018 Only", "Total", "% 2018"]] = np.nan

    _tbl = _tbl.reset_index(names="2018 decile")

    _dcols = [str(c) for c in range(1, 11)]
    _ccols = _dcols + ["2018 Only", "Total"]

    _is_pct = lambda d: d["2018 decile"].eq("% 2019")
    _is_total = lambda d: d["2018 decile"].eq("Total")

    (
        GT(_tbl, rowname_col="2018 decile")
        .tab_header(
            title="Profit Decile Change",
            subtitle=f"{YEAR_PRIOR} to {YEAR_CURR}",
        )
        .tab_stubhead(label=f"{YEAR_PRIOR} decile")
        .tab_spanner(label=f"{YEAR_CURR} decile", columns=_dcols)
        .fmt_number(columns=_ccols, decimals=0, use_seps=True)
        .fmt_percent(columns=_ccols, rows=_is_pct, decimals=1)
        .fmt_percent(columns="% 2018", decimals=1)
        .sub_missing(missing_text="")
        .data_color(
            columns=_dcols,
            rows=lambda d: (
                ~d["2018 decile"].isin(["2019 Only", "Total", "% 2019"])
            ),
            palette=["#ffffff", "#c6dbef", "#4292c6", "#08306b"],
            na_color="white",
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(rows=_is_total),
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns=["Total"]),
        )
        .pipe(accent_stub)
        .pipe(style_table, font_size="11px", row_padding="3px")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Up-down analysis
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
    \$1.1M and the 2019-only block adds about \$1.6M. **Acquisition and lapse, not
    the movement of returning customers, dominate the change in profit.**

    Three points guide the build:

    - **Handle undefined margin.** One customer has zero 2019 spend, so margin is
      undefined. Drop that customer (the count becomes 9,870).
    - **Do not hard-code the number of groups.** This 1% sample shows 14 of the 16
      logically possible groups, but the two missing groups are possible, not
      impossible; the full dataset contains them.
    - **Use three states for transactions.** With a "≥" rule, 3,273 of the 6,524
      customers marked "up" on transactions in fact had the **same** count in both
      years (a third of the repeat base). Split transactions into up / same / down,
      and keep two states for the other three quantities.
      (Ties are rare for profit and spend, 4 and 41 customers respectively)
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Keep the customers active in both years with spend above zero. This drops the one customer whose current-year margin is undefined (9,871 → 9,870).
    2. Flag four moves: profit up, spend per order up, margin up (each "up" means "not lower"), and transactions up, same, or down.
    3. Group by the four flags. Count the customers and add the profit of both years.
    4. Append the subtotal, the lapsed row, the new row, and the total.

    **Purpose:** Sort the returning customers by how their behaviour moved.

    **Result:** The 14 groups that occur in this sample, then four tail rows.

    **Watch:** Do not hard-code 16 groups; the two absent ones are possible. Transactions need three states, because a third of the returning base buys the same number of times in both years.
    """)
    return


@app.cell
def _(GT, YEAR_CURR, YEAR_PRIOR, cust_2018_2019, np, pd, style_table):
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
                d["Profit_2019"] / d["Spend_2019"]
                >= d["Profit_2018"] / d["Spend_2018"]
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
    _body = pd.concat(
        [_lbl, _grp[["NumCust", "P2018", "P2019", "Change"]]], axis=1
    )
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
        cust_2018_2019["Status"] == "2019 Only (New/Reactivated)",
        "Profit_2019",
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
            title="Up-Down Analysis",
            subtitle=f"Customers active in both {YEAR_PRIOR} and {YEAR_CURR}",
        )
        .tab_spanner(label="Profit", columns=["2018", "2019", "Change"])
        .fmt_number(columns="# Customers", decimals=0, use_seps=True)
        .fmt_currency(
            columns=["2018", "2019", "Change"], currency="USD", decimals=0
        )
        .sub_missing(missing_text="")
        .cols_align(
            align="center", columns=["Profit", "# Trans", "ASPT", "Avg Marg"]
        )
        .pipe(style_table, font_size="11px", row_padding="3px")
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Lens 3 — How does a cohort evolve?
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
    ## Data prep
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Keep the focus-cohort rows and group them by year and quarter.
    2. Count the rows for the active customers (one row is one customer-quarter), and add the transactions, the spend, and the profit.
    3. Take the cohort size from the acquisition quarter, and divide to get the percent active.
    4. Divide to get AOF, AOV, and ASPAC (spend per active member). Number the quarters 0 to 15.

    **Purpose:** Follow the cohort quarter by quarter and split its revenue into factors.

    **Result:** 16 rows, one for each quarter, with the four factors of the revenue identity.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Revenue decomposition over time
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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
        "AOF",
        "Average order frequency by quarter",
        "AOF",
        tickformat=",.2f",
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
    ## Annual repeat-buying patterns
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Reduce each customer to four annual flags. The 2016 flag is set only if the
    customer made **more than one** transaction in 2016, so it records a repeat
    purchase beyond acquisition. The 2017–2019 flags record any activity in the
    year. The four flags give 16 patterns.

    The headline: **45% of the cohort never made a second purchase** by the end of 2019.
    The always-active pattern (Y-Y-Y-Y) is about 8%. Most acquired customers
    buy once and do not return. This never-repeated majority (distinct from Lens 1's
    one-and-done-in-2019 share) is the defining feature
    of a non-contractual base.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Pivot the cohort to a customer-by-year table of transaction counts. Fill the empty cells with 0.
    2. Set the flag with a different rule in the acquisition year: more than one transaction there, more than zero after. So the first flag means a repeat beyond the acquisition purchase.
    3. Group the customers by their four-flag pattern. Count them and divide by the cohort size.
    4. Sort the patterns and append a Total.

    **Purpose:** Show the common year-by-year buying patterns.

    **Result:** Up to 16 rows, one for each pattern of Y and N.
    """)
    return


@app.cell
def _(FOCUS_COHORT_N, FOCUS_COHORT_QTR, GT, cust_data, pd, style_table):
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
        [
            _rp[_years].replace({True: "Y", False: "N"}),
            _rp[["NumCust", "Pct"]],
        ],
        axis=1,
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
            title="Cohort Annual Repeat-Buying Patterns",
            subtitle=f"Acquired {FOCUS_COHORT_QTR} · n = {FOCUS_COHORT_N:,}",
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
    ## Time to second purchase
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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Pivot the cohort to a customer-by-quarter table of transaction counts.
    2. Set the same threshold as the annual table: more than one transaction in the acquisition quarter, more than zero after.
    3. Take the running maximum along each row. The flag latches on at the second purchase and stays on.
    4. The column mean is the cumulative share. The first difference is the added share of the quarter.

    **Purpose:** Measure how fast the cohort makes a second purchase.

    **Result:** 16 rows: the count, the cumulative share, and the incremental share.
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
            "Period": [f"Y{y} Q{q}" for y, q in _m.columns],
            "cum_fr": _latched.sum().to_numpy(),
            "cum_pct": _latched.mean().to_numpy(),
        }
    )
    second_purchase["inc_pct"] = (
        second_purchase["cum_pct"]
        .diff()
        .fillna(second_purchase["cum_pct"].iloc[0])
    )
    return (second_purchase,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Time-to-second-purchase chart
    """)
    return


@app.cell(hide_code=True)
def _(ACCENT, ACCENT2, FOCUS_COHORT_QTR, GRID, go):
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
        fig.update_layout(
            template="cba",
            title=f"Second-Purchase Rate by Quarter ({FOCUS_COHORT_QTR} Cohort)",
            autosize=True,
            width=width,
            height=height,
            bargap=0.25,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
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


@app.cell
def _(second_purchase, second_purchase_chart):
    second_purchase_chart(second_purchase)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Quarter-to-quarter repeat-buying rate
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


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Pivot the cohort to a customer-by-quarter table and mark each cell active or not.
    2. Combine the table with itself, shifted one quarter to the left, to find the customers active in a quarter and again in the next.
    3. Divide that count by the customers active in the first of the two quarters.

    **Purpose:** Measure the conditional quarter-to-quarter repeat rate.

    **Result:** 15 rows. The last quarter has no successor, so it is dropped.
    """)
    return


@app.cell
def _(FOCUS_COHORT_QTR, cust_data, line_chart):
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
                "Y" + d["Year"].astype(str) + " Q" + d["Quarter"].astype(str)
            )
        )
    )
    line_chart(
        _rbr,
        "Period",
        "Rate",
        f"Quarter-to-Quarter Repeat-Buying Rate ({FOCUS_COHORT_QTR} Cohort)",
        "Repeat rate",
        x_title="Quarter",
        tickformat=".0%",
        x_categorical=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Value to date (VTD) and its concentration
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### VTD distribution
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Keep the focus-cohort rows and group them by customer.
    2. Add the transactions, and add the spend and the profit over the four years, in dollars.
    3. Bin the profit in steps of $25, with a bin below 0 and censoring at $1,000. Divide the counts by the cohort size.

    **Purpose:** Measure each customer's value to date.

    **Result:** One row for each of the 2,944 cohort members, and the binned frame the chart draws.
    """)
    return


@app.cell
def _(
    FOCUS_COHORT_QTR,
    bar_distribution,
    create_bins_labels,
    create_distribution,
    cust_data,
):
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
        create_distribution(
            vtd_df, "TotalProfit", **create_bins_labels(25, 1000, 0)
        ),
        title=f"Value-to-Date Distribution ({FOCUS_COHORT_QTR} Cohort)",
        x_title="Value to Date ($)",
    )
    return (vtd_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### VTD decile analysis
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Sort the cohort by value to date, high to low, and take the running total in whole cents.
    2. Cut at each tenth of the cohort total, so each decile holds about 10% of the value.
    3. For each decile, add the customers, the transactions, the spend, and the profit.
    4. Divide to get the four shares, the two averages, AOF, AOV, and margin.

    **Purpose:** Show which factor makes the top customers valuable.

    **Result:** 10 rows and 10 columns.

    **Watch:** The cut is on value, so decile 1 holds far fewer than 10% of the customers. Every loss-making customer lands in decile 10.
    """)
    return


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
        .tab_header(title="Cohort Behaviour by VTD Decile")
        .fmt_percent(columns=_fields[1:5] + [_fields[-1]], decimals=2)
        .fmt_currency(columns=_fields[5:7] + [_fields[8]])
        .fmt_number(columns=_fields[7])
        .pipe(style_table)
    )
    return (vtd_decile,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual % active by VTD decile
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Pivot the cohort to a customer-by-year table and mark each cell active or not.
    2. Join the value-to-date decile of each customer.
    3. Count the active customers in each decile and year, and count the size of each decile. Append a Total row.
    4. Divide the counts by the decile size. Add the decile's share of the cohort, and leave it blank on the Total row.

    **Purpose:** Show whether the top-value customers stay active.

    **Result:** 11 rows: the decile size and the percent active in each of the four years.
    """)
    return


@app.cell
def _(FOCUS_COHORT_QTR, bold_totals, crosstab_table, cust_data, vtd_decile):
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
        .rename_axis("Decile")
        # "% Cohort" is the size of the decile, not a yearly rate: keep it next
        # to the decile label, before the "% active" year columns.
        .loc[:, ["% Cohort", *_yr]]
    )
    crosstab_table(
        _tbl,
        title="Annual % Active by VTD Decile",
        subtitle=f"{FOCUS_COHORT_QTR} cohort",
        spanner="% active",
        lead_cols=["% Cohort"],
    ).pipe(bold_totals, "Decile")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## RFM analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compute recency, frequency, and monetary value at the end of the window.
    Recency is the index of the last active quarter (1 = Q1 2016 … 16 = Q4 2019).
    Frequency is total transactions over the analysis window. Monetary value is
    average profit per transaction (total profit / total transactions).
    State the monetary definition, because several are in use.

    | Dim | Bins |
    |---|---|
    | R | Q1; Q2–Q8; Q9–Q15; Q16 |
    | F | 1; 2–4; 5–10; 11+ |
    | M | ≤ \$25; (\$25, \$50]; (\$50, \$75]; > \$75 |

    Cross-tab: rows = R × M, columns = F.

    The cross-tab has 64 cells, but only 52 are structurally possible: a customer
    with frequency 1 made that single purchase in the acquisition quarter, so
    **frequency 1 forces recency Q1**. The 12 cells with frequency 1 and later
    recency are impossible, not empty; do not read them as zeros. The two
    near-mandatory bin choices are a standalone frequency-1 bin and standalone
    recency bins for the first and last periods.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Keep the focus-cohort rows and number the quarters 1 to 16.
    2. For each customer, find the recency (the last active quarter), the frequency (all transactions), and the money (profit per transaction, in dollars).
    3. Band each of the three, as ordered categories: R as Q1 / Q2-Q8 / Q9-Q15 / Q16, F as 1 / 2-4 / 5-10 / 11+, M as ≤$25 / $25-50 / $50-75 / $75+.
    4. Cross-tabulate: recency and money down the rows, frequency across the columns. Keep the unused bands, and blank the zeros.

    **Purpose:** Score each cohort member on recency, frequency, and money.

    **Result:** 16 rows and 4 columns.

    **Watch:** 12 of the 64 cells are impossible, not empty. A customer with one transaction made it in the acquisition quarter, so frequency 1 forces recency Q1.
    """)
    return


@app.cell
def _(FOCUS_COHORT_QTR, crosstab_table, cust_data, np, pd):
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
                [
                    d["Frequency"].eq(1),
                    d["Frequency"].le(4),
                    d["Frequency"].le(10),
                ],
                ["1", "2-4", "5-10"],
                default="11+",
            ),
            categories=_fo,
            ordered=True,
        ),
        M=lambda d: pd.Categorical(
            np.select(
                [
                    d["Monetary"].le(25),
                    d["Monetary"].le(50),
                    d["Monetary"].le(75),
                ],
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
        .rename_axis(index=["Recency", "Avg profit/trans"])
    )
    crosstab_table(
        _tbl,
        title="RFM Summary",
        subtitle=f"{FOCUS_COHORT_QTR} cohort",
        spanner="Frequency",
        percent=False,
        decimals=0,
        row_padding="3px",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Lens 4 — Comparing cohorts
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
    ## Data prep
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Group every customer by acquisition cohort and quarter.
    2. Count the distinct customers, add the transactions, and add the spend and the profit in dollars.
    3. Divide to get AOF, AOV, and margin.
    4. Read each cohort's size off the diagonal, where the cohort key is the quarter key, and divide to get the percent active.

    **Purpose:** Build the quarterly record of all 17 cohorts.

    **Result:** A cohort-by-quarter grid with four totals and four derived factors.

    **Watch:** The pre-2016 cohort has no diagonal cell, so its percent active is missing. That is by design; its size is unknown.
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
        .loc[
            _idx.get_level_values("Cohort")
            == _idx.get_level_values("YearQuarter")
        ]
        .droplevel("YearQuarter")
    )
    cohort_df = cohort_df.assign(
        PctActive=lambda d: d["TotalCust"].div(_csize, level="Cohort")
    )
    return (cohort_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Workflow
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cohort trajectory lines
    """)
    return


@app.cell
def _(go, pretty_cohort):
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
        base_year = (
            d["YearQuarter"].str.extract(pattern)[0].astype("float").min()
        )
        d["Age"] = _q_index(d["YearQuarter"], base_year, pattern) - _q_index(
            d["Cohort"], base_year, pattern
        )
        if index:
            d[metric] = (
                d[metric]
                / d.groupby("Cohort")[metric].transform("first")
                * 100
            )
        order = [
            c
            for c in ["pre y2016", *sorted(d["YearQuarter"].unique())]
            if c in set(d["Cohort"])
        ]
        colors = dict(zip(order, _sample_colorscale(len(order))))
        tickformat = tickformat or (",.0f" if index else ",.2f")
        _labels = {
            "TotalProfit": "Total Profit",
            "TotalSpend": "Total Spend",
            "NumActive": "Active Customers",
            "PctActive": "% Active",
            "AOF": "Average Order Frequency",
            "AOV": "Average Order Value",
            "AvgMargin": "Average Profit Margin",
            "ASPAC": "Spend per Active Customer",
        }
        _mlabel = _labels.get(metric, metric)
        y_title = f"{_mlabel} (Acq. Qtr = 100)" if index else _mlabel
        if title is None:
            _bits = [
                b
                for b in (
                    "Aligned" if align else "",
                    "Indexed" if index else "",
                )
                if b
            ]
            title = f"{_mlabel} by Cohort" + (
                f" ({', '.join(_bits)})" if _bits else ""
            )
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
                name=pretty_cohort(c),
                line=dict(width=1.6, color=colors[c]),
                marker=dict(size=5, color=colors[c]),
                hovertemplate=f"{pretty_cohort(c)} · %{{x}}<br>%{{y}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            title=title,
            width=width,
            height=height,
            legend=dict(title="Cohort"),
        )
        if align:
            fig.update_xaxes(title="Quarters Since Acquisition", dtick=1)
        else:
            fig.update_xaxes(title=None, tickangle=-45, type="category")
        fig.update_yaxes(title=y_title, tickformat=tickformat)
        return fig

    return (cohort_lines,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3 2016 vs Q4 2016 — raw profit, then indexed, then decomposed
    """)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "TotalProfit",
        cohorts=["y2016_q3", "y2016_q4"],
        tickformat="$,.0f",
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "TotalProfit", cohorts=["y2016_q3", "y2016_q4"], index=True
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "PctActive",
        cohorts=["y2016_q3", "y2016_q4"],
        tickformat=".0%",
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "AOF", cohorts=["y2016_q3", "y2016_q4"], tickformat=",.1f"
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "AOV", cohorts=["y2016_q3", "y2016_q4"], tickformat="$,.0f"
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "AvgMargin",
        cohorts=["y2016_q3", "y2016_q4"],
        tickformat=".0%",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q4 2016 vs Q4 2017 — like-for-like, aligned by quarters since acquisition
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


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "AOF",
        cohorts=["y2016_q4", "y2017_q4"],
        align=True,
        tickformat=",.1f",
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "AOV",
        cohorts=["y2016_q4", "y2017_q4"],
        align=True,
        tickformat="$,.0f",
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df,
        "AvgMargin",
        cohorts=["y2016_q4", "y2017_q4"],
        align=True,
        tickformat=".0%",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## All cohorts, aligned by quarters since acquisition
    """)
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(
        cohort_df, "TotalProfit", align=True, index=True, tickformat="$,.0f"
    )
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "PctActive", align=True, tickformat=".0%")
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "AOF", align=True, tickformat=",.1f")
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "AOV", align=True, tickformat="$,.0f")
    return


@app.cell
def _(cohort_df, cohort_lines):
    cohort_lines(cohort_df, "AvgMargin", align=True, tickformat=".0%")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Lens 5 — Health of the customer base
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lens 5 takes the firm-level view. It asks whether growth comes from a healthy
    base or from acquisition outrunning lapse. The working dataset groups customers
    into annual cohorts (pre-2016, 2016, 2017, 2018, 2019) and builds an annual
    cohort-by-year grid of active customers, transactions, spend, and profit.

    **A note on wording — "retention" vs "repeat-buying rate" vs "% of cohort
    active".** Madrigal is a *noncontractual* business: a customer who skips a
    period has not necessarily left, so this audit avoids the word *retention*,
    which properly describes contractual renewal or survival (where a cancellation
    is actually observed). Instead it uses **% of cohort active** — the share of a
    cohort that buys in a given period (*unconditional*, and it includes one-time
    buyers) — and, for value, **carryover** — a cohort's profit in one year relative
    to the year before. The **repeat-buying rate** is the *conditional* quantity —
    the share of customers active in one period who buy again in the next — and is
    reported in Lens 3. The three are not interchangeable; only in a contractual
    setting does "retention rate" have a single, well-defined meaning.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data prep
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual summary bars
    """)
    return


@app.cell(hide_code=True)
def _(ACCENT, ACCENT2, go):
    ANNUAL_VIEWS = {
        "acquisitions": dict(
            metrics={"NumActive": "New customers"},
            diagonal=True,
            title="Acquisitions by Year",
            y_title="New Customers",
            tickformat=",.0f",
            value_fmt=",.0f",
        ),
        "active": dict(
            metrics={"NumActive": "Active customers"},
            diagonal=False,
            title="Active Customers by Year",
            y_title="Active Customers",
            tickformat=",.0f",
            value_fmt=",.0f",
        ),
        "spend_profit": dict(
            metrics={"TotalSpend": "Spend", "TotalProfit": "Profit"},
            diagonal=False,
            title="Spend and Profit by Year",
            y_title=None,
            tickformat="$,.0f",
            value_fmt="$,.0f",
        ),
    }

    def annual_summary_data(df, view):
        spec = ANNUAL_VIEWS[view]
        d = df.reset_index()
        if spec["diagonal"]:
            d = d[d["CohortYear"].astype(str) == d["Year"].astype(str)]
        values = (
            d.groupby("Year", observed=True)[list(spec["metrics"])]
            .sum()
            .rename(columns=spec["metrics"])
        )
        values.index = values.index.astype(str)
        return {
            "values": values,
            "title": spec["title"],
            "y_title": spec["y_title"],
            "tickformat": spec["tickformat"],
            "value_fmt": spec["value_fmt"],
        }

    def annual_summary_chart(
        data, colors=(ACCENT, ACCENT2), width=520, height=340
    ):
        values = data["values"]
        one_series = values.shape[1] == 1
        fig = go.Figure()
        for name, color in zip(values.columns, colors):
            fig.add_bar(
                x=values.index,
                y=values[name],
                name=name,
                marker_color=color,
                hovertemplate=f"{name} · %{{x}}<br>%{{y:{data['value_fmt']}}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            title=data["title"],
            width=width,
            height=height,
            barmode="group",
            bargap=0.4 if one_series else 0.35,
            bargroupgap=0.08,
            showlegend=not one_series,
        )
        fig.update_yaxes(title=data["y_title"], tickformat=data["tickformat"])
        fig.update_xaxes(type="category")
        return fig

    return annual_summary_chart, annual_summary_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cohort stack and flow
    """)
    return


@app.cell(hide_code=True)
def _(pd):
    ANNUAL_ORDER = ["pre_2016", "2016", "2017", "2018", "2019"]

    def cohort_flow_data(
        df, metric, scale=1.0, order=tuple(ANNUAL_ORDER), level="Year"
    ):
        order = list(order)
        P = df[metric].unstack(level).reindex(order).div(scale)
        P.columns = P.columns.astype(str)
        years = list(P.columns)
        totals = P.sum(axis=0)
        share = P.div(totals, axis=1)
        bottoms = P.cumsum(axis=0) - P
        gaps = [
            f"{years[i]}\u2192{years[i + 1]}" for i in range(len(years) - 1)
        ]
        # Per-cohort carryover: a cohort's value next year / its value this year.
        cohort_carryover = pd.DataFrame(
            {
                gaps[i]: P[years[i + 1]] / P[years[i]]
                for i in range(len(gaps))
            },
            index=order,
        )
        # Base carryover: of a year's whole base, the share still
        # delivered next year (the newest cohort of the next year is excluded).
        base = {}
        for i, g in enumerate(gaps):
            y0, y1 = years[i], years[i + 1]
            new_next = P.loc[y1, y1] if y1 in P.index else 0.0
            new_next = 0.0 if pd.isna(new_next) else new_next
            base[g] = (
                (totals[y1] - new_next) / totals[y0]
                if totals[y0]
                else float("nan")
            )
        base_carryover = pd.Series(base, name="base_carryover")
        return {
            "values": P,
            "totals": totals,
            "share": share,
            "bottoms": bottoms,
            "cohort_carryover": cohort_carryover,
            "base_carryover": base_carryover,
            "years": years,
            "gaps": gaps,
        }

    return (cohort_flow_data,)


@app.cell(hide_code=True)
def _(SEQ, go, pd, pretty_cohort):
    def _hex_rgba(hexc, a):
        h = hexc.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{a})"

    def _text_color(hexc):
        # White reads on the dark end of the ramp; switch to ink once the
        # band lightens past mid-luminance.
        h = hexc.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "white" if luminance < 140 else "#22303f"

    def cohort_flow_chart(
        data,
        y_title="",
        total_fmt="{:.2f}",
        flows=True,
        palette=None,
        width=820,
        height=520,
    ):
        P, years, gaps = data["values"], data["years"], data["gaps"]
        totals, share, bottoms = (
            data["totals"],
            data["share"],
            data["bottoms"],
        )
        cohort_car, base_car = (
            data["cohort_carryover"],
            data["base_carryover"],
        )
        order = list(P.index)
        colors = dict(zip(order, (palette or SEQ)[: len(order)]))
        text_color = {c: _text_color(colors[c]) for c in order}
        xpos = list(range(len(years)))
        hw = (1 - 0.45) / 2
        fig = go.Figure()
        # Ribbons first, so the bars render on top of them.
        if flows:
            for c in order:
                for i in range(len(years) - 1):
                    v1, v2 = P.loc[c, years[i]], P.loc[c, years[i + 1]]
                    if pd.isna(v1) or pd.isna(v2) or v1 == 0 or v2 == 0:
                        continue
                    b1, b2 = (
                        bottoms.loc[c, years[i]],
                        bottoms.loc[c, years[i + 1]],
                    )
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
                name=pretty_cohort(c),
                x=xpos,
                y=y_vals,
                marker=dict(
                    color=colors[c], line=dict(color="white", width=1)
                ),
                hovertemplate=f"{pretty_cohort(c)} \u00b7 %{{x}}<br>{y_title}: %{{y:,.2f}}<extra></extra>",
            )
        fig.update_layout(
            template="cba",
            barmode="stack",
            bargap=0.45,
            title=f"{y_title.split(' (')[0]} by Acquisition Cohort",
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
            # Middle labels: each cohort's own carryover on its ribbon.
            for c in order:
                for i in range(len(years) - 1):
                    v1, v2 = P.loc[c, years[i]], P.loc[c, years[i + 1]]
                    if pd.isna(v1) or pd.isna(v2) or v1 == 0 or v2 == 0:
                        continue
                    if share.loc[c, years[i]] < 0.05:
                        continue
                    b1, b2 = (
                        bottoms.loc[c, years[i]],
                        bottoms.loc[c, years[i + 1]],
                    )
                    fig.add_annotation(
                        x=i + 0.5,
                        y=float(0.5 * ((b1 + v1 / 2) + (b2 + v2 / 2))),
                        text=f"{cohort_car.loc[c, gaps[i]]:.0%}",
                        showarrow=False,
                        font=dict(size=9, color="#374151"),
                    )
            # Top label: base carryover between bars, boxed.
            for i, g in enumerate(gaps):
                if pd.isna(base_car[g]):
                    continue
                base_top = totals[years[i]]
                carried = base_top * base_car[g]
                fig.add_annotation(
                    x=i + 0.5,
                    y=float(0.5 * (base_top + carried)),
                    text=f"{base_car[g]:.0%}",
                    showarrow=False,
                    font=dict(size=11, color="#374151"),
                    bgcolor="rgba(255,255,255,0.82)",
                    bordercolor="#c9d3df",
                    borderpad=2,
                )
        fig.update_yaxes(title=y_title, rangemode="tozero", automargin=True)
        fig.update_xaxes(tickvals=xpos, ticktext=years, automargin=True)
        return fig

    return (cohort_flow_chart,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual cohort dynamics
    """)
    return


@app.cell(hide_code=True)
def _(ACCENT2, SEQ, go, pd, pretty_cohort):
    PRE_COHORT = "pre_2016"

    def annual_cohort_dynamics_data(df):
        # One row for each customer and year, with the annual cohort kept on the
        # row. Customers acquired before the window carry the `pre_2016` label.
        # They cannot appear in the second-purchase tables, whose denominator is
        # the cohort size, but they do belong in the repeat-buying rates, whose
        # denominator is the customers active in a year.
        annual = (
            df.assign(
                Cohort=lambda d: (
                    d["Cohort"]
                    .str.extract(r"y(\d{4})_q\d", expand=False)
                    .fillna(PRE_COHORT)
                )
            )
            .groupby(["CustomerID", "Cohort", "Year"], as_index=False)[
                "NumTrans"
            ]
            .sum()
        )
        # One row for each customer, one column for each year. A zero cell means
        # the customer made no purchase in that year.
        trans = annual.pivot_table(
            index=["CustomerID", "Cohort"],
            columns="Year",
            values="NumTrans",
            aggfunc="sum",
            fill_value=0,
        ).rename(columns=str)
        years = list(trans.columns)
        cohorts = trans.index.get_level_values("Cohort")
        # Oldest first, with the pre-window group at the top.
        order = [PRE_COHORT] + sorted(set(cohorts) - {PRE_COHORT})
        order = [c for c in order if c in set(cohorts)]

        # --- Time to second purchase -------------------------------------
        # The first transaction of the acquisition year is the acquisition
        # itself, not a repeat purchase. Take it out of the count. One rule then
        # covers the whole grid: any transaction left over is a second-or-later
        # purchase. The running maximum latches the flag on at the second
        # purchase and keeps it on, so the column sums are cumulative.
        acquired = pd.DataFrame(
            {y: cohorts == y for y in years}, index=trans.index
        )
        flags = (
            trans.sub(acquired.astype("int8"))[cohorts != PRE_COHORT]
            .gt(0)
            .cummax(axis=1)
        )

        grp = flags.groupby("Cohort")
        counts = grp.sum()
        sizes = grp.size().rename("Cohort size")
        # A cohort has no cell before its acquisition year. Keep those cells
        # missing. A zero would read as "nobody has come back yet", and the
        # chart would draw it.
        exists = pd.DataFrame(
            {y: counts.index.astype(int) <= int(y) for y in counts.columns},
            index=counts.index,
        )

        # The share of each cohort that has come back, down the calendar years.
        by_year = counts.div(sizes, axis=0).where(exists)

        # The same shares re-labelled by the age of the cohort: push each row
        # left, so column 1 is every cohort's own first year. Only this
        # alignment compares like with like.
        first = min(int(c) for c in by_year.columns)
        by_age = by_year.apply(
            lambda row: row.shift(first - int(row.name)), axis=1
        )
        by_age.columns = [f"Year {i}" for i in range(1, by_age.shape[1] + 1)]

        # --- Annual repeat-buying rates ----------------------------------
        # Of the cohort members active in year x, the share also active in year
        # x+1. The rate is conditional on being active in the first year of the
        # pair, so a cohort's own acquisition year is its first denominator.
        active = trans.gt(0)
        pairs = {
            f"{years[i]}/{years[i + 1][-2:]}": (years[i], years[i + 1])
            for i in range(len(years) - 1)
        }
        both = pd.DataFrame(
            {lab: active[y0] & active[y1] for lab, (y0, y1) in pairs.items()},
            index=active.index,
        )
        at_risk = pd.DataFrame(
            {lab: active[y0] for lab, (y0, _) in pairs.items()},
            index=active.index,
        )
        rbr_counts = both.groupby("Cohort").sum().reindex(order)
        rbr_base = at_risk.groupby("Cohort").sum().reindex(order)
        # A cohort that does not exist yet has nobody to condition on. Keep the
        # cell missing rather than 0/0.
        rbr = (rbr_counts / rbr_base).where(rbr_base > 0)
        # The firm-level rate: every customer, not split by cohort. It is a
        # weighted average of the rows, not the mean of them.
        rbr.loc["Overall"] = both.sum() / at_risk.sum()
        # The newest cohort has no year before the last pair, so its row is
        # empty. Reading it needs one more year of data.
        rbr = rbr.dropna(how="all")

        return {
            "flags": flags,
            "counts": counts.where(exists),
            "sizes": sizes,
            "cum_pct_by_year": by_year,
            "cum_pct_by_age": by_age,
            "active": active.groupby("Cohort").sum().reindex(order),
            "rbr_counts": rbr_counts,
            "rbr_base": rbr_base,
            "rbr": rbr,
        }

    def cohort_dynamics_chart(
        tbl,
        title="Time to Second Purchase by Annual Cohort",
        x_title="Year",
        y_title="Cumulative % of Cohort",
        name_fmt="{} cohort",
        emphasize=("Overall",),
        tickformat=".0%",
        hover_fmt=".1%",
        rangemode="tozero",
        width=740,
        height=380,
    ):
        # `tbl` is a finished cohort-by-period matrix of shares. Missing cells
        # break the line, so each cohort starts in its own period. Rows named in
        # `emphasize` are firm-level benchmarks, not cohorts: they are drawn in
        # the accent colour and stay out of the cohort colour ramp.
        fig = go.Figure()
        colors = iter(SEQ)
        for cohort, row in tbl.iterrows():
            marked = cohort in emphasize
            color = ACCENT2 if marked else next(colors)
            name = (
                str(cohort)
                if marked
                else name_fmt.format(pretty_cohort(cohort))
            )
            fig.add_scatter(
                x=list(tbl.columns),
                y=row.to_numpy(),
                name=name,
                mode="lines+markers",
                line=dict(
                    width=2.2 if marked else 1.8,
                    color=color,
                    dash="dash" if marked else "solid",
                ),
                marker=dict(size=6, color=color),
                connectgaps=False,
                hovertemplate=(
                    f"{name} · %{{x}}<br>%{{y:{hover_fmt}}}<extra></extra>"
                ),
            )
        fig.update_layout(
            template="cba",
            title=title,
            width=width,
            height=height,
            # A legend above the plot sits inside the top margin, where the
            # title also lives. Deepen that margin so the two do not touch.
            margin=dict(t=104),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1.0,
            ),
        )
        fig.update_xaxes(title=x_title, type="category")
        fig.update_yaxes(
            title=y_title,
            tickformat=tickformat,
            rangemode=rangemode,
        )
        return fig

    return annual_cohort_dynamics_data, cohort_dynamics_chart


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Annual performance
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The three bar charts below give the firm-level headline for each year. They
    use one function, `annual_summary_chart`, with one of three prepared views.

    - **Acquisitions.** The customers acquired in the year. This is the diagonal
      of the cohort grid, where the acquisition year is the calendar year.
    - **Active customers.** All customers who buy in the year, new and old
      together. This is the column total of the grid.
    - **Spend and profit.** The two money totals for the year, side by side.

    Read the three together. Acquisition sets how many customers enter. The
    active count adds the customers who stay from earlier years. Spend and profit
    follow the active count, because one customer's behaviour changes little from
    year to year (Lens 2).

    These bars show **that** the firm grows. They do not show **where** the
    growth comes from. The cohort flow charts below answer that.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Take the acquisition year out of the cohort key. Customers acquired before the window go in a `pre_2016` group.
    2. Make the cohort year an ordered category, so the stack order is fixed from oldest to newest.
    3. Group by cohort year and calendar year. Count the distinct customers, add the transactions, and add the spend and the profit in dollars.

    **Purpose:** Roll the quarterly cohorts up to five yearly cohorts.

    **Result:** 14 rows. The grid is triangular: a cohort has no row before its acquisition year.
    """)
    return


@app.cell
def _(cust_data, pd):
    _order = ["pre_2016", "2016", "2017", "2018", "2019"]
    _annual = cust_data.assign(
        CohortYear=lambda d: pd.Categorical(
            d["Cohort"]
            .str.extract(r"y(\d{4})_q\d", expand=False)
            .fillna("pre_2016"),
            categories=_order,
            ordered=True,
        )
    )
    annual_cohort_combined = _annual.groupby(
        ["CohortYear", "Year"], observed=True
    ).agg(
        NumActive=("CustomerID", "nunique"),
        TotalTrans=("NumTrans", "sum"),
        TotalSpend=("Spend", lambda s: s.sum() / 100),
        TotalProfit=("Profit", lambda s: s.sum() / 100),
    )
    return (annual_cohort_combined,)


@app.cell
def _(annual_cohort_combined, annual_summary_data):
    bars_acquisitions = annual_summary_data(
        annual_cohort_combined, "acquisitions"
    )
    bars_active = annual_summary_data(annual_cohort_combined, "active")
    bars_spend_profit = annual_summary_data(
        annual_cohort_combined, "spend_profit"
    )
    return bars_acquisitions, bars_active, bars_spend_profit


@app.cell
def _(annual_summary_chart, bars_acquisitions):
    annual_summary_chart(bars_acquisitions)
    return


@app.cell
def _(annual_summary_chart, bars_active):
    annual_summary_chart(bars_active)
    return


@app.cell
def _(annual_summary_chart, bars_spend_profit):
    annual_summary_chart(bars_spend_profit, width=560, height=360)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prepared flow data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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
    carryover of the base. It is the part of one year's value that the cohorts
    from that year still give in the next year. It leaves out the customers who
    join in the next year.

    Read the three charts with the acquisition bar chart and the active-customer
    bar chart above. The charts show one fact. A healthy firm keeps profit and
    customers from old cohorts. A weak firm replaces lost customers with new
    customers each year.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Write $P_{c,y}$ for the value that cohort $c$ gives in calendar year $y$,
    divided by the scale (thousands for customers, millions for money). Cells
    before a cohort exists are missing, not zero. Each table below is one part of
    the chart:

    | Table | Formula | What the chart does with it |
    |---|---|---|
    | `values` | $P_{c,y}$ | the height of each band |
    | `totals` | $T_y=\sum_c P_{c,y}$ | the label above each bar |
    | `share` | $P_{c,y}/T_y$ | the label inside each band |
    | `bottoms` | $B_{c,y}=\sum_{c'\le c}P_{c',y}-P_{c,y}$ | where each band starts |
    | `cohort_carryover` | $P_{c,y+1}/P_{c,y}$ | the label on each ribbon |
    | `base_carryover` | $(T_{y+1}-P_{y+1,\,y+1})/T_y$ | the boxed label between two bars |

    **`bottoms` — where each band starts.** Plotly stacks the bars, but the
    labels and the ribbons need the coordinates of each band. Add the values down
    the cohort order to get the top edge of each band. Subtract the band's own
    value to get its foot. The chart then puts the share label at
    $B_{c,y}+P_{c,y}/2$, the middle of the band, and draws each ribbon between
    the feet and the tops of two bands.

    **Cohort carryover — how much one cohort gives again.** Divide a cohort's
    value in one year by its value in the year before. 100% means the cohort
    gives the same value in both years. 40% means it gives two fifths as much.
    This is a ratio of value, not a count of persons: a customer who does not buy
    in one year can buy in the next.

    **Base carryover — how much the whole base gives again.** Take the total for
    the next year, remove the cohort acquired in that year (the newest band), and
    divide by the total for this year. It answers one question: of the value the
    base gives this year, how much do the same cohorts give again next year? It
    leaves out the new customers, so it measures the old base alone.

    Read the two carryovers against the totals. If the totals grow while base
    carryover stays near half, the firm buys its growth with acquisition. The
    first year is the exception: the pre-2016 cohort has no earlier year in the
    window, so no ribbon enters it.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. For one metric, put the calendar years across the columns and the cohorts down the rows, in the fixed order. Divide by the scale: thousands for customers, millions for money.
    2. Add each column to get the year totals. Divide each cell by its column total to get the share.
    3. Add the values down each column and subtract the cell itself. This gives the foot of each band.
    4. Divide each cohort's next year by its own current year to get the cohort carryover.
    5. Take the next year's total, remove the cohort acquired in that year, and divide by this year's total. This gives the base carryover.

    **Purpose:** Compute every number the flow chart draws, as tables you can read first.

    **Result:** Six tables, plus the year labels and the year-pair labels.

    **Watch:** Cells before a cohort exists stay missing. A zero would be drawn.
    """)
    return


@app.cell
def _(annual_cohort_combined, cohort_flow_data):
    flow_active = cohort_flow_data(
        annual_cohort_combined, "NumActive", scale=1e3
    )
    flow_profit = cohort_flow_data(
        annual_cohort_combined, "TotalProfit", scale=1e6
    )
    flow_spend = cohort_flow_data(
        annual_cohort_combined, "TotalSpend", scale=1e6
    )
    return flow_active, flow_profit, flow_spend


@app.cell
def _(cohort_flow_chart, flow_active):
    cohort_flow_chart(
        flow_active, y_title="Active Customers (000s)", total_fmt="{:.3f}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For the profit-by-cohort stack, the two annotations answer different questions.

    **(a) Share of a year's profit from that year's new customers.** In 2016,
    \$1,193,524 of \$1,871,911 (64%) came from the 2016 cohort, so 36% came from
    customers acquired earlier.

    **(b) Year-on-year carryover of profit from existing cohorts.** Profit in 2017
    from cohorts acquired before 2017 was \$988,558, which is 53% of what the same
    cohorts delivered in 2016. Per cohort: the 2016 cohort delivered \$1,193,524 in
    2016 and \$451,670 in 2017 (38% carryover); the pre-2016 cohort delivered
    \$678,387 then \$536,888 (79% carryover).

    The pattern generalizes. **New cohorts decay fast; old, self-selected
    survivors are far stickier.** Each existing cohort's profit falls by roughly
    half per year, and total growth is bought with acquisition. Survivorship, not
    superiority, explains why older cohorts look loyal.
    """)
    return


@app.cell
def _(cohort_flow_chart, flow_profit):
    cohort_flow_chart(
        flow_profit, y_title="Profit ($ MM)", total_fmt="{:.3f}"
    )
    return


@app.cell
def _(cohort_flow_chart, flow_spend):
    cohort_flow_chart(flow_spend, y_title="Spend ($ MM)", total_fmt="{:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Annual cohort dynamics
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The charts above measure the **value** each cohort gives each year. This
    section measures the **behaviour** behind that value: how many members of a
    cohort ever come back, and how long they take. Lens 3 asked this of one
    quarterly cohort. Here the same question runs across all four annual
    cohorts, so the answer can be compared from cohort to cohort.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Time to second purchase, by annual cohort
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cumulative % of each annual cohort that has made a second-ever purchase by end of each year.

    Logic per customer × year cell:
    - 0 if the year precedes the cohort year
    - if year == cohort year: `1 if trans > 1 else 0` (repeat beyond the acquisition purchase)
    - if year > cohort year: `max(previous_flag, 1 if trans > 0 else 0)`

    Sum by cohort year, divide by cohort size. **Exclude the `pre 2016` cohort** — its size is unknown and its "acquisition year" is outside the window.

    Result is a triangular table (each cohort's series starts in its acquisition year).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start from the customer-by-year grid of transaction counts. Build one flag
    for each customer and each year: 0 means the customer has not yet made a
    second purchase, 1 means the customer has made one, in this year or in an
    earlier year. Three rules give the flag, one for each side of the
    acquisition year:

    | Year | Flag |
    |---|---|
    | before the cohort year | 0 — the customer does not exist yet |
    | the cohort year | 1 if transactions > 1 (the first transaction is the acquisition) |
    | after the cohort year | 1 if transactions > 0, or if the flag was already on |

    The last rule **latches**: once a customer has a second purchase, the flag
    stays on for every later year. So the column sums are **cumulative**, and
    dividing them by the cohort size gives the cumulative share of the cohort
    that has come back.

    The code needs only one of these three rules. Take the acquisition
    transaction out of the year it falls in, and every year then asks the same
    question: is there a purchase left over? A year before the cohort holds no
    transactions, so it answers no on its own.

    Exclude the `pre 2016` cohort. Its size is unknown and its acquisition year
    is outside the window, so there is no denominator to divide by.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Add the transactions of each customer in each year. Keep the acquisition year on the row. Customers acquired before the window get the `pre` label.
    2. Pivot to one row for each customer and one column for each year. Each cell holds the transactions of that customer in that year.
    3. For the second purchase, take one transaction out of the acquisition year. That transaction is the acquisition itself, so what is left is the repeat purchases. A cell with more than zero repeat purchases sets the flag.
    4. Take the running maximum along each row. The flag latches on at the second purchase and stays on.
    5. Add the flags down each cohort. Count the members of each cohort.
    6. Divide the sums by the cohort size to get the cumulative share. Then make a second copy with the rows pushed to the left, so column 1 is every cohort's own first year.
    7. For the repeat-buying rate, mark each cell active or not. For each pair of adjacent years, count the customers active in both years and the customers active in the first year.
    8. Add the two counts down each cohort and divide. Add the two counts across all customers and divide, to get the firm-level rate.

    **Purpose:** Measure how many of each cohort come back, how fast, and how many of those active in a year come back the next year.

    **Result:** Two groups of tables to audit. Second purchase: the customer-level `flags`, the `counts` of flagged customers, the cohort `sizes`, and the shares `cum_pct_by_year` and `cum_pct_by_age`. Repeat buying: the `active` counts, the `rbr_counts` and `rbr_base` that make the ratio, and the rates `rbr`.

    **Watch:** Step 3 does the work of a threshold. Without it, the acquisition year needs **more than one** transaction and every later year needs more than zero, which is two rules instead of one. Cells before a cohort exists stay missing, not zero. The cohort acquired in the last year has no repeat-buying rate: that row needs one more year of data.
    """)
    return


@app.cell
def _(annual_cohort_dynamics_data, cust_data):
    # `annual_dynamics` holds the audit trail for both analyses: the
    # customer-level flags, the counts, the cohort sizes and the second-purchase
    # shares (read by calendar year and by age of the cohort), then the active
    # counts, the two counts behind the repeat-buying rate, and the rate itself.
    annual_dynamics = annual_cohort_dynamics_data(cust_data)
    return (annual_dynamics,)


@app.cell
def _(annual_dynamics, crosstab_table):
    crosstab_table(
        annual_dynamics["cum_pct_by_year"],
        title="Time to Second Purchase by Annual Cohort",
        subtitle="Cumulative % of cohort with a second-ever purchase",
        spanner="By end of",
        stubhead="Cohort",
    )
    return


@app.cell
def _(annual_dynamics, crosstab_table):
    crosstab_table(
        annual_dynamics["cum_pct_by_age"],
        title="Time to Second Purchase by Annual Cohort",
        subtitle="Cumulative % of cohort, counted from each cohort's own first year",
        spanner="Years since acquisition",
        stubhead="Cohort",
    )
    return


@app.cell
def _(annual_dynamics, cohort_dynamics_chart):
    cohort_dynamics_chart(
        annual_dynamics["cum_pct_by_age"], x_title="Years Since Acquisition"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The first table reads by calendar year: each cohort starts on its own
    diagonal. The second pushes every row to the left, so the columns hold the
    first, second, third and fourth year of each cohort's own life. Only the
    second alignment compares like with like, and it is the one the chart draws.

    The four cohorts behave alike. About 26% to 29% of each cohort makes a
    second purchase inside its acquisition year, and each curve then rises by
    about 14 points in the following year and by less after that. The 2016
    cohort, the only one observed for four years, reaches 52% by the end of
    2019: **about half of every cohort never buys twice**, and the half that
    does buy twice mostly does so early.

    This is the annual view of the Lens 3 result. There the Q1 2016 cohort
    reached 55% by the end of 2019; here the whole 2016 cohort reaches 52%,
    because its later quarters have less time to come back.

    Read the curves against the cohort flow charts above. A cohort's value
    falls by about half in its second year not because the firm loses
    customers it had, but because most members of the cohort never became
    repeat buyers in the first place.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual repeat-buying rate, by annual cohort
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The second-purchase table counts a cohort against its **size**. The
    repeat-buying rate counts it against the members who were **active**, so it
    is a conditional measure:

    $$
    \text{RBR}(c,\, x \to x{+}1) \;=\; \frac{\#\{c \text{ active in year } x
    \text{ and in year } x{+}1\}}{\#\{c \text{ active in year } x\}}
    $$

    Three differences from the tables above are worth holding on to.

    - The `pre 2016` cohort **is** in this table. The denominator is a count of
      active customers, not the cohort size, so the unknown size does not matter.
    - There is no row for the cohort acquired in the last year of the window.
      Its first pair of years needs one more year of data.
    - The **Overall** row is every customer, not the average of the rows. It is
      the firm-level rate, weighted by how many customers each cohort has.
    """)
    return


@app.cell
def _(annual_dynamics, bold_totals, crosstab_table, pretty_cohort):
    crosstab_table(
        annual_dynamics["rbr"].rename(index=pretty_cohort),
        title="Annual Repeat-Buying Rate by Annual Cohort",
        subtitle="% of a cohort's actives in one year who are active again the next year",
        spanner="Year pair",
        stubhead="Cohort",
        decimals=0,
    ).pipe(bold_totals, "Cohort")
    return


@app.cell
def _(annual_dynamics, cohort_dynamics_chart):
    cohort_dynamics_chart(
        annual_dynamics["rbr"],
        title="Annual Repeat-Buying Rate by Annual Cohort",
        x_title="Year Pair",
        y_title="% of Prior-Year Actives Who Return",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read each row from left to right and the same story appears in every cohort.
    A cohort's **first** repeat-buying rate is about 25% to 27%: of everyone
    active in the acquisition year, a quarter come back the next year. One year
    later the same cohort runs at about 50%, and the year after that at about
    55%. The `pre 2016` cohort, the most self-selected group of all, sits at 51%
    to 57% throughout.

    Nobody became a better customer. The rate rises because the population it is
    measured on **changes**: each pair of years drops the one-time buyers, and
    what is left is the customers who were always going to buy again. This is the
    same sorting effect that lifts the cohort flow charts, seen at the customer
    level instead of the dollar level.

    The **Overall** row moves the other way, from 34% to 38%, and it moves for a
    different reason. It is a share-weighted blend of the rows, so it tracks the
    mix of the base: as the firm ages, a larger part of each year's actives comes
    from older cohorts with high rates. A firm-level repeat-buying rate that
    drifts up is a statement about the mix, not about customer quality.

    Note the low first rate of each cohort against the second-purchase table. Both
    say the same thing in different units — most of a cohort buys once — but the
    repeat-buying rate is the harsher test, because it asks for a purchase in a
    **specific** year, while a second-ever purchase can come at any time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Full cohort decomposition by year
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cohort flow charts above show **how much** value each cohort gives each
    year. This section applies the profit identity to each cohort × year cell to
    show **why**: whether a cohort's value moves because more or fewer of its
    members are active, because they buy more or less often, because their orders
    are bigger or smaller, or because their margin shifts.

    | Table | Formula |
    |---|---|
    | % active | active / cohort size *(2016–2019 cohorts only — the pre-2016 cohort's size is unknown)* |
    | Avg annual profit per active member | profit / active |
    | Annual AOF | trans / active |
    | Annual AOV | spend / trans |
    | Annual avg margin | profit / spend |

    Each table below has one row for each cohort and one column for each
    calendar year; a cell before a cohort's acquisition year is missing, not
    zero, so its line does not fall to the axis. The AOF, AOV and margin tables
    also carry a **Total** row — the firm-level ratio for that year, over every
    active customer regardless of cohort. That row is exactly Table 6.9 of the
    companion, read off one table at a time instead of assembled separately.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Start from `annual_cohort_combined`. Find each cohort's size from its diagonal cell (`CohortYear == Year`), the same trick `cohort_df` uses in Lens 4.
    2. Divide active customers by cohort size to get % active. Divide profit, transactions and spend by active customers and by each other to get the four remaining ratios.
    3. Separately, add `annual_cohort_combined` down each column (across cohorts) to get one row of year totals, then apply the same ratios to that row. This is the **Total** row, weighted by how many customers each cohort has — not an average of the per-cohort rows.
    4. Pivot each metric to cohort rows and year columns, append the Total row where one applies, and relabel the cohorts for display.

    **Purpose:** Decompose each cohort's annual value into the four factors of the profit identity.

    **Result:** Five cohort-by-year tables, plus a Total row on four of them.

    **Watch:** The pre-2016 cohort has no diagonal cell, so its % active is missing for every year, by design — there is nothing to divide by.
    """)
    return


@app.cell
def _(annual_cohort_combined):
    _idx = annual_cohort_combined.index
    _csize = (
        annual_cohort_combined["NumActive"]
        .loc[
            _idx.get_level_values("CohortYear").astype(str)
            == _idx.get_level_values("Year").astype(str)
        ]
        .droplevel("Year")
    )
    annual_decomp = annual_cohort_combined.assign(
        PctActive=lambda d: d["NumActive"].div(_csize, level="CohortYear"),
        AvgProfitPerActive=lambda d: d["TotalProfit"] / d["NumActive"],
        AOF=lambda d: d["TotalTrans"] / d["NumActive"],
        AOV=lambda d: d["TotalSpend"] / d["TotalTrans"],
        AvgMargin=lambda d: d["TotalProfit"] / d["TotalSpend"],
    )
    return (annual_decomp,)


@app.cell
def _(annual_cohort_combined):
    # The firm-level ratio for each year: sum every cohort's totals for that
    # year, then derive AOF/AOV/margin/profit-per-active from the sums. This is
    # a share-weighted blend of the cohort rows, not a mean of them.
    year_totals = annual_cohort_combined.groupby("Year")[
        ["NumActive", "TotalTrans", "TotalSpend", "TotalProfit"]
    ].sum()
    year_totals = year_totals.assign(
        AOF=lambda d: d["TotalTrans"] / d["NumActive"],
        AOV=lambda d: d["TotalSpend"] / d["TotalTrans"],
        AvgProfitPerActive=lambda d: d["TotalProfit"] / d["NumActive"],
        AvgMargin=lambda d: d["TotalProfit"] / d["TotalSpend"],
    )
    year_totals.index = year_totals.index.astype(str)
    return (year_totals,)


@app.cell
def _(pretty_cohort):
    def cohort_year_table(decomp, metric, year_totals=None, add_total=False):
        # Wide cohort-by-year view of one metric from `annual_decomp`, oldest
        # cohort first, with an optional Total row from `year_totals`.
        p = decomp[metric].unstack("Year")
        p.columns = p.columns.astype(str)
        p.index = p.index.astype(str)
        p = p.reindex(["pre_2016", "2016", "2017", "2018", "2019"]).dropna(
            how="all"
        )
        if add_total:
            p.loc["Total"] = year_totals[metric]
        p.index = p.index.map(pretty_cohort)
        p.index.name = "Cohort"
        return p

    return (cohort_year_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Percent of cohort active
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Every cohort starts at 100% in its own acquisition year, by definition, and
    falls fast after that: the 2016 cohort is 27% active in 2017, 23% in 2018,
    21% in 2019. The 2017 and 2018 cohorts fall along the same path. This is the
    per-cohort mechanism behind the cohort flow charts above — a band shrinks
    from year to year mostly because fewer of its members buy, not because the
    ones who do buy spend less (see AOV and margin below, which are close to
    flat).
    """)
    return


@app.cell
def _(annual_decomp, cohort_year_table, crosstab_table):
    pct_active_tbl = cohort_year_table(annual_decomp, "PctActive")
    crosstab_table(
        pct_active_tbl,
        title="Percent of Annual Cohort Active",
        subtitle="Share of cohort members buying in each calendar year",
        spanner="Calendar year",
        stubhead="Cohort",
        decimals=0,
    )
    return (pct_active_tbl,)


@app.cell
def _(cohort_dynamics_chart, pct_active_tbl):
    cohort_dynamics_chart(
        pct_active_tbl,
        title="Percent of Annual Cohort Active by Year",
        x_title="Year",
        y_title="% of Cohort Active",
        emphasize=(),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Average annual profit per active cohort member
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Divide each cohort's profit in a year by the number of its members active
    that year. A cohort's own acquisition year is its weakest: the 2016 cohort
    gives \$80 per active member in 2016, then \$110, \$106, \$107 in the years
    after. The pre-2016 cohort — the oldest, most self-selected group — sits
    highest throughout, \$115–\$120. **The customers who come back are worth
    more, on average, than the ones acquired that year**, because the
    acquisition-year figure is dragged down by the one-time buyers who never
    return. The Total row is Table 6.9's missing fourth ratio: firm-level profit
    per active customer holds close to \$87–\$91 across all four years, far
    steadier than any single cohort's own trajectory.
    """)
    return


@app.cell
def _(annual_decomp, cohort_year_table, year_totals):
    avg_profit_tbl = cohort_year_table(
        annual_decomp, "AvgProfitPerActive", year_totals, add_total=True
    )
    return (avg_profit_tbl,)


@app.cell
def _(avg_profit_tbl, bold_totals, crosstab_table):
    crosstab_table(
        avg_profit_tbl,
        title="Average Annual Profit per Active Cohort Member",
        spanner="Calendar year",
        stubhead="Cohort",
        fmt="currency",
        decimals=0,
    ).pipe(bold_totals, "Cohort")
    return


@app.cell
def _(avg_profit_tbl, cohort_dynamics_chart):
    cohort_dynamics_chart(
        avg_profit_tbl,
        title="Average Annual Profit per Active Cohort Member",
        x_title="Year",
        y_title="Avg. Annual Profit ($)",
        emphasize=("Total",),
        tickformat="$,.0f",
        hover_fmt="$,.2f",
        rangemode="normal",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Annual AOF, AOV and margin by cohort
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The three factors behind average profit per active member. Read them
    together: a cohort's AOF **rises** with age (the 2016 cohort: 1.55 orders in
    its acquisition year, then 2.40, 2.50, 2.48), while its AOV and margin stay
    close to flat or drift down slightly (AOV \$104 → \$94 → \$89 → \$90; margin
    50% → 49% → 47% → 48%). The same story repeats for every cohort. This
    confirms the % active finding: **a cohort's fall in value is a story about
    fewer buyers, not smaller or lower-margin orders** — order frequency among
    survivors is stable to rising, and basket size and margin barely move. The
    Total row of each table gives the firm-level AOF, AOV and margin by year
    (Table 6.9): AOF rises from 1.77 to 1.91 as the base ages and the mix shifts
    toward higher-frequency returning customers, while AOV and margin drift down
    slightly as the firm adds cohorts of new, lower-spending customers each year.
    """)
    return


@app.cell
def _(annual_decomp, bold_totals, cohort_year_table, crosstab_table, year_totals):
    aof_tbl = cohort_year_table(
        annual_decomp, "AOF", year_totals, add_total=True
    )
    crosstab_table(
        aof_tbl,
        title="Annual AOF by Cohort",
        subtitle="Average order frequency — transactions per active member",
        spanner="Calendar year",
        stubhead="Cohort",
        fmt="number",
        decimals=2,
    ).pipe(bold_totals, "Cohort")
    return (aof_tbl,)


@app.cell
def _(aof_tbl, cohort_dynamics_chart):
    cohort_dynamics_chart(
        aof_tbl,
        title="Annual AOF by Cohort",
        x_title="Year",
        y_title="AOF (Transactions per Active Member)",
        emphasize=("Total",),
        tickformat=",.2f",
        hover_fmt=",.2f",
        rangemode="normal",
    )
    return


@app.cell
def _(annual_decomp, bold_totals, cohort_year_table, crosstab_table, year_totals):
    aov_tbl = cohort_year_table(
        annual_decomp, "AOV", year_totals, add_total=True
    )
    crosstab_table(
        aov_tbl,
        title="Annual AOV by Cohort",
        subtitle="Average order value — spend per transaction",
        spanner="Calendar year",
        stubhead="Cohort",
        fmt="currency",
        decimals=2,
    ).pipe(bold_totals, "Cohort")
    return (aov_tbl,)


@app.cell
def _(aov_tbl, cohort_dynamics_chart):
    cohort_dynamics_chart(
        aov_tbl,
        title="Annual AOV by Cohort",
        x_title="Year",
        y_title="AOV ($ per Transaction)",
        emphasize=("Total",),
        tickformat="$,.0f",
        hover_fmt="$,.2f",
        rangemode="normal",
    )
    return


@app.cell
def _(annual_decomp, bold_totals, cohort_year_table, crosstab_table, year_totals):
    margin_tbl = cohort_year_table(
        annual_decomp, "AvgMargin", year_totals, add_total=True
    )
    crosstab_table(
        margin_tbl,
        title="Annual Average Margin by Cohort",
        spanner="Calendar year",
        stubhead="Cohort",
        fmt="percent",
        decimals=0,
    ).pipe(bold_totals, "Cohort")
    return (margin_tbl,)


@app.cell
def _(cohort_dynamics_chart, margin_tbl):
    cohort_dynamics_chart(
        margin_tbl,
        title="Annual Average Margin by Cohort",
        x_title="Year",
        y_title="Average Margin (%)",
        emphasize=("Total",),
        rangemode="normal",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Quarterly analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The annual pictures above trade resolution for readability: a year is long
    enough to smooth over the seasonal pattern in the business. This section
    repeats three of them at quarterly granularity, reusing `cust_data` directly
    and the `cohort_df` cohort-by-quarter grid built in Lens 4.

    1. **Quarterly revenue and profit** — the same headline as the annual bars,
       one point per quarter instead of per year.
    2. **Quarterly profit, stacked by quarterly acquisition cohort** — the
       fine-grained version of the annual cohort-flow chart, with 17 cohorts
       instead of 5.
    3. **Customers acquired each quarter** — the diagonal of the quarterly grid.
    """)
    return


@app.cell(hide_code=True)
def _(how):
    how(r"""
    1. Group `cust_data` by `YearQuarter` and add spend and profit, in dollars, for Figure 6.11.
    2. Reuse `cohort_df` from Lens 4 for the quarterly cohort grid: it already has one row for each cohort × quarter with total profit. Unstack it to cohort rows and quarter columns, in chronological order, for Figure 6.12. `pre y2016` sorts first because the string `"pre_y2016"` is alphabetically before every `"yYYYY_qQ"` key — no manual ordering list is needed.
    3. Turn off the ribbons on the flow chart. With 17 cohorts the ribbons would overlap into noise; the stacked bars and their share labels carry the picture on their own.
    4. Count the distinct customers in each quarterly cohort (excluding `pre y2016`, which is not a quarter of acquisition) for Figure 6.13.

    **Purpose:** Show the within-year seasonal pattern that the annual view smooths away.

    **Result:** Three figures at quarterly grain, built from data already on hand.
    """)
    return


@app.cell
def _(cust_data):
    quarterly_totals = (
        cust_data.groupby("YearQuarter", as_index=False)
        .agg(
            TotalSpend=("Spend", lambda s: s.sum() / 100),
            TotalProfit=("Profit", lambda s: s.sum() / 100),
        )
        .sort_values("YearQuarter")
        .assign(
            Label=lambda d: "Q"
            + d["YearQuarter"].str[-1]
            + "/"
            + d["YearQuarter"].str[1:5].str[-2:]
        )
    )
    return (quarterly_totals,)


@app.cell
def _(dual_line_chart, quarterly_totals):
    dual_line_chart(
        quarterly_totals,
        x="Label",
        series={"Sales": "TotalSpend", "Profit": "TotalProfit"},
        title="Summary of Quarterly Performance",
        y_title="$",
        tickformat="$,.0f",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Both series spike every fourth quarter and reset lower in Q1, then climb
    again — Madrigal's demand is seasonal, and each year's Q4 peak sits above
    the Q4 peak before it. The annual bars (Figure 6.1's cousin, above) show a
    steady climb because a calendar year always contains one full cycle of this
    pattern; the quarterly view shows the cycle itself.
    """)
    return


@app.cell
def _(cohort_df, cohort_flow_data):
    _order = sorted(cohort_df.index.get_level_values("Cohort").unique())
    flow_quarterly_profit = cohort_flow_data(
        cohort_df, "TotalProfit", scale=1e3, order=_order, level="YearQuarter"
    )
    return (flow_quarterly_profit,)


@app.cell
def _(flow_quarterly_profit):
    def _blue_ramp(n, c0="0d3b66", c1="a3c7e8"):
        # A dark-navy-to-light-blue ramp long enough for all 17 quarterly
        # cohorts, in the same family as the 5-stop `SEQ` palette.
        r0, g0, b0 = int(c0[0:2], 16), int(c0[2:4], 16), int(c0[4:6], 16)
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        steps = [i / (n - 1) for i in range(n)] if n > 1 else [0.0]
        return [
            f"#{round(r0 + (r1 - r0) * t):02x}"
            f"{round(g0 + (g1 - g0) * t):02x}"
            f"{round(b0 + (b1 - b0) * t):02x}"
            for t in steps
        ]

    quarterly_palette = _blue_ramp(len(flow_quarterly_profit["values"].index))
    return (quarterly_palette,)


@app.cell
def _(cohort_flow_chart, flow_quarterly_profit, quarterly_palette):
    cohort_flow_chart(
        flow_quarterly_profit,
        y_title="Quarterly Profit ($ 000s)",
        total_fmt="{:.0f}",
        flows=False,
        palette=quarterly_palette,
        width=900,
        height=540,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The annual flow chart above folds 16 quarters of history into 5 broad bands.
    Here each band is one acquisition **quarter**, so the picture shows what the
    annual version cannot: within-year seasonality is itself acquisition-driven.
    The bottom-most, oldest slice (`pre y2016`) thins from bar to bar exactly as
    the annual pre-2016 band does; each subsequent Q4 bar carries a thick new
    band from that quarter's own (large) acquisition cohort, which is why every
    Q4 profit spike in Figure 6.11 is partly a spike in new customers, not just
    in existing customers buying more.
    """)
    return


@app.cell
def _(cust_data, pretty_cohort):
    quarterly_cohort_sizes = (
        cust_data.query("Cohort != 'pre_y2016'")
        .groupby("Cohort")["CustomerID"]
        .nunique()
        .sort_index()
        .rename("Customers")
        .reset_index()
        .assign(CohortLabel=lambda d: d["Cohort"].map(pretty_cohort))
    )
    return (quarterly_cohort_sizes,)


@app.cell
def _(ACCENT, go, quarterly_cohort_sizes):
    def _quarterly_acquisitions_chart(df, width=860, height=360):
        fig = go.Figure(
            go.Bar(
                x=df["CohortLabel"],
                y=df["Customers"],
                marker_color=ACCENT,
                marker_line_width=0,
                hovertemplate="%{x}<br>Customers acquired: %{y:,}<extra></extra>",
            )
        )
        fig.update_layout(
            template="cba",
            title="Number of Customers Acquired Each Quarter",
            width=width,
            height=height,
            bargap=0.25,
        )
        fig.update_xaxes(type="category", tickangle=-45)
        fig.update_yaxes(title="Customers Acquired", tickformat=",.0f")
        return fig

    _quarterly_acquisitions_chart(quarterly_cohort_sizes)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Every Q4 dwarfs the three quarters before it. Q4 2019 alone acquires 8,601
    customers — nearly as many as Q1, Q2 and Q3 2019 combined (3,485 + 3,023 +
    3,208 = 9,716) — and each year's Q4 bar sits above the Q4 bar before it.
    Acquisition itself is seasonal, and it is growing. This is the source
    figure for both charts above: it is the diagonal that the profit-by-cohort
    stack builds on, and the reason Figure 6.11's profit line spikes hardest
    exactly where new customers arrive fastest.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Appendix
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

    The intersection area of two circles a distance $d$ (centre-to-centre distance) apart is
    (ref: [circle-circle intersection](https://mathworld.wolfram.com/Circle-CircleIntersection.html)):

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
