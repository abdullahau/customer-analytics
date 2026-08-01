import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 📊 Learn & Practice Plotly

    An interactive, self-contained tour of **Plotly** — from the first scatter plot to
    animations, subplots, and reactive selection inside marimo.

    **How to use this notebook**

    - Each section has **worked examples** you can read and edit, followed by
      **✏️ Your turn** practice cells with a `# TODO`.
    - Every practice has a **💡 Show solution** accordion below it — try first, peek if stuck.
    - Because marimo is *reactive*, editing any cell re-runs everything that depends on it.
      Change a color, a column, a parameter — watch the figure update instantly.

    **The two Plotly APIs you'll meet**

    | API | Import | When to use |
    |---|---|---|
    | **Plotly Express** | `import plotly.express as px` | High-level, one-liner charts from a dataframe. Start here. |
    | **Graph Objects** | `import plotly.graph_objects as go` | Low-level, full control — build a figure trace-by-trace. |

    `px` builds `go.Figure` objects under the hood, so you can always start with `px`
    and then reach into `fig.update_*()` for fine control. Best of both worlds.
    """)
    return


@app.cell
def _():
    import marimo as mo

    import numpy as np
    import pandas as pd

    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots

    rng = np.random.default_rng(42)
    return go, make_subplots, mo, np, pd, pio, px


@app.cell
def _(px):
    # Bundled sample datasets (ship with plotly, work offline)
    iris = px.data.iris()  # 150 flowers: sepal/petal measurements + species
    tips = (
        px.data.tips()
    )  # 244 restaurant bills: total_bill, tip, day, time, size (number of diners)
    gapminder = px.data.gapminder()  # country-year: lifeExp, pop, gdpPercap, continent
    stocks = px.data.stocks()  # normalized daily prices for 6 tech stocks
    return gapminder, iris, stocks, tips


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1 · Plotly Express basics

    `px` functions all follow the same shape: `px.<kind>(dataframe, x=..., y=..., color=...)`.
    The dataframe is *tidy* (one row per observation); you map **columns → visual channels**
    (x, y, color, size, symbol, facet). Below are the five you'll use most.
    """)
    return


@app.cell
def _(tips):
    # review tips head
    tips.head()
    return


@app.cell
def _(px, tips):
    # SCATTER — map columns to x, y, and color; size encodes a third number
    _fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        color="time",  # categorical → discrete colors
        size="size",  # party size → marker area
        hover_data=["day"],  # extra fields shown on hover
        title="Tips vs total bill",
    )
    _fig
    return


@app.cell
def _(stocks):
    stocks.head()
    return


@app.cell
def _(px, stocks):
    # LINE — great for time series; `y` can be a list of columns
    _fig = px.line(
        stocks,
        x="date",
        y=["GOOG", "AAPL", "AMZN"],
        title="Normalized stock prices",
        labels={"value": "price (indexed to 1.0)", "variable": "ticker"},
    )
    _fig
    return


@app.cell
def _(gapminder):
    gapminder.query("year == 2007").groupby("continent", as_index=False)[
        "lifeExp"
    ].mean().sort_values("lifeExp")
    return


@app.cell
def _(gapminder, px):
    # BAR — aggregate first, then plot. Here: mean life expectancy by continent in 2007
    _d = (
        gapminder.query("year == 2007")
        .groupby("continent", as_index=False)["lifeExp"]
        .mean()
        .sort_values("lifeExp")
    )
    _fig = px.bar(
        _d,
        x="lifeExp",
        y="continent",
        orientation="h",
        color="lifeExp",
        color_continuous_scale="Viridis",
        title="Mean life expectancy by continent (2007)",
    )
    _fig
    return


@app.cell
def _(px, tips):
    # HISTOGRAM & BOX — distributions. `marginal` adds a mini-distribution on the axis
    _fig = px.histogram(
        tips,
        x="total_bill",
        color="sex",
        nbins=30,
        marginal="box",
        barmode="overlay",
        opacity=0.7,
        title="Distribution of total bill by sex",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 1

    Using the `iris` dataframe, make a **scatter plot** of `sepal_width` (x) vs
    `sepal_length` (y), colored by `species`, with the marker **symbol** also varying
    by `species`. Give it a title.

    *Hint:* `px.scatter(..., symbol=...)`.
    """)
    return


@app.cell
def _(iris):
    iris.head()
    return


@app.cell
def _(iris, px):
    # TODO: your scatter here (replace this figure)
    _fig = px.scatter(
        iris,
        x="sepal_width",
        y="sepal_length",
        color="species",
        symbol="species",
        title="Iris sepal shape by species",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 1": mo.md(
                r"""
                ```python
                px.scatter(
                    iris,
                    x="sepal_width",
                    y="sepal_length",
                    color="species",
                    symbol="species",
                    title="Iris sepal shape by species",
                )
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 2

    Make a **box plot** (`px.box`) of `tip` grouped by `day`, colored by `smoker`.
    Then add `points="all"` to overlay the raw observations.

    *Hint:* boxes side-by-side by color is automatic when you pass `color=`.
    """)
    return


@app.cell
def _(px, tips):
    # TODO: your box plot here
    _fig = px.box(
        tips,
        x="day",
        y="tip",
        color="smoker",
        points="all",
        title="Tip distribution by day and smoker status",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 2": mo.md(
                r"""
                ```python
                px.box(
                    tips, x="day", y="tip", color="smoker",
                    points="all",
                    title="Tip distribution by day and smoker status",
                )
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2 · Faceting — small multiples for free

    Pass `facet_col` / `facet_row` and `px` splits the data into a grid of subplots
    sharing axes. This is one of `px`'s superpowers — a faceted view is a one-word change.
    """)
    return


@app.cell
def _(gapminder, px):
    _fig = px.scatter(
        gapminder.query("year == 2007"),
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        facet_col="continent",
        facet_col_wrap=3,
        log_x=True,
        size_max=45,
        title="Wealth vs health, 2007 — one panel per continent",
    )
    _fig.update_layout(showlegend=False)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 3

    From `tips`, draw a histogram of `total_bill` **faceted by `time`** (Lunch/Dinner)
    as two rows (`facet_row="time"`), colored by `sex`.
    """)
    return


@app.cell
def _(px, tips):
    # TODO: faceted histogram here
    _fig = px.histogram(
        tips,
        x="total_bill",
        color="sex",
        facet_row="time",
        nbins=30,
        barmode="overlay",
        opacity=0.7,
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 3": mo.md(
                r"""
                ```python
                px.histogram(
                    tips, x="total_bill", color="sex",
                    facet_row="time", nbins=30, barmode="overlay", opacity=0.7,
                )
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3 · Customizing the layout

    Every `px` figure is a `go.Figure` you can refine. The three workhorses:

    - `fig.update_layout(...)` — title, size, legend, margins, template, fonts.
    - `fig.update_xaxes(...)` / `fig.update_yaxes(...)` — ranges, ticks, gridlines, titles.
    - `fig.update_traces(...)` — marker/line styling applied to matching traces.

    **Templates** set the whole look at once: `"plotly"`, `"plotly_white"`,
    `"plotly_dark"`, `"simple_white"`, `"ggplot2"`, `"seaborn"`, `"presentation"`.
    """)
    return


@app.cell
def _(px, stocks):
    _fig = px.line(stocks, x="date", y="GOOG", title="Styling a figure")
    _fig.update_traces(line=dict(width=3, color="#7c3aed"))
    _fig.update_layout(
        template="plotly_white",
        title=dict(x=0.5, font=dict(size=22)),
        font=dict(family="Georgia, serif", size=14),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=70, b=50),
        width=760,
        height=420,
    )
    _fig.update_yaxes(title_text="indexed price", tickformat=".0%", gridcolor="#eee")
    _fig.update_xaxes(title_text="", showgrid=False)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 4

    Take a `px.scatter` of `iris` (`petal_length` vs `petal_width`, colored by species) and:

    1. apply the `"simple_white"` template,
    2. center the title,
    3. move the legend to the **bottom**, laid out horizontally,
    4. make markers size 10 with a thin black outline.

    *Hints:* `legend=dict(orientation="h", yanchor="bottom", y=1.02)`;
    `update_traces(marker=dict(size=10, line=dict(width=1, color="black")))`.
    """)
    return


@app.cell
def _(iris, px):
    # TODO: build and style the figure
    _fig = px.scatter(
        iris,
        x="petal_length",
        y="petal_width",
        color="species",
        title="Petal Length vs Petal Width, Colored by Species",
    )
    _fig.update_traces(marker=dict(size=10, line=dict(width=1, color="black")))
    _fig.update_layout(
        template="simple_white",
        title=dict(x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 4": mo.md(
                r"""
                ```python
                fig = px.scatter(
                    iris, x="petal_length", y="petal_width", color="species",
                    title="Iris petals",
                )
                fig.update_traces(marker=dict(size=10, line=dict(width=1, color="black")))
                fig.update_layout(
                    template="simple_white",
                    title=dict(x=0.5),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                )
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4 · Graph Objects — building a figure by hand

    When you outgrow `px`, drop to `go`. The pattern is always:

    1. `fig = go.Figure()`
    2. `fig.add_trace(go.Scatter(...))` — one call per series,
    3. `fig.update_layout(...)`.

    Common trace types: `go.Scatter` (lines **and** markers via `mode=`),
    `go.Bar`, `go.Histogram`, `go.Box`, `go.Heatmap`, `go.Surface`, `go.Scatter3d`.
    """)
    return


@app.cell
def _(go, np):
    _x = np.linspace(0, 4 * np.pi, 200)

    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_x, y=np.sin(_x), mode="lines", name="sin"))
    _fig.add_trace(
        go.Scatter(
            x=_x,
            y=np.cos(_x),
            mode="lines",
            name="cos",
            line=dict(dash="dash"),
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=_x,
            y=np.sin(_x) * np.cos(_x),
            mode="lines",
            name="sin·cos",
            fill="tozeroy",
            opacity=0.3,
        )
    )
    _fig.update_layout(
        title="Three traces, built by hand",
        template="plotly_white",
        legend=dict(orientation="h", y=1.05),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 5

    Using **graph objects only** (no `px`), recreate a grouped bar chart:

    - categories on x: `["Q1", "Q2", "Q3", "Q4"]`
    - two bar traces: `revenue = [10, 14, 12, 18]` and `cost = [7, 9, 8, 11]`
    - set `barmode="group"` and give each trace a `name`.

    *Hint:* two `fig.add_trace(go.Bar(x=..., y=..., name=...))` calls.
    """)
    return


@app.cell
def _(go):
    # TODO: build the grouped bar chart with go
    _x = ["Q1", "Q2", "Q3", "Q4"]
    _revenue = [10, 14, 12, 18]
    _cost = [7, 9, 8, 11]
    _fig = go.Figure()
    _fig.add_trace(go.Bar(x=_x, y=_revenue, name="Revenue"))
    _fig.add_trace(go.Bar(x=_x, y=_cost, name="Cost"))
    _fig.update_layout(
        title="Revenue & Costs, by Quarter", barmode="group", template="simple_white"
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 5": mo.md(
                r"""
                ```python
                q = ["Q1", "Q2", "Q3", "Q4"]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=q, y=[10, 14, 12, 18], name="revenue"))
                fig.add_trace(go.Bar(x=q, y=[7, 9, 8, 11], name="cost"))
                fig.update_layout(barmode="group", title="Revenue vs cost", template="plotly_white")
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5 · Subplots & secondary axes

    `make_subplots` gives you a grid you fill with `fig.add_trace(..., row=r, col=c)`.
    Pass `specs=[[{"secondary_y": True}]]` to overlay two different y-scales in one panel.
    """)
    return


@app.cell
def _(gapminder, go, make_subplots):
    _fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Population (log)", "Life expectancy"),
    )
    _asia = gapminder.query("country == 'India'")
    _fig.add_trace(go.Scatter(x=_asia.year, y=_asia["pop"], name="pop"), row=1, col=1)
    _fig.add_trace(
        go.Scatter(x=_asia.year, y=_asia.lifeExp, name="lifeExp"), row=1, col=2
    )
    _fig.update_yaxes(type="log", row=1, col=1)
    _fig.update_layout(
        title="India over time", template="plotly_white", showlegend=False
    )
    _fig
    return


@app.cell
def _(gapminder, go, make_subplots):
    # SECONDARY Y-AXIS — two scales, one panel
    _fig = make_subplots(specs=[[{"secondary_y": True}]])
    _ind = gapminder.query("country == 'India'")
    _fig.add_trace(
        go.Bar(x=_ind.year, y=_ind["pop"], name="population", opacity=0.5),
        secondary_y=False,
    )
    _fig.add_trace(
        go.Scatter(
            x=_ind.year, y=_ind.gdpPercap, name="GDP per capita", line=dict(width=3)
        ),
        secondary_y=True,
    )
    _fig.update_yaxes(title_text="population", secondary_y=False)
    _fig.update_yaxes(title_text="GDP per capita", secondary_y=True)
    _fig.update_layout(
        title="Population vs GDP/capita — dual axis", template="plotly_white"
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 6

    Build a **1×2 subplot**. Left panel: histogram of `tips.total_bill`.
    Right panel: histogram of `tips.tip`. Add `subplot_titles`.

    *Hint:* `make_subplots(rows=1, cols=2, subplot_titles=(...))` then two
    `add_trace(go.Histogram(x=...), row=1, col=n)`.
    """)
    return


@app.cell
def _(go, make_subplots, tips):
    # TODO: two-panel histogram subplot
    _fig = make_subplots(rows=1, cols=2, subplot_titles=("Total Bill", "Tips"))
    _fig.add_trace(go.Histogram(x=tips.total_bill, name="Total Bill"), row=1, col=1)
    _fig.add_trace(go.Histogram(x=tips.tip, name="Tips"), row=1, col=2)
    _fig.update_layout(template="plotly_white", showlegend=False)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 6": mo.md(
                r"""
                ```python
                fig = make_subplots(rows=1, cols=2, subplot_titles=("total_bill", "tip"))
                fig.add_trace(go.Histogram(x=tips.total_bill, name="total_bill"), row=1, col=1)
                fig.add_trace(go.Histogram(x=tips.tip, name="tip"), row=1, col=2)
                fig.update_layout(template="plotly_white", showlegend=False)
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6 · Heatmaps & 3D

    - **Heatmap**: `px.imshow(matrix)` or `go.Heatmap(z=...)` — correlation matrices,
      density grids, images.
    - **3D**: `go.Surface(z=...)` for surfaces, `px.scatter_3d` / `go.Scatter3d` for
      point clouds. Drag to rotate in the browser.
    """)
    return


@app.cell
def _(iris, px):
    # Correlation heatmap with annotated cells
    _corr = iris.drop(columns=["species", "species_id"]).corr().round(2)
    _fig = px.imshow(
        _corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        title="Iris feature correlations",
    )
    _fig
    return


@app.cell
def _(go, np):
    # A 3D surface: z = sin(sqrt(x^2 + y^2))
    _t = np.linspace(-6, 6, 120)
    _xx, _yy = np.meshgrid(_t, _t)
    _zz = np.sin(np.sqrt(_xx**2 + _yy**2))
    _fig = go.Figure(go.Surface(z=_zz, x=_t, y=_t, colorscale="Viridis"))
    _fig.update_layout(
        title="z = sin(√(x²+y²))",
        height=520,
        scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"),
        template="simple_white",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 7

    Make a **3D scatter** of `iris` with `px.scatter_3d`: `sepal_length`,
    `sepal_width`, `petal_length` on the three axes, colored by `species`.
    Rotate it once it renders.
    """)
    return


@app.cell
def _(iris, px):
    # TODO: 3D scatter here
    _fig = px.scatter_3d(
        iris,
        x="sepal_length",
        y="sepal_width",
        z="petal_length",
        color="species",
        title="Iris in 3D",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 7": mo.md(
                r"""
                ```python
                px.scatter_3d(
                    iris, x="sepal_length", y="sepal_width", z="petal_length",
                    color="species", title="Iris in 3D",
                )
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7 · Annotations, shapes & reference lines

    Draw attention with `fig.add_hline` / `add_vline` (with optional
    `annotation_text`), shade regions with `add_hrect` / `add_vrect`, and place free
    text with `fig.add_annotation(x, y, text, showarrow=True, arrowhead=...)`.
    """)
    return


@app.cell
def _(px, tips):
    _mean_tip = tips.tip.mean()
    _fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        opacity=0.6,
        title="Reference lines & annotations",
        template="simple_white",
    )
    _fig.add_hline(
        y=_mean_tip,
        line_dash="dash",
        line_color="red",
        opacity=1,
        line_width=2,
        annotation_text=f"mean tip = ${_mean_tip:.2f}",
        annotation_position="top left",
    )
    _fig.add_vrect(
        x0=40,
        x1=55,
        fillcolor="orange",
        opacity=0.12,
        line_width=0,
        annotation_text="big spenders",
        annotation_position="top",
    )
    _fig.add_annotation(
        x=50.81, y=10, text="largest tip", showarrow=True, arrowhead=2, ax=30, ay=40
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 8

    On a `px.line` of `stocks` `AAPL` over `date`:

    1. add a horizontal line at `y=1.0` (the indexing baseline), dashed and gray,
    2. add a vertical rectangle shading the year **2019** (`x0="2019-01-01"`,
       `x1="2019-12-31"`) faintly.
    """)
    return


@app.cell
def _(px, stocks):
    # TODO: add the hline and vrect
    _fig = px.line(stocks, x="date", y="AAPL", template="simple_white")
    _fig.add_hline(y=1, opacity=1, line_width=2, line_dash="dash", line_color="gray")
    _fig.add_vrect(
        x0="2019-01-01",
        x1="2019-12-31",
        fillcolor="gray",
        opacity=0.2,
        annotation_text="2019",
        annotation_position="top",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 8": mo.md(
                r"""
                ```python
                fig = px.line(stocks, x="date", y="AAPL", title="AAPL")
                fig.add_hline(y=1.0, line_dash="dash", line_color="gray")
                fig.add_vrect(x0="2019-01-01", x1="2019-12-31",
                              fillcolor="steelblue", opacity=0.12, line_width=0,
                              annotation_text="2019")
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8 · Custom hover templates

    Default hovers are decent; `hovertemplate` makes them exact. Reference data with
    `%{x}`, `%{y}`, `%{marker.size}`, and pull extra columns via `customdata` +
    `%{customdata[0]}`. End with `<extra></extra>` to hide the trace-name box.
    """)
    return


@app.cell
def _(gapminder, px):
    _d = gapminder.query("year == 2007")
    _fig = px.scatter(
        _d,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        log_x=True,
        size_max=55,
        custom_data=["country", "pop"],
        title="Custom hover — 2007",
    )
    _fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "GDP/capita: $%{x:,.0f}<br>"
            "Life expectancy: %{y:.1f} yrs<br>"
            "Population: %{customdata[1]:,.0f}"
            "<extra></extra>"
        )
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 9

    On a `px.scatter` of `tips` (`total_bill` vs `tip`), write a `hovertemplate` that
    shows: `Bill: $<total_bill>`, `Tip: $<tip>`, and the `day` (via `custom_data=["day"]`
    and `%{customdata[0]}`). Hide the extra box with `<extra></extra>`.
    """)
    return


@app.cell
def _(px, tips):
    # TODO: custom hovertemplate
    _fig = px.scatter(tips, x="total_bill", y="tip", custom_data=["day"])
    _fig.update_traces(
        hovertemplate=(
            "Bill: %{x:,.2f}<br>Tip: %{y:,.2f}<br>Day: %{customdata[0]}<extra></extra>"
        )
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 9": mo.md(
                r"""
                ```python
                fig = px.scatter(tips, x="total_bill", y="tip", custom_data=["day"])
                fig.update_traces(
                    hovertemplate=(
                        "Bill: $%{x:.2f}<br>Tip: $%{y:.2f}<br>Day: %{customdata[0]}<extra></extra>"
                    )
                )
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 9 · Animation

    `px` animates with `animation_frame` (the time/step variable) and optional
    `animation_group` (which mark is "the same" across frames). Fix the axis ranges
    so the view doesn't jump between frames. Press ▶ to play.
    """)
    return


@app.cell
def _(gapminder, px):
    _fig = px.scatter(
        gapminder,
        x="gdpPercap",
        y="lifeExp",
        animation_frame="year",
        animation_group="country",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=55,
        range_x=[200, 100000],
        range_y=[25, 90],
        title="Gapminder — the Hans Rosling classic",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 10

    Animate a **bar chart** of `gapminder` mean `lifeExp` per continent, one frame per
    `year`. Fix `range_y=[0, 90]` so bars are comparable across frames.

    *Hint:* pre-aggregate to `year, continent, lifeExp`, then
    `px.bar(..., animation_frame="year", range_y=[0, 90])`.
    """)
    return


@app.cell
def _(gapminder, px):
    # TODO: animated bar chart
    _agg = gapminder.groupby(["year", "continent"], as_index=False)["lifeExp"].mean()
    _fig = px.bar(
        _agg,
        x="continent",
        y="lifeExp",
        color="continent",
        range_y=[0, 90],
        animation_frame="year",
        animation_group="continent",
        title="Mean life expectancy by continent, animated",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 10": mo.md(
                r"""
                ```python
                agg = gapminder.groupby(["year", "continent"], as_index=False)["lifeExp"].mean()
                px.bar(
                    agg, x="continent", y="lifeExp", color="continent",
                    animation_frame="year", range_y=[0, 90],
                    title="Mean life expectancy by continent, animated",
                )
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 10 · Interactive Plotly *inside marimo* 🔌

    This is where marimo shines. Wrap any figure in **`mo.ui.plotly(fig)`** and marimo
    turns box/lasso selection into a reactive Python value. Select points in the chart
    below — the table and summary underneath **update automatically**, no callbacks.

    > Use the **box-** or **lasso-select** tools in the modebar (top-right of the chart),
    > then drag over some points.
    """)
    return


@app.cell
def _(mo, px, tips):
    _fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        color="day",
        title="Select points → drives the cells below",
    )
    _fig.update_layout(dragmode="select")
    selection = mo.ui.plotly(_fig)
    selection
    return (selection,)


@app.cell
def _(mo, pd, selection):
    _pts = selection.value  # list of dicts for the selected points
    if _pts:
        _df = pd.DataFrame(_pts)
        _msg = mo.md(
            f"**{len(_df)}** points selected — "
            f"mean bill **\\${_df['x'].mean():.2f}**, mean tip **\\${_df['y'].mean():.2f}**."
        )
        _out = mo.vstack([_msg, mo.ui.table(_df[["x", "y"]].round(2), page_size=5)])
    else:
        _out = mo.md("*No selection yet — box/lasso-select some points above.*")
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 11

    Build your own reactive selector: a `mo.ui.plotly` scatter of `iris`
    (`petal_length` vs `petal_width`), and a cell below that reports **how many of each
    species** are in the current selection.

    *Hint:* pass `hover_data=["species"]` so the species column rides along in `selection.value`,
    then `pd.DataFrame(sel.value)["species"]` to count.
    """)
    return


@app.cell
def _(iris, mo, px):
    # TODO: make an mo.ui.plotly selector over iris
    _fig = px.scatter(
        iris, x="petal_length", y="petal_width", color="species", hover_data=["species"]
    )
    _fig.update_layout(dragmode="select")
    my_selection = mo.ui.plotly(_fig)
    my_selection
    return (my_selection,)


@app.cell
def _(mo, my_selection, pd):
    # TODO: count species in my_selection.value
    _pts = my_selection.value
    _out = mo.md("*Select some points above to see the species breakdown.*")
    if _pts:
        _df = pd.DataFrame(_pts)
        if "species" in _df.columns:
            _counts = (
                _df["species"]
                .value_counts()
                .rename_axis("species")
                .reset_index(name="count")
            )
            _out = mo.vstack(
                [
                    mo.md(f"**{len(_df)} points selected**"),
                    mo.ui.table(_counts, selection=None),
                ]
            )
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 11": mo.md(
                r"""
                The scaffold above *is* the solution — the key ideas are:

                1. `hover_data=["species"]` makes each selected point carry its species
                   in `selection.value[i]["species"]`.
                2. `dragmode="select"` starts the chart in box-select mode.
                3. The downstream cell reads `my_selection.value`, rebuilds a DataFrame, and
                   `value_counts()` the species — and because marimo is reactive, it recomputes
                   every time your selection changes.

                Try switching the count to a small `px.bar` of the counts instead of a table.
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 11 · Themes & templates — colors, background, fonts

    A **template** is a reusable `go.layout.Template` that bundles *every* styling
    default — fonts, background colors, the categorical color cycle, axis look — so you
    set the whole appearance with one word instead of repeating `update_layout` calls.

    **Built-ins** (recap): `"plotly"`, `"plotly_white"`, `"plotly_dark"`,
    `"simple_white"`, `"ggplot2"`, `"seaborn"`, `"presentation"`, `"none"`.

    **Combine with `+`** — layer a base look and your tweaks: `template="plotly_white+mytheme"`.
    The pieces on the right win, so your theme overrides the base.

    Anatomy of the properties you'll set most:

    | Property (`layout.…`) | Controls |
    |---|---|
    | `font` | global family / size / color for all text |
    | `title.font`, `legend.font`, `hoverlabel.font` | per-element fonts |
    | `paper_bgcolor` | color *around* the plot (the whole card) |
    | `plot_bgcolor` | color of the **plotting area** only |
    | `colorway` | the categorical color cycle (discrete series) |
    | `colorscale` / trace `colorscale=` | the continuous gradient |
    | `hoverlabel` | tooltip background / border / font |
    """)
    return


@app.cell
def _(go, pio):
    # CREATE & REGISTER a custom template, then make it the default look
    pio.templates["practice_theme"] = go.layout.Template(
        layout=dict(
            font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#2b303a"),
            title=dict(x=0.5, font=dict(size=20)),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f6f8fa",
            colorway=["#2563eb", "#16a34a", "#dc2626", "#d97706", "#7c3aed", "#0891b2"],
            hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#c3c9d0"),
            xaxis=dict(
                gridcolor="#e6e8eb",
                zeroline=False,
                showline=True,
                linecolor="#c3c9d0",
                ticks="outside",
            ),
            yaxis=dict(
                gridcolor="#e6e8eb",
                zeroline=False,
                showline=True,
                linecolor="#c3c9d0",
                ticks="outside",
            ),
        )
    )
    # Make it the global default for THIS notebook (applies to every bare figure):
    pio.templates.default = "plotly_white+practice_theme"

    theme_name = "practice_theme"  # returned so downstream cells depend on this cell
    theme_name
    return (theme_name,)


@app.cell
def _(px, stocks, theme_name):
    # Use the theme explicitly (or rely on pio.templates.default set above)
    _fig = px.line(
        stocks,
        x="date",
        y=["GOOG", "AAPL", "AMZN"],
        template=f"plotly_white+{theme_name}",
        title="Same data, custom theme",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Editing an existing template** instead of writing one from scratch — copy it so you
    don't mutate the shared original, tweak, re-register:

    ```python
    import copy
    t = copy.deepcopy(pio.templates["plotly_dark"])
    t.layout.font.family = "JetBrains Mono, monospace"
    t.layout.colorway = ["#22d3ee", "#f472b6", "#a3e635"]
    pio.templates["my_dark"] = t
    ```

    > **marimo tip:** `pio.templates[...] = ...` and `pio.templates.default = ...` are
    > *global side effects*, not marimo variables — the reactive graph can't see them. Have
    > the cell that registers a theme **return a value** (here `theme_name`) and reference
    > it downstream, so those cells run *after* registration.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎛️ Playground — `pio.templates.default` (global) vs `template=` (per-figure)

    Two ways to apply a theme, and it's worth *feeling* the difference:

    - **Global** — `pio.templates.default = "…"` sets the look for **every figure created
      afterwards that doesn't ask for a specific template**. One setting, whole notebook.
    - **Per-figure** — `px.<kind>(..., template="…")` (or `fig.update_layout(template="…")`)
      themes **just that figure** and **overrides** the global default.

    The two dropdowns below are live. The options come from `sorted(pio.templates)` — the
    built-ins plus the `practice_theme` you registered above — with a few `base+overlay`
    combos added.
    """)
    return


@app.cell
def _(pio, theme_name):
    # Option list = every registered template + a few useful combinations
    template_options = sorted(pio.templates) + [
        f"plotly_white+{theme_name}",
        f"plotly_dark+{theme_name}",
    ]
    return (template_options,)


@app.cell
def _(mo, template_options):
    global_default = mo.ui.dropdown(
        options=template_options,
        value="plotly_white",
        label="🌍 Global: `pio.templates.default` →",
    )
    global_default
    return (global_default,)


@app.cell
def _(gapminder, global_default, mo, pio, px):
    # Set the GLOBAL default, then build a figure with NO template= → it inherits the default.
    pio.templates.default = global_default.value

    _d = gapminder.query("year == 2007")
    _fig = px.scatter(
        _d,
        x="gdpPercap",
        y="lifeExp",
        color="continent",
        log_x=True,
        size="pop",
        size_max=45,
        title="No template= set → inherits the global default",
    )
    mo.vstack(
        [
            mo.md(
                f"Active default: **`{global_default.value}`**. This figure passes **no** "
                "`template=`, so it takes whatever the dropdown sets. Change it and watch."
            ),
            _fig,
        ]
    )
    return


@app.cell
def _(mo, template_options):
    per_fig_default = mo.ui.dropdown(
        options=template_options,
        value="ggplot2",
        label="🎯 Per-figure: `template=` →",
    )
    per_fig_default
    return (per_fig_default,)


@app.cell
def _(iris, mo, per_fig_default, px):
    # Explicit template= on THIS figure — overrides the global default, whatever it is.
    _fig = px.scatter(
        iris,
        x="sepal_width",
        y="sepal_length",
        color="species",
        template=per_fig_default.value,
        title=f"template={per_fig_default.value!r} — overrides the global default",
    )
    mo.vstack(
        [
            mo.md(
                "This figure sets `template=` explicitly, so the **global dropdown above has "
                "no effect on it** — per-figure always wins."
            ),
            _fig,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Reactivity note (marimo):** changing the global dropdown re-runs only the cells
    > that *read* `global_default` — so the figure directly above updates, but the other
    > example charts elsewhere in the notebook keep the template they were **built with**
    > (they don't depend on the dropdown, so they don't re-run). That mirrors real Plotly:
    > `pio.templates.default` only affects figures **created after** it's set. To reset,
    > pick `"plotly"` (or `"plotly_white+practice_theme"`) in the global dropdown.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 12

    Register a template named `"night"` with: a dark `paper_bgcolor` (`"#111827"`) and
    `plot_bgcolor` (`"#0b1220"`), off-white font (`"#e5e7eb"`), a 3-color `colorway`, and
    faint grid lines (`gridcolor="#334155"`). Then draw any `px` chart with
    `template="night"`.
    """)
    return


@app.cell
def _(go, pio, px, tips):
    # TODO: register the "night" template, then plot with it
    pio.templates["night"] = go.layout.Template(
        layout=dict(
            font=dict(color="#e5e7eb"),
            paper_bgcolor="#111827",
            plot_bgcolor="#0b1220",
            colorway=["#38bdf8", "#f472b6", "#a3e635"],
            xaxis=dict(gridcolor="#334155", zeroline=False),
            yaxis=dict(gridcolor="#334155", zeroline=False),
        )
    )

    _fig = px.scatter(tips, x="total_bill", y="tip", color="sex", template="night")
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 12": mo.md(
                r"""
                ```python
                pio.templates["night"] = go.layout.Template(layout=dict(
                    paper_bgcolor="#111827", plot_bgcolor="#0b1220",
                    font=dict(color="#e5e7eb"),
                    colorway=["#38bdf8", "#f472b6", "#a3e635"],
                    xaxis=dict(gridcolor="#334155", zeroline=False),
                    yaxis=dict(gridcolor="#334155", zeroline=False),
                ))
                px.scatter(tips, x="total_bill", y="tip", color="sex", template="night")
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 12 · Axes & grids in depth

    **Grids.** Toggle and style per axis with `update_xaxes` / `update_yaxes`:

    - turn off: `showgrid=False`
    - color / weight / style: `gridcolor="#e5e7eb"`, `gridwidth=1`, `griddash="dot"`
    - the line at 0: `zeroline=True/False`, `zerolinecolor`, `zerolinewidth`
    - *minor* gridlines: `minor=dict(showgrid=True, gridcolor="#f1f5f9")`

    **Axes.** The knobs you'll reach for:

    | Goal | Property |
    |---|---|
    | title | `title_text="…"` (or `title=dict(text=…, font=…)`) |
    | fixed range | `range=[lo, hi]` |
    | log / date / category | `type="log" / "date" / "category"` |
    | number/date format | `tickformat=".0%"`, `",.0f"`, `"%b %Y"` |
    | rotate labels | `tickangle=-45` |
    | custom ticks | `tickvals=[…]`, `ticktext=[…]`, or `nticks=6`, `dtick=10` |
    | tick marks | `ticks="outside"`, `ticklen=6`, `tickcolor` |
    | axis line | `showline=True`, `linecolor`, `linewidth`, `mirror=True` |
    | hover spike line | `showspikes=True`, `spikemode="across"` |
    """)
    return


@app.cell
def _(px, stocks):
    _fig = px.line(stocks, x="date", y="MSFT", title="Fully dressed axes")
    # y-axis: percent ticks, dotted grid, no zero line, minor grid
    _fig.update_yaxes(
        title_text="indexed price",
        tickformat=".0%",
        showgrid=True,
        gridcolor="#e5e7eb",
        griddash="dot",
        zeroline=False,
        minor=dict(showgrid=True, gridcolor="#f3f4f6"),
        showline=True,
        linecolor="#9ca3af",
        ticks="outside",
    )
    # x-axis: no grid, month-year labels, angled, solid axis line
    _fig.update_xaxes(
        title_text="",
        showgrid=False,
        tickformat="%b %Y",
        tickangle=-30,
        showline=True,
        linecolor="#9ca3af",
        mirror=False,
    )
    _fig.update_layout(template="plotly_white")
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 13

    On a `px.bar` of `tips` mean `tip` by `day`:

    1. **remove the y grid entirely** (`showgrid=False`) but keep a solid y axis line,
    2. format y ticks as currency (`tickformat="$.2f"`),
    3. force the x order Thur→Fri→Sat→Sun with
       `categoryorder="array", categoryarray=[...]`,
    4. angle the x tick labels by `-30°`.
    """)
    return


@app.cell
def _(px, tips):
    # TODO: aggregate then style the axes/grids
    _d = tips.groupby("day", as_index=False)["tip"].mean()
    _fig = px.bar(
        _d, x="day", y="tip", template="plotly_white", title="Mean tip by day"
    )
    _fig.update_yaxes(
        title_text="Tip",
        showgrid=False,
        showline=True,
        linecolor="#9ca3af",
        tickformat="$.2f",
        ticks="outside",
    )
    _fig.update_xaxes(
        title_text="",
        categoryorder="array",
        categoryarray=["Thur", "Fri", "Sat", "Sun"],
        tickangle=-30,
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 13": mo.md(
                r"""
                ```python
                d = tips.groupby("day", as_index=False)["tip"].mean()
                fig = px.bar(d, x="day", y="tip", template="plotly_white", title="Mean tip by day")
                fig.update_yaxes(showgrid=False, showline=True, linecolor="#9ca3af",
                                 tickformat="$.2f", ticks="outside")
                fig.update_xaxes(categoryorder="array",
                                 categoryarray=["Thur", "Fri", "Sat", "Sun"], tickangle=-30)
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 13 · Controlling interactivity — modebar, zoom, hover, selection

    Plotly interactivity is set in **two independent layers**:

    1. **Layout-baked** (lives in the figure JSON → works for *both* a bare returned
       figure and `mo.ui.plotly`, regardless of anything else):
       - `dragmode` — what a click-drag *does*: `"select"`, `"lasso"`, `"zoom"`, `"pan"`, or `False`.
       - `xaxis.fixedrange=True` / `yaxis.fixedrange=True` — **lock the axis**: kills
         drag-zoom, scroll/pinch-zoom, *and* pan on that axis, while leaving **hover
         tooltips and box/lasso selection fully working**.
       - `modebar_remove=[...]` / `modebar_add=[...]` — which toolbar buttons exist.
    2. **Render config** (the `config` dict — the modebar toolbar & scroll behavior):
       - `displayModeBar`: `True` / `False` / `"hover"`.
       - `scrollZoom`: `False` disables wheel/pinch zoom over the plot.
       - `modeBarButtonsToRemove` / `modeBarButtonsToAdd`, `displaylogo=False`.
       - ⚠️ `staticPlot=True` disables **everything including hover** — do *not* use it here.

    ### 🎯 Your exact goal — keep only hover-tooltip + select/highlight

    Kill pinch/scroll zoom, pan, the zoom/screenshot/reset buttons — keep tooltips and
    selection. Use **both layers**:

    ```python
    fig.update_layout(dragmode="select")          # drag = box-select (use "lasso" for freehand)
    fig.update_xaxes(fixedrange=True)             # no zoom / pan / pinch on x
    fig.update_yaxes(fixedrange=True)             # no zoom / pan / pinch on y

    lockdown = {                                  # the render config
        "displayModeBar": False,                  # hide the whole toolbar…
        "scrollZoom": False,                      # …and the mouse-wheel / pinch zoom
    }
    ```

    **Applying the config depends on how you render:**

    - **Reactive (recommended, gives you `.value`):** `mo.ui.plotly(fig, config=lockdown)`
    - **Bare figure returned as the cell output:** it uses the *renderer's* default config,
      so either call `fig.show(config=lockdown)` or set it globally once:
      `pio.renderers["browser"].config = lockdown` (or whatever `pio.renderers.default` is).

    **Prefer to keep the toolbar but drop only zoom/pan/screenshot** (leaving the
    select & lasso buttons so users can switch tools)? Do it in either layer:

    ```python
    # layout-baked — travels with the figure:
    fig.update_layout(modebar_remove=["zoom", "pan", "zoomin", "zoomout",
                                      "autoscale", "resetscale", "toimage"])
    # …or render config — keeps select2d + lasso2d, removes the rest:
    cfg = {"displaylogo": False, "scrollZoom": False,
           "modeBarButtonsToRemove": ["zoom2d", "pan2d", "zoomIn2d", "zoomOut2d",
                                      "autoScale2d", "resetScale2d", "toImage"]}
    ```

    The live chart below is fully locked down — **hover for tooltips, drag to select &
    highlight; there is no zoom, no pan, and no toolbar.**
    """)
    return


@app.cell
def _(mo, px, tips):
    _fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        color="day",
        title="Locked down: hover + select only",
    )
    _fig.update_layout(dragmode="select")  # box-select on drag ("lasso" for freehand)
    _fig.update_xaxes(fixedrange=True)  # no zoom/pan/pinch on x
    _fig.update_yaxes(fixedrange=True)  # no zoom/pan/pinch on y

    locked = mo.ui.plotly(
        _fig,
        config={"displayModeBar": False, "scrollZoom": False},
    )
    locked
    return (locked,)


@app.cell
def _(locked, mo):
    _pts = locked.value
    _out = mo.md(
        "*Drag a box over some points above — hover still shows tooltips, but zoom/pan are disabled.*"
    )
    if _pts:
        _out = mo.md(f"✅ Selection still works: **{len(_pts)}** points highlighted.")
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ✏️ Your turn — Practice 14

    Take a `px.line` of `stocks` `NFLX` and lock it down so the user can **hover** for
    values but **cannot zoom, pan, or see the toolbar** — a "display-only" line chart.

    *Hints:* `fixedrange=True` on both axes; render with
    `config={"displayModeBar": False, "scrollZoom": False}` — either via `mo.ui.plotly(fig, config=...)`
    or `fig.show(config=...)`. (A line chart needs no `dragmode="select"` unless you also
    want selection.)
    """)
    return


@app.cell
def _(px, stocks):
    # TODO: lock down this line chart to hover-only
    _fig = px.line(
        stocks, x="date", y="NFLX", title="NFLX — display only", template="simple_white"
    )
    _fig.update_xaxes(fixedrange=True)
    _fig.update_yaxes(fixedrange=True)
    _fig.show(config={"displayModeBar": False, "scrollZoom": False})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Practice 14": mo.md(
                r"""
                ```python
                fig = px.line(stocks, x="date", y="NFLX", title="NFLX — display only",
                              template="plotly_white")
                fig.update_xaxes(fixedrange=True)
                fig.update_yaxes(fixedrange=True)

                # reactive render (or fig.show(config=...) for a bare figure):
                mo.ui.plotly(fig, config={"displayModeBar": False, "scrollZoom": False})
                ```

                Because `fixedrange=True` is baked into the figure, even a *bare* returned
                `fig` is un-zoomable; the `config` only additionally hides the toolbar and the
                scroll-zoom. Hover tooltips are untouched by both.
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏁 Capstone challenge

    Put it all together. Using `gapminder`, build a **single figure** that:

    1. shows GDP/capita (log x) vs life expectancy for **2007**,
    2. sizes markers by population, colors by continent,
    3. adds a **vertical line** at the median GDP/capita with an annotation,
    4. adds a **horizontal line** at the global mean life expectancy,
    5. uses a custom `hovertemplate` showing country, GDP, and life expectancy,
    6. applies the `"plotly_white"` template and a centered title.

    Sketch it in the cell below; a reference solution is in the accordion.
    """)
    return


@app.cell
def _(gapminder, np, px):
    # TODO: capstone — your integrated figure here
    _d = gapminder.query("year == 2007")
    _fig = px.scatter(
        _d,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=55,
        color="continent",
        log_x=True,
        template="plotly_white",
        custom_data=["country"],
        title="Wealth & Health, 2007",
    )
    _fig.add_vline(
        x=_d["gdpPercap"].median(),
        line_width=1,
        line_dash="dot",
        annotation_text="Median GDP/capita",
        annotation_position="top",
        annotation_x=np.log10(_d["gdpPercap"].median()),
    )
    _fig.add_hline(
        y=_d["lifeExp"].mean(),
        line_width=1,
        line_dash="dash",
        line_color="gray",
        annotation_text="Global Mean Life Expectancy",
        annotation_position="bottom right",
    )
    _fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "GDP/capita: $%{x:,.0f}<br>"
            "Life exp: %{y:.1f} yrs<br>"
            "<extra></extra>"
        )
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Show solution — Capstone": mo.md(
                r"""
                ```python
                d = gapminder.query("year == 2007")
                fig = px.scatter(
                    d, x="gdpPercap", y="lifeExp", size="pop", color="continent",
                    log_x=True, size_max=55, custom_data=["country"],
                    title="Wealth & health, 2007",
                )
                fig.update_traces(
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>GDP/capita: $%{x:,.0f}<br>"
                        "Life exp: %{y:.1f}<extra></extra>"
                    )
                )
                fig.add_vline(
                    x=d.gdpPercap.median(), line_dash="dot",
                    annotation_text="median GDP/capita", annotation_position="top",
                )
                fig.add_hline(
                    y=d.lifeExp.mean(), line_dash="dash", line_color="gray",
                    annotation_text="global mean life exp", annotation_position="bottom right",
                )
                fig.update_layout(template="plotly_white", title=dict(x=0.5))
                fig
                ```
                """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 📚 Cheat-sheet & where to go next

    | Task | Call |
    |---|---|
    | Quick chart from a dataframe | `px.scatter / line / bar / histogram / box / violin` |
    | Small multiples | `facet_col=`, `facet_row=`, `facet_col_wrap=` |
    | Full control, trace-by-trace | `go.Figure(); fig.add_trace(go.Scatter(...))` |
    | Grid of panels | `make_subplots(rows, cols)` + `add_trace(..., row=, col=)` |
    | Two y-scales | `make_subplots(specs=[[{"secondary_y": True}]])` |
    | Style everything | `fig.update_layout / update_xaxes / update_traces` |
    | Whole-look preset | `template="plotly_white" / "simple_white" / "plotly_dark"` |
    | Reference marks | `add_hline / add_vline / add_hrect / add_vrect / add_annotation` |
    | Exact tooltips | `hovertemplate=` + `custom_data=` |
    | Play over time | `animation_frame=`, `animation_group=` |
    | Reactive selection in marimo | `mo.ui.plotly(fig)` → `.value` |
    | Whole-look theme | `template="plotly_white"` · `"base+mytheme"` |
    | Register a custom theme | `pio.templates["x"] = go.layout.Template(layout=dict(...))` |
    | Backgrounds / fonts / colors | `paper_bgcolor`, `plot_bgcolor`, `font`, `colorway` |
    | Grid on/off & style | `update_yaxes(showgrid=False, gridcolor=, griddash=)` |
    | Axis format / ticks / range | `update_xaxes(tickformat=, tickangle=, range=, type=)` |
    | Disable zoom/pan/pinch | `update_xaxes(fixedrange=True)` (+ y) |
    | Default drag = select | `update_layout(dragmode="select")` (or `"lasso"`) |
    | Hide the toolbar & scroll-zoom | `config={"displayModeBar": False, "scrollZoom": False}` |
    | Drop only some buttons | `modebar_remove=["zoom","pan","toimage",...]` |
    | Save to file | `fig.write_html("f.html")` · `fig.write_image("f.png")` (needs `kaleido`) |

    **Docs:** the Plotly Python reference at `plotly.com/python/` mirrors this
    structure. `help(px.scatter)` and `fig.<trace>.` tab-completion in the editor are
    your fastest reference. Every property you set with a nested `dict(...)` is
    documented under `plotly.com/python/reference/`.

    Happy plotting! 🎨
    """)
    return


if __name__ == "__main__":
    app.run()
