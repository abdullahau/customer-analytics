import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    # ---- Consulting-deck framework: CSS + slide builders (style emulation only) ----
    # Scroll-stack of fixed 16:9 slides. Each slide is one cell -> easy to edit,
    # reorder, and reuse as a template. Compose 1+ exhibits per slide with cols()/
    # exhibit(), narrative with bullets()/note(), and make charts fill with fit().
    def _slot(obj):
        # Render any marimo / plotly / great-tables object to embeddable HTML.
        return obj.text if hasattr(obj, "text") else mo.vstack([obj]).text

    def fit(fig, height=None):
        # Make a plotly figure fill its column (drop fixed width, autosize).
        fig.update_layout(autosize=True, width=None)
        if height is not None:
            fig.update_layout(height=height)
        return fig

    def cols(*items, gap=26, widths=None):
        # Place exhibits side by side. `widths` = list of flex-grow ints.
        ws = widths or [1] * len(items)
        inner = "".join(
            f"<div class='mck-col' style='flex:{w}'>{_slot(it)}</div>"
            for it, w in zip(items, ws)
        )
        return mo.Html(f"<div class='mck-cols' style='gap:{gap}px'>{inner}</div>")

    def stack(*items, gap=16):
        inner = "".join(f"<div>{_slot(it)}</div>" for it in items)
        return mo.Html(f"<div class='mck-stack' style='gap:{gap}px'>{inner}</div>")

    def exhibit(obj, caption=""):
        cap = f"<div class='mck-cap'>{caption}</div>" if caption else ""
        return mo.Html(f"<div class='mck-exh'>{_slot(obj)}{cap}</div>")

    def bullets(items):
        lis = "".join(f"<li>{it}</li>" for it in items)
        return mo.Html(f"<ul class='mck-points'>{lis}</ul>")

    def note(html):
        return mo.Html(f"<div class='mck-note'>{html}</div>")

    def slide(title, body, eyebrow="", subtitle="", takeaway="", source="", page=None):
        head = f"<div class='mck-eyebrow'>{eyebrow}</div>" if eyebrow else ""
        sub = f"<div class='mck-sub'>{subtitle}</div>" if subtitle else ""
        tak = f"<div class='mck-takeaway'>{takeaway}</div>" if takeaway else ""
        src = f"Source: {source}" if source else ""
        pg = "" if page is None else page
        return mo.Html(
            "<div class='mck-deck'><section class='mck-slide'>"
            f"{head}<h2 class='mck-title'>{title}</h2>{sub}"
            "<div class='mck-rule'></div>"
            f"<div class='mck-body'>{_slot(body)}</div>{tak}"
            f"<div class='mck-foot'><div class='mck-src'>{src}</div>"
            f"<div class='mck-page'>{pg}</div></div>"
            "</section></div>"
        )

    def cover(title, subtitle, tagline="", meta=""):
        return mo.Html(
            "<div class='mck-deck'><section class='mck-slide mck-cover'>"
            f"<div class='mck-cover-kicker'>{tagline}</div>"
            f"<h1 class='mck-cover-title'>{title}</h1>"
            f"<div class='mck-cover-sub'>{subtitle}</div>"
            f"<div class='mck-cover-meta'>{meta}</div>"
            "</section></div>"
        )

    def divider(number, title, page=None):
        pg = "" if page is None else f"<div class='mck-corner-page'>{page}</div>"
        return mo.Html(
            "<div class='mck-deck'><section class='mck-slide mck-divider'>"
            f"<div class='mck-divider-num'>{number}</div>"
            f"<h2 class='mck-divider-title'>{title}</h2>{pg}"
            "</section></div>"
        )

    mo.Html("""<style>
    .mck-deck{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
      --navy:#1f3a5f;--ink:#1f2328;--muted:#6b7280;--accent:#c4703a;}
    /* fixed 16:9 slide, PowerPoint / reveal.js proportions */
    .mck-slide{position:relative;background:#fff;border:1px solid #e6e8eb;border-radius:3px;
      box-shadow:0 3px 16px rgba(31,58,95,.10);width:100%;max-width:1180px;aspect-ratio:16/9;
      margin:20px auto;padding:32px 46px 14px;display:flex;flex-direction:column;box-sizing:border-box;overflow:hidden;}
    .mck-eyebrow{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);
      font-weight:700;margin-bottom:6px;}
    .mck-title{font-size:23px;line-height:1.2;font-weight:700;color:var(--navy);margin:0;letter-spacing:-.01em;}
    .mck-sub{font-size:13px;color:var(--muted);margin-top:4px;}
    .mck-rule{height:3px;background:var(--navy);width:56px;margin:11px 0 14px;}
    .mck-body{flex:1;min-height:0;color:var(--ink);font-size:14px;line-height:1.5;overflow:auto;}
    .mck-takeaway{margin-top:12px;padding:10px 15px;background:#f3f6fa;border-left:3px solid var(--accent);
      font-size:13px;color:var(--ink);line-height:1.45;}
    .mck-foot{display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid #e6e8eb;
      padding-top:7px;margin-top:10px;font-size:10.5px;color:var(--muted);}
    .mck-src{font-style:italic;max-width:80%;} .mck-page{font-variant-numeric:tabular-nums;font-weight:700;}
    /* layout primitives */
    .mck-cols{display:flex;height:100%;align-items:stretch;}
    .mck-col{min-width:0;display:flex;flex-direction:column;justify-content:center;}
    .mck-stack{display:flex;flex-direction:column;height:100%;}
    .mck-exh{display:flex;flex-direction:column;height:100%;justify-content:center;}
    .mck-cap{font-size:11px;color:var(--muted);text-align:center;margin-top:2px;font-style:italic;}
    .mck-note{font-size:14.5px;line-height:1.6;color:var(--ink);}
    .mck-note b{color:var(--navy);} .mck-note h4{color:var(--navy);margin:.2em 0 .4em;font-size:15px;}
    /* cover + divider */
    .mck-cover{background:linear-gradient(135deg,#1f3a5f 0%,#122336 100%);color:#fff;justify-content:center;border:none;}
    .mck-cover-kicker{font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:#d68a5a;font-weight:700;margin-bottom:18px;}
    .mck-cover-title{font-size:44px;line-height:1.06;font-weight:700;margin:0 0 14px;max-width:84%;}
    .mck-cover-sub{font-size:18px;color:#cdd7e3;max-width:66%;line-height:1.45;}
    .mck-cover-meta{position:absolute;bottom:22px;left:46px;font-size:11px;letter-spacing:.05em;color:#93a6bc;}
    .mck-divider{background:#1f3a5f;color:#fff;justify-content:center;border:none;}
    .mck-divider-num{font-size:14px;letter-spacing:.22em;color:#d68a5a;font-weight:700;}
    .mck-divider-title{font-size:33px;font-weight:700;margin:8px 0 0;max-width:82%;line-height:1.15;}
    .mck-corner-page{position:absolute;right:46px;bottom:20px;font-size:11px;font-weight:700;
      color:#93a6bc;font-variant-numeric:tabular-nums;}
    /* lists */
    .mck-agenda{list-style:none;padding:0;margin:4px 0 0;}
    .mck-agenda li{display:flex;gap:18px;padding:12px 2px;border-bottom:1px solid #eef1f4;font-size:16px;color:var(--ink);}
    .mck-agenda .n{color:var(--accent);font-weight:700;min-width:30px;}
    .mck-agenda .q{color:var(--muted);font-size:13.5px;margin-left:auto;text-align:right;max-width:46%;}
    .mck-points{list-style:none;padding:0;margin:0;}
    .mck-points li{position:relative;padding:8px 0 8px 26px;border-bottom:1px solid #f1f3f5;font-size:15px;line-height:1.45;}
    .mck-points li:before{content:'';position:absolute;left:2px;top:15px;width:9px;height:9px;background:var(--accent);border-radius:1px;}
    .mck-points b{color:var(--navy);}
    </style>""")
    return cols, cover, divider, exhibit, fit, note, slide, stack


@app.cell
def _():
    # ---------------------------------------------------------------------
    # CONTENT & CHARTS COME FROM THE MARIMO NOTEBOOK (single source of truth).
    #
    # customer-base-audit.py is parsed, marimo's scaffolding stripped (the
    # `@app.cell` / `def _(...)` wrapper and the cell-level `return`), the
    # marimo-only blocks dropped (`mo.*`, the `how(...)` explainers), and the
    # rest exec'd into one namespace.
    #
    # It is returned as a SINGLE object on purpose: marimo builds its reactive
    # graph by static analysis, so names created dynamically by exec() would be
    # invisible to it. One tracked symbol (`NB`) keeps the DAG correct — hence
    # `NB.bar_distribution(...)`, `NB.cust_data_2019`, `NB.YEAR_CURR`, etc.
    # ---------------------------------------------------------------------
    import ast
    import re
    import textwrap
    from pathlib import Path
    from types import SimpleNamespace

    def load_notebook_namespace(path):
        src = Path(path).read_text(encoding="utf-8")
        src = src[: re.search(r"\nif __name__ ==", src).start()]
        blocks = []
        for cell in re.split(r"(?m)^(?=@app\.cell)", src)[1:]:
            lines = cell.splitlines()
            di = next((i for i, l in enumerate(lines) if re.match(r"def _\(", l)), None)
            if di is None:
                continue
            j = di
            while not lines[j].rstrip().endswith("):"):
                j += 1
            body = lines[j + 1 :]
            ri = next(
                (i for i, l in enumerate(body) if re.match(r"^    return(\s|$|\()", l)),
                None,
            )
            if ri is not None:
                body = body[:ri]
            body = textwrap.dedent("\n".join(body))
            if not body.strip():
                continue
            kept = [
                seg
                for seg in (
                    ast.get_source_segment(body, n) for n in ast.parse(body).body
                )
                if seg and not re.search(r"\bmo\.|\bhow\(", seg)
            ]
            if kept:
                blocks.append("\n".join(kept))
        ns = {}
        exec(compile("\n\n".join(blocks), str(path), "exec"), ns)
        return SimpleNamespace(**ns)

    NB = load_notebook_namespace("notebooks/analyses/customer-base-audit.py")
    return (NB,)


@app.cell
def _(cover):
    cover(
        title="Customer-Base Audit",
        subtitle="How Madrigal's customers differ — and how their behaviour changes over time",
        tagline="Descriptive customer analytics",
        meta="Madrigal transaction sample · 2016–2019 · Illustrative analysis",
    )
    return


@app.cell
def _(mo, slide):
    _agenda = mo.Html(
        "<ol class='mck-agenda'>"
        "<li><span class='n'>1</span><span>How do customers differ from one another?</span>"
        "<span class='q'>Heterogeneity within a single year</span></li>"
        "<li><span class='n'>2</span><span>What changed between two periods?</span>"
        "<span class='q'>2018 vs 2019 performance bridge</span></li>"
        "<li><span class='n'>3</span><span>How does a single cohort evolve?</span>"
        "<span class='q'>The Q1-2016 cohort over its life</span></li>"
        "<li><span class='n'>4</span><span>How do cohorts compare to one another?</span>"
        "<span class='q'>Like-for-like by age</span></li>"
        "<li><span class='n'>5</span><span>How healthy is the customer base overall?</span>"
        "<span class='q'>Acquisition, repeat buying, concentration</span></li>"
        "</ol>"
    )
    slide(
        title="Five lenses on the same customer base",
        eyebrow="Contents",
        subtitle="Each lens asks a different question of one transaction dataset",
        body=_agenda,
        page=2,
    )
    return


@app.cell
def _(mo, slide):
    _pts = mo.Html(
        "<ul class='mck-points'>"
        "<li><b>Value is concentrated.</b> A small share of customers accounts for "
        "most transactions, spend, and profit — the base is not uniform.</li>"
        "<li><b>The “average customer” describes no one.</b> Every behavioural "
        "measure is right-skewed, so the mean sits well above the median and most "
        "customers fall below the mean.</li>"
        "<li><b>Cohorts decay through fewer active buyers, not weaker spending.</b> "
        "Spend per active customer stays broadly flat; the base shrinks because fewer "
        "customers remain — so <b>repeat buying is the lever</b>.</li>"
        "<li><b>Behaviour is stable and predictable</b> once heterogeneity is taken "
        "into account — the same patterns recur across periods and cohorts.</li>"
        "</ul>"
    )
    slide(
        title="The average customer describes no one — value is concentrated, and its decay is driven by repeat buying",
        eyebrow="Executive summary",
        body=_pts,
        takeaway="Manage the customer base as a portfolio: protect the high-value minority and lift repeat buying, rather than chase an “average” customer that does not exist.",
        source="Madrigal transaction sample, 2016–2019",
        page=3,
    )
    return


@app.cell
def _(cols, note, slide):
    _left = note(
        "<h4>The data</h4>"
        "A 1% sample of <b>Madrigal</b>'s transaction records — 70,041 customers, "
        "aggregated to the quarter, for 16 quarters (Q1 2016 – Q4 2019). "
        "Each customer carries transactions, spend, profit, and an acquisition cohort.<br><br>"
        "The audit is <b>descriptive</b>: it summarises how customers behave, "
        "it does not forecast."
    )
    _right = note(
        "<h4>One identity ties it together</h4>"
        "<b>Profit = N<sub>c</sub> × AOF × AOV × Margin</b><br>"
        "<span style='color:#6b7280'>(active customers × orders per customer × "
        "spend per order × profit margin)</span><br><br>"
        "Every result below traces a change in profit to one of these factors — "
        "<b>fewer customers</b>, <b>less frequent orders</b>, <b>smaller orders</b>, "
        "or <b>thinner margins</b>."
    )
    slide(
        title="One dataset, one profit identity — read every exhibit through its four factors",
        eyebrow="Approach & data",
        body=cols(_left, _right, gap=40),
        source="Madrigal transaction sample, 2016–2019",
        page=4,
    )
    return


@app.cell
def _(divider):
    divider("Lens 1", "How do customers differ from one another?", page=5)
    return


@app.cell
def _(NB, cols, exhibit, fit, slide):
    _spend = fit(
        NB.bar_distribution(
            NB.create_distribution(
                NB.cust_data_2019, "Spend", **NB.create_bins_labels(25, 1000)
            ),
            title="",
            x_title="Annual Spend ($)",
        ),
        height=360,
    )
    _profit = fit(
        NB.bar_distribution(
            NB.create_distribution(
                NB.cust_data_2019, "Profit", **NB.create_bins_labels(25, 500, 0)
            ),
            title="",
            x_title="Annual Profit ($)",
            color="#c4703a",
        ),
        height=360,
    )
    slide(
        title="The average customer describes no one — spend and profit are both right-skewed",
        eyebrow=f"Lens 1 · Distributions · {NB.YEAR_CURR}",
        subtitle="Share of active customers by annual spend (left) and annual profit (right)",
        body=cols(
            exhibit(_spend, "Annual spend per customer"),
            exhibit(_profit, "Annual profit per customer"),
        ),
        takeaway=f"About {NB.spend_stats['pct_below_mean']:.0%} of customers spend below the mean "
        f"and {NB.profit_stats['pct_below_mean']:.0%} earn below the mean profit — a long right tail carries the base.",
        source=f"Madrigal transaction sample, active customers, {NB.YEAR_CURR}",
        page=6,
    )
    return


@app.cell
def _(NB, slide):
    _tbl = NB.decile_report_gt(NB.cust_decile_rep, NB.DECILE_FIELDS, "")
    slide(
        title="The top deciles capture a disproportionate share of profit",
        eyebrow="Lens 1 · Value concentration",
        subtitle="Customers ranked into ten equal groups by profit contribution",
        body=_tbl,
        takeaway="The most valuable decile contributes far more than one-tenth of profit, while the lowest deciles contribute little or are loss-making.",
        source="Madrigal transaction sample; deciles by annual profit",
        page=7,
    )
    return


@app.cell
def _(divider):
    divider("Lens 2", "What changed between two periods?", page=8)
    return


@app.cell
def _(NB, cols, fit, note, slide):
    _bridge = fit(NB.profit_bridge_chart(NB.profit_by_group), height=420)
    _txt = note(
        "<h4>Read the bridge</h4>"
        f"Profit moves from {NB.YEAR_PRIOR} to {NB.YEAR_CURR} through three customer groups:"
        "<ul class='mck-points' style='margin-top:8px'>"
        "<li><b>Returning</b> customers, active in both years</li>"
        "<li><b>Lapsed</b> customers, who leave (a drag)</li>"
        "<li><b>New / reactivated</b> customers, who join (a lift)</li></ul>"
    )
    slide(
        title="Profit growth is a balance of returning, lapsed, and newly-won customers",
        eyebrow=f"Lens 2 · Profit bridge · {NB.YEAR_PRIOR}→{NB.YEAR_CURR}",
        body=cols(_bridge, _txt, gap=34, widths=[3, 2]),
        takeaway="The net change is small relative to the gross flows beneath it — sustaining profit depends on keeping lapse in check, not only on winning new customers.",
        source=f"Madrigal transaction sample, {NB.YEAR_PRIOR} and {NB.YEAR_CURR}",
        page=9,
    )
    return


@app.cell
def _(NB, cols, exhibit, fit, note, slide):
    _venn = fit(
        NB.venn_two(
            int(NB.overlap.loc["Active 2018", "Customers"]),
            int(NB.overlap.loc["Active 2019", "Customers"]),
            int(NB.overlap.loc["Active Both Years", "Customers"]),
            "2018 active",
            "2019 active",
            "",
            width=520,
            height=420,
        ),
        height=400,
    )
    _txt = note(
        "Only part of each year's base carries over. The overlap is the "
        "<b>returning</b> core; the crescents are <b>lapsed</b> (left) and "
        "<b>new/reactivated</b> (right) customers.<br><br>"
        "A large non-overlap means the headline active-customer count hides a great "
        "deal of <b>lapse and replacement</b> underneath."
    )
    slide(
        title="Each year's customer base is substantially replaced, not merely carried forward",
        eyebrow="Lens 2 · Customer overlap",
        body=cols(
            exhibit(_venn, "Area-proportional overlap of the two yearly bases"),
            _txt,
            gap=34,
            widths=[3, 2],
        ),
        source="Madrigal transaction sample; customers active in either year",
        page=10,
    )
    return


@app.cell
def _(divider):
    divider("Lens 3", "How does a single cohort evolve?", page=11)
    return


@app.cell
def _(NB, cols, fit, slide, stack):
    _h = 205
    _pa = fit(
        NB.line_chart(
            NB.cohort_q1_decomp,
            "Period",
            "Pct_Active",
            "% active by quarter",
            "% active",
            tickformat=".0%",
        ),
        height=_h,
    )
    _as = fit(
        NB.line_chart(
            NB.cohort_q1_decomp,
            "Period",
            "ASPAC",
            "Spend per active member",
            "ASPAC ($)",
            tickformat="$,.0f",
        ),
        height=_h,
    )
    _ao = fit(
        NB.line_chart(
            NB.cohort_q1_decomp,
            "Period",
            "AOF",
            "Orders per active member",
            "AOF",
            tickformat=".2f",
        ),
        height=_h,
    )
    _av = fit(
        NB.line_chart(
            NB.cohort_q1_decomp,
            "Period",
            "AOV",
            "Average order value",
            "AOV ($)",
            tickformat="$,.0f",
        ),
        height=_h,
    )
    slide(
        title="Cohort revenue decays through fewer active buyers — not weaker spending",
        eyebrow=f"Lens 3 · Revenue decomposition · {NB.FOCUS_COHORT_QTR} cohort",
        subtitle="% active falls steeply; spend-per-active, order frequency and order value stay broadly flat",
        body=stack(cols(_pa, _as), cols(_ao, _av), gap=10),
        takeaway="The customers who remain keep behaving normally; the base shrinks because fewer of them remain — the lever is repeat buying, not spend stimulation.",
        source="Madrigal transaction sample; Q1-2016 acquisition cohort by quarter",
        page=12,
    )
    return


@app.cell
def _(NB, fit, slide):
    _fig = fit(NB.second_purchase_chart(NB.second_purchase), height=420)
    slide(
        title="Most repeat buying is decided early — the second-purchase curve flattens quickly",
        eyebrow=f"Lens 3 · Second purchase · {NB.FOCUS_COHORT_QTR} cohort",
        subtitle="Cumulative share of the cohort that has made a second purchase, by quarter",
        body=_fig,
        takeaway=f"Across the {NB.FOCUS_COHORT_N:,} customers in the cohort, the cumulative repeat rate rises fastest in the first few quarters, then plateaus — early experience is decisive.",
        source="Madrigal transaction sample; Q1-2016 acquisition cohort",
        page=13,
    )
    return


@app.cell
def _(divider):
    divider("Lens 4", "How do cohorts compare to one another?", page=14)
    return


@app.cell
def _(NB, cols, exhibit, fit, slide):
    _pa = fit(
        NB.cohort_lines(NB.cohort_df, "PctActive", align=True, tickformat=".0%"),
        height=360,
    )
    _av = fit(
        NB.cohort_lines(NB.cohort_df, "AOV", align=True, tickformat="$,.0f"), height=360
    )
    slide(
        title="Aligned by age, cohorts trace nearly the same path — behaviour is a property of the base",
        eyebrow="Lens 4 · Like-for-like by cohort age",
        subtitle="Every acquisition cohort, indexed to quarters since acquisition",
        body=cols(
            exhibit(_pa, "% active by quarters since acquisition"),
            exhibit(_av, "Average order value by quarters since acquisition"),
        ),
        takeaway="Newer cohorts are not obviously better or worse than older ones once you align by age — the decay curve is structural, so forecasts can lean on it.",
        source="Madrigal transaction sample; all acquisition cohorts aligned by age",
        page=15,
    )
    return


@app.cell
def _(divider):
    divider("Lens 5", "How healthy is the customer base overall?", page=16)
    return


@app.cell
def _(NB, cols, exhibit, fit, slide):
    _acq = fit(NB.acquisitions_bar_chart(NB.annual_cohort_combined), height=300)
    _act = fit(NB.active_customers_bar_chart(NB.annual_cohort_combined), height=300)
    _sp = fit(NB.spend_profit_bar_chart(NB.annual_cohort_combined), height=300)
    slide(
        title="The base is growing on every headline measure — customers, spend, and profit",
        eyebrow="Lens 5 · Annual performance",
        body=cols(
            exhibit(_acq, "New customers"),
            exhibit(_act, "Active customers"),
            exhibit(_sp, "Spend & profit"),
        ),
        takeaway="Growth shows up first in acquisition and the active count; because per-customer behaviour is stable, more customers translates fairly directly into more spend and profit.",
        source="Madrigal transaction sample, 2016–2019",
        page=17,
    )
    return


@app.cell
def _(NB, fit, slide):
    _fig = fit(
        NB.cohort_flow_chart(
            NB.flow_profit, y_title="Profit ($ MM)", total_fmt="{:.2f}"
        ),
        height=430,
    )
    slide(
        title="Each year's profit rests increasingly on older cohorts — repeat buying compounds",
        eyebrow="Lens 5 · Cohort contribution to profit",
        subtitle="Annual profit split by acquisition-year cohort",
        body=_fig,
        takeaway="A healthy base carries a thick tail of still-active older cohorts; new acquisition tops it up rather than replacing a leaking core.",
        source="Madrigal transaction sample; profit by acquisition-year cohort",
        page=18,
    )
    return


@app.cell
def _(mo, slide):
    _imp = mo.Html(
        "<ul class='mck-points'>"
        "<li><b>Treat the base as a portfolio.</b> Segment by value and manage the "
        "high-value minority explicitly — the average hides them.</li>"
        "<li><b>Make repeat buying the first lever.</b> Cohort decay is driven by fewer "
        "active customers, so small repeat-buying gains compound across every cohort.</li>"
        "<li><b>Win the second purchase early.</b> Repeat behaviour is largely set in "
        "the first few quarters — invest in early-life experience.</li>"
        "<li><b>Acquire more of the right customers.</b> Per-customer behaviour is "
        "stable, so growth comes mainly from adding customers like the ones you keep.</li>"
        "</ul>"
    )
    slide(
        title="Four moves follow directly from the audit",
        eyebrow="Implications",
        body=_imp,
        takeaway="None of these require an “average customer”. They require managing a heterogeneous base by value and by age.",
        page=19,
    )
    return


@app.cell
def _(divider):
    divider("Appendix", "Supplementary exhibits", page=20)
    return


@app.cell
def _(NB, cols, exhibit, fit, slide):
    _tx = fit(
        NB.bar_distribution(
            NB.create_distribution(
                NB.cust_data_2019,
                "NumTrans",
                bins=list(range(1, 11)) + [float("inf")],
                labels=[str(i) for i in range(1, 10)] + ["10+"],
            ),
            title="",
            x_title="Annual Transactions",
        ),
        height=360,
    )
    _mg = fit(
        NB.bar_distribution(
            NB.create_distribution(
                NB.cust_data_2019, "Margin", **NB.create_bins_labels(5, 100, 0)
            ),
            title="",
            x_title="Margin (%)",
            color="#c4703a",
        ),
        height=360,
    )
    slide(
        title="Transaction counts and margins are skewed too",
        eyebrow=f"Appendix · Further distributions · {NB.YEAR_CURR}",
        body=cols(
            exhibit(_tx, "Annual transactions per customer"),
            exhibit(_mg, "Average margin per customer"),
        ),
        source=f"Madrigal transaction sample, active customers, {NB.YEAR_CURR}",
        page=21,
    )
    return


@app.cell
def _(note, slide):
    _txt = note(
        "<h4>“Average spend per transaction” is two different numbers</h4>"
        "<ul class='mck-points' style='margin-top:8px'>"
        "<li><b>AOV — ratio of totals.</b> Total spend ÷ total transactions. A "
        "<b>transaction-weighted</b> average, so frequent buyers dominate it.</li>"
        "<li><b>Mean of per-customer averages.</b> Average each customer's own "
        "spend-per-transaction, then average across customers — every customer counts "
        "equally, so one-and-done-in-2019 buyers pull it up.</li></ul>"
        "The two are equal only if every customer transacts the same number of times, "
        "which never happens. The gap's direction is informative: here the weighted "
        "figure sits below the unweighted one, so heavier buyers have <b>smaller</b> "
        "baskets than light buyers.<br><br>"
        "<span style='color:#6b7280'>Convention used throughout: “AOV” always means the "
        "transaction-weighted ratio of totals.</span>"
    )
    slide(
        title="A definitions note: keep the two “average transaction” numbers apart",
        eyebrow="Appendix · Method",
        body=_txt,
        source="See Lens 1 — Distribution of average spend per transaction",
        page=22,
    )
    return


@app.cell
def _(note, slide):
    _txt = note(
        "<ul class='mck-points'>"
        "<li><b>Why not “retention” here.</b> Madrigal is <b>noncontractual</b> — a "
        "customer who skips a period has not necessarily left. “Retention” properly "
        "describes contractual renewal / survival, where a cancellation is actually "
        "observed.</li>"
        "<li><b>% of cohort active.</b> The share of a cohort that buys in a period — "
        "<b>unconditional</b>, and it includes one-time buyers.</li>"
        "<li><b>Repeat-buying rate.</b> The <b>conditional</b> quantity — the share of "
        "customers active in one period who buy again in the next.</li>"
        "<li><b>Carryover.</b> For value: a cohort's profit in one year relative to the "
        "year before (what the cohort-flow chart annotates).</li></ul>"
        "Likewise the two “one-and-done” figures are different: <b>one-and-done in "
        "2019</b> (exactly one transaction that year, Lens 1) is not the share of a "
        "cohort that <b>never makes a second purchase</b> (Lens 3)."
    )
    slide(
        title="A wording note: “repeat-buying rate” and “% of cohort active”, not “retention”",
        eyebrow="Appendix · Method",
        body=_txt,
        source="After Fader, Hardie & Ross, The Customer-Base Audit (2022), Ch. 9 — “Be Wary of the ‘R’ Word”",
        page=23,
    )
    return


if __name__ == "__main__":
    app.run()
