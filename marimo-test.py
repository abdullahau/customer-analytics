import marimo

__generated_with = "0.9.20"
app = marimo.App(layout_file="layouts/marimo-test.grid.json")


@app.cell
def __():
    import marimo as mo

    import polars as pl
    import altair as alt
    import numpy as np
    from great_tables import GT

    alt.renderers.enable('mimetype')
    return GT, alt, mo, np, pl


@app.cell(hide_code=True)
def __(mo):
    mo.md("""### Import Data""")
    return


@app.cell
def __(pl):
    grocery_lf = pl.scan_csv(source="data/panel-datasets/edible_grocery.csv",
                             has_header=True,
                             separator=",",
                             schema={'panel_id': pl.Int32,
                                     'trans_id': pl.Int32,
                                     'week': pl.Int16,
                                     'sku_id': pl.Categorical,
                                     'units': pl.Int16,
                                     'price': pl.Float32,
                                     'brand': pl.Categorical})
    grocery_lf.collect_schema()
    return (grocery_lf,)


@app.cell
def __(pl):
    sku_lf = pl.scan_csv(source="data/panel-datasets/sku_weight.csv",
                             has_header=True,
                             separator=",",
                             schema={'sku_id': pl.Categorical,
                                     'weight': pl.Int16})
    sku_lf.collect_schema()
    return (sku_lf,)


@app.cell
def __(pl):
    kiwi_lf = pl.scan_csv(source="data/panel-datasets/kiwibubbles_trans.csv",
                          has_header=True,
                          separator=",",
                          schema={'ID': pl.Int16,
                                  'Market': pl.Categorical,
                                  'Week': pl.Int16,
                                  'Day': pl.Int16,
                                  'Units': pl.Int16})
    kiwi_lf.collect_schema()
    return (kiwi_lf,)


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"""### Reusable Functions""")
    return


@app.cell
def __(pl):
    # Weekly Grocery Sales LazyFrame (Query Plan): Weekly 'spend' by 'Category', 'Brand' or 'All'
    def weekly_spend_summary(brand, lf):
        summary = (
            lf
            .select(['week', 'units', 'price', 'brand'])
            .with_columns(((pl.col('units') * pl.col('price')).cast(pl.Float64)).alias('spend'))
        )

        if brand == 'Category': # Return LazyFrame of total category
            summary = summary.group_by('week')
        elif brand == 'All': # Return LazyFrame of all brands
            summary = summary.group_by('week', 'brand')
        else:  # Return LazyFrame of specified brand
            summary = summary.filter(
                pl.col('brand') == brand
            ).group_by('week', 'brand')

        summary = summary.agg(
            pl.col("spend").sum().cast(pl.Float64).alias('Weekly Spend') 
        ).sort('week')

        return summary
    return (weekly_spend_summary,)


@app.cell
def __(pl, sku_lf):
    # Weekly Grocery Volume Sales LazyFrame (Query Plan): Weekly 'volume' by 'Brand' or 'All'
    def weekly_vol_summary(brand, lf):
        with pl.StringCache():
            lf = (
                lf
                .join(
                    other=sku_lf,
                    left_on="sku_id",
                    right_on="sku_id"            
                )
                .select(['week', 'units', 'brand', 'weight'])
            )

            if brand != 'All': 
                brand = [brand] if type(brand) == str else brand
                lf = lf.filter(
                    pl.col('brand').is_in(*[brand])
                )

            summary = lf.with_columns(
                (((pl.col('units') * pl.col('weight'))/1000).cast(pl.Float64)).alias('volume')
            ).group_by('week', 'brand').agg(
                pl.col("volume").sum().cast(pl.Float64).alias('Weekly Volume')
            ).sort('week')

        return summary
    return (weekly_vol_summary,)


@app.cell
def __(alt, np):
    # Altair Weekly Line Plot
    def weekly_plot(dataframe, y, color=None, title="", y_axis_label="", pct=False, legend=False):

        # Configure the color encoding only if color is provided
        if color is not None:
            color_encoding = alt.Color(
                f'{color}:N',  # N = a discrete unordered category
                legend=alt.Legend(title=color) if legend else None  # Add legend conditionally
            )
        else:
            color_encoding = alt.Color()  # No color encoding    

        chart = alt.Chart(dataframe).mark_line(strokeWidth=1).encode(
            x = alt.X(
                'week',
                axis=alt.Axis(
                    values=np.arange(0, 104 + 1, 13), # Explicitly specify quarter-end weeks
                    labelExpr="datum.value", # Show only these labels
                    title='Week'
                )
            ),
            y = alt.Y(
                f'{y}:Q', # Q = a continuous real-valued quantity
                title=y_axis_label,
                axis=alt.Axis(format="$,.0f") if not pct else alt.Axis(format=",.0%")
            ),
            color = color_encoding
        ).properties(
            width=500,
            height=250,
            title=title
        ).configure_view(
            stroke=None
        ).configure_axisY(
            # grid=False # turn off y-axis grid if required
        )

        return chart # alt.JupyterChart(chart)
    return (weekly_plot,)


@app.cell
def __(grocery_lf, pl, weekly_spend_summary):
    # Annual Sales Summary LazyFrame for All Brands
    def annual_sales_summary():
        summary = (
            weekly_spend_summary('All', grocery_lf)
            .with_columns((pl.col("week") / 52).ceil().cast(pl.Int32).alias('year'))
            .group_by(['year', 'brand'])
            .agg(pl.col("Weekly Spend").sum().cast(pl.Float64).alias('Yearly Sales'))
        ).sort('year')

        return summary
    return (annual_sales_summary,)


@app.cell
def __(alt, pl):
    def freq_dist_plot(
        data, 
        column, 
        bin_edges, 
        labels, 
        x_title, 
        y_title, 
        chart_title, 
        subtitle, 
        width=500, 
        height=250, 
        label_angle=0, 
        left_closed=True, 
        compute_rel_freq=True
    ):
        """
        Creates a standardized Altair bar chart for relative frequency distribution plots.

        Parameters:
        - data (Polars LazyFrame or DataFrame): Input dataset.
        - column (str): Column to analyze for distribution.
        - bin_edges (array-like): Edges for binning.
        - labels (list of str): Labels for the bins.
        - x_title (str): Title for the x-axis.
        - y_title (str): Title for the y-axis.
        - chart_title (str): Main title for the chart.
        - subtitle (str): Subtitle for the chart.
        - width (int, optional): Width of the chart. Default is 650.
        - height (int, optional): Height of the chart. Default is 250.
        - label_angle (int, optional): Angle for x-axis labels. Default is 0.
        - left_closed (bool, optional): Whether bins are left-closed. Default is True.
        - compute_rel_freq (bool, optional): Whether to compute relative frequencies. Default is True.

        Returns:
        - alt.Chart: The generated Altair chart.
        """
        # Apply binning to the data
        binned_data = data.with_columns(
            pl.col(column).cut(bin_edges, labels=labels, left_closed=left_closed).alias("cut")
        )

        # Optionally compute relative frequencies
        if compute_rel_freq:
            binned_data = (
                binned_data
                .group_by("cut")
                .agg(pl.col("cut").count().alias("Frequency"))
                .with_columns(
                    (pl.col("Frequency") / pl.col("Frequency").sum()).alias("% of Total")
                )
                .collect()
            )

        # Create the Altair chart
        chart = alt.Chart(binned_data).mark_bar().encode(
            x=alt.X("cut:O", axis=alt.Axis(labelAngle=label_angle, title=x_title), sort=labels),
            y=alt.Y("% of Total:Q", axis=alt.Axis(format=".0%", title=y_title)),
        ).properties(
            width=width,
            height=height,
            title={"text": chart_title, "subtitle": subtitle},
        )

        return chart
    return (freq_dist_plot,)


@app.cell(hide_code=True)
def __(mo):
    mo.md("""## Preliminaries""")
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md("""### Weekly Sales Pattern""")
    return


@app.cell(disabled=True)
def __(grocery_lf, pl, weekly_spend_summary):
    # Weekly Sales Pivot Table - Polars DataFrame
    # For visualizing and inspecting only
    weekly_spend_summary('All', grocery_lf).collect().pivot(
        on="brand",
        index="week",
        values="Weekly Spend",
        sort_columns=True,
    ).with_columns(
        pl.sum_horizontal(pl.exclude('week')).cast(pl.Float64).alias("Total") # Row total
    ).sort("week")
    return


@app.cell
def __(grocery_lf, weekly_plot, weekly_spend_summary):
    weekly_plot(dataframe=weekly_spend_summary('Category', grocery_lf).collect(), 
                y='Weekly Spend', 
                title='Category - Weekly Revenue', 
                y_axis_label='Spend ($)',
                pct=False,
                legend=False)
    return


if __name__ == "__main__":
    app.run()
