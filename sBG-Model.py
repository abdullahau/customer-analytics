import marimo

__generated_with = "0.9.20"
app = marimo.App(layout_file="layouts/sBG-model.grid.json")


@app.cell(hide_code=True)
def __():
    import marimo as mo

    import numpy as np
    from scipy.optimize import minimize
    from scipy.stats import beta
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import io

    np.set_printoptions(legacy='1.25')
    return beta, go, io, minimize, mo, np, plt


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        """
        ## Customer Retention Model 1: Shifted Beta Geometric (sBG)
        _Discrete-time, contractual setting retention model_

        This model works best for subscription-like businesses where the customer relationship is contractual and that contract is renewed periodically over months, quarters, or years.
        """
    )
    return


@app.cell(hide_code=True)
def __(mo):
    upload = mo.ui.file(kind="button")

    period = mo.ui.dropdown(options=['Years', 'Months'],
                           value='Years',
                           label='Choose Renewal Period:')

    mo.vstack([upload, period])
    return period, upload


@app.cell(hide_code=True)
def __(io, mo, np, period, upload):
    try:
        file = io.StringIO(upload.contents().decode())
    except AttributeError:
        file = 'data/hardie-sample-retention.csv'

    cohort_period, cohort_alive = np.loadtxt(file,
                              dtype='f8',
                              delimiter=',',
                              unpack=True,
                              skiprows=1)

    mo.md(f"#### **{period.value}**: {list(cohort_period)}\n #### **Customers Alive**: {list(cohort_alive)}")
    return cohort_alive, cohort_period, file


@app.cell(hide_code=True)
def __(cohort_period, mo, period):
    train_range = mo.ui.slider(steps=list(cohort_period),
                               show_value=True,
                               value=5,
                               label=f'Select Model Training Period ({period.value})')

    train_range
    return (train_range,)


@app.cell(hide_code=True)
def __(cohort_alive, cohort_period, mo, period, train_range):
    train_period = cohort_period[:int(train_range.value)]
    train_alive = cohort_alive[:int(train_range.value)]


    mo.md(f"#### **{period.value}**: {list(train_period)}\n #### **Customers Alive**: {list(train_alive)}")
    return train_alive, train_period


@app.cell(hide_code=True)
def __(minimize, np):
    def sBG(alive: np.array, period: np.array, guess=[1,1]) -> tuple(float, float): # type: ignore

        def log_likelihood(x):
            gamma, delta = x[0], x[1]

            p_churn = np.zeros_like(alive[1:], dtype=float)
            p_churn[0] = gamma / (gamma + delta) # Define the base probability for t=1
            terms = (delta + period[2:] - 2) / (gamma + delta + period[2:] - 1) # Define the sequence for t=2,3, ...
            p_churn[1:] = np.cumprod(terms) * p_churn[0] # Calculate cumulative products for probabilities

            n_lost = alive[:-1] - alive[1:]
            ll_churn = np.sum(n_lost * np.log(p_churn))
            ll_alive = alive[-1] * np.log(1-np.sum(p_churn))
            return -(ll_churn + ll_alive)

        bnds = [(0, np.inf), (0, np.inf)]

        return minimize(log_likelihood, guess, bounds=bnds)
    return (sBG,)


@app.cell(hide_code=True)
def __(mo, sBG, train_alive, train_period):
    result = sBG(train_alive, train_period)
    gamma, delta = result.x[0], result.x[1]
    ll = -result.fun

    mo.md(f" ### **Output**:\n ### γ = {gamma:.3f}\n ### δ = {delta:.3f}\n ### Log-Likelihood = {ll:,.2f}")
    return delta, gamma, ll, result


@app.cell(hide_code=True)
def __(mo):
    mo.md("""### Model Plots""")
    return


@app.cell(hide_code=True)
def __(cohort_alive, cohort_period, delta, gamma, go, np, period):
    # Data preparation
    train_marker_x = [5 for _ in np.arange(0, 1.2, 0.1)]
    train_marker_y = [_ for _ in np.arange(0, 1.2, 0.1)]

    retention = cohort_alive / cohort_alive[0]
    p_churn = np.zeros_like(cohort_alive, dtype=float)
    p_churn[1] = gamma / (gamma + delta)
    terms = (delta + cohort_period[2:] - 2) / (gamma + delta + cohort_period[2:] - 1)
    p_churn[2:] = np.cumprod(terms) * p_churn[1]

    e_retention = np.ones_like(cohort_alive, dtype=float)
    for t in range(1, len(cohort_alive)):
        e_retention[t] = e_retention[t - 1] - p_churn[t]

    # Create the plot
    survivalfig = go.Figure()

    # Plot actual retention
    survivalfig.add_trace(go.Scatter(
        x=np.arange(len(retention)),
        y=retention,
        mode='lines+markers',
        line=dict(color='blue'),
        marker=dict(symbol='circle'),
        name='Actual'
    ))

    # Plot predicted retention
    survivalfig.add_trace(go.Scatter(
        x=np.arange(len(e_retention)),
        y=e_retention,
        mode='lines+markers',
        line=dict(dash='dash', color='red'),
        marker=dict(symbol='circle'),
        name='Predicted - sBG'
    ))

    # Plot train marker line
    survivalfig.add_trace(go.Scatter(
        x=train_marker_x,
        y=train_marker_y,
        mode='lines',
        line=dict(color='black', width=0.5),
        name='Train Marker'
    ))

    # Update layout for styling
    survivalfig.update_layout(
        title="Shifted Beta Geometric (sBG) - Survival Curve Projection",
        xaxis_title=f"Tenure ({period.value})",
        yaxis_title="% Surviving",
        yaxis=dict(range=[0, 1.1], tickformat=".0%"),
        legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
        template='plotly_white'
    )
    return (
        e_retention,
        p_churn,
        retention,
        survivalfig,
        t,
        terms,
        train_marker_x,
        train_marker_y,
    )


@app.cell(hide_code=True)
def __(cohort_alive, cohort_period, e_retention, go, period):
    # Data preparation
    rr = cohort_alive[1:] / cohort_alive[:-1]
    e_alive = cohort_alive[0] * e_retention
    e_rr = e_alive[1:] / e_alive[:-1]

    # Create the plot
    retentionplot = go.Figure()

    # Plot actual retention rate
    retentionplot.add_trace(go.Scatter(
        x=cohort_period[1:],  # Exclude the first year as per the slicing
        y=rr,
        mode='lines',
        line=dict(color='blue'),
        name='Actual'
    ))

    # Plot predicted retention rate
    retentionplot.add_trace(go.Scatter(
        x=cohort_period[1:],
        y=e_rr,
        mode='lines',
        line=dict(color='red'),
        name='Predicted - sBG'
    ))

    # Update layout for styling
    retentionplot.update_layout(
        title="Actual Versus Model-Based Estimates of Retention Rates by Tenure",
        xaxis_title=f"Tenure ({period.value})",
        yaxis_title="Retention Rate (%)",
        yaxis=dict(tickformat=".0%"),  # Format as percentages
        legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
        template='plotly_white'
    )
    return e_alive, e_rr, retentionplot, rr


@app.cell(hide_code=True)
def __(beta, delta, gamma, go, np):
    # Generate x and y values for the beta distribution
    x = np.linspace(beta.ppf(0, gamma, delta), beta.ppf(0.999, gamma, delta), 300)
    y = beta.pdf(x, gamma, delta)

    # Create the plot
    churn_dist = go.Figure()

    # Add the beta distribution curve
    churn_dist.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        line=dict(color='blue'),
        name=f'γ={gamma:0.3f}, δ={delta:0.3f}, E(Θ)={gamma/(gamma+delta):.3f}'
    ))

    # Update layout for styling
    churn_dist.update_layout(
        title='Beta Distribution PDF',
        xaxis_title='θ',
        yaxis_title='g(θ)',
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 3]),
        legend=dict(font=dict(size=11), x=0.5, y=1.1, xanchor="center"),
        template='plotly_white'
    )
    return churn_dist, x, y


@app.cell(hide_code=True)
def __(go, np, train_alive, train_period):
    def log_likelihood(gamma, delta):

        p_churn = np.zeros_like(train_alive[1:], dtype=float)
        p_churn[0] = gamma / (gamma + delta) # Define the base probability for t=1
        terms = (delta + train_period[2:] - 2) / (gamma + delta + train_period[2:] - 1) # Define the sequence for t=2,3, ...
        p_churn[1:] = np.cumprod(terms) * p_churn[0] # Calculate cumulative products for probabilities

        n_lost = train_alive[:-1] - train_alive[1:]
        ll_churn = np.sum(n_lost * np.log(p_churn))
        ll_alive = train_alive[-1] * np.log(1-np.sum(p_churn))
        return (ll_churn + ll_alive)

    # Generate data
    gammas = np.linspace(0.02, 2, 50)
    deltas = np.linspace(0.51, 2.5, 50)
    delta_grid, gamma_grid = np.meshgrid(deltas, gammas)
    lls = np.vectorize(log_likelihood)(gamma_grid, delta_grid)

    # Create the 3D surface plot
    fig3d = go.Figure(data=[go.Surface(
        x=gamma_grid,
        y=delta_grid,
        z=lls,
        colorscale='Rainbow',
        showscale=True,
        contours={
            "z": {"show": True, "start": -3600, "end": -1400, "size": 500}
        }
    )])

    # Update layout to match the Matplotlib version
    fig3d.update_layout(
        title='Surface Plot of Beta Geometric Log-Likelihood Function',
        scene=dict(
            xaxis_title='γ',
            yaxis_title='δ',
            zaxis_title='LL',
            xaxis=dict(range=[0, 2]),
            yaxis=dict(range=[0.5, 2.5]),
            zaxis=dict(range=[-3600, -1400], tickvals=[-3400, -2900, -2400, -1900, -1400]),
        ),
        margin=dict(l=0, r=0, b=15, t=40),
    )

    # Adjust the camera view
    camera = dict(
        up=dict(x=0, y=0, z=1.5),
        center=dict(x=0, y=0, z=-0.1),
        eye=dict(x=-1.15, y=-1.6, z=1.0)
    )

    fig3d.update_layout(scene_camera=camera)
    return (
        camera,
        delta_grid,
        deltas,
        fig3d,
        gamma_grid,
        gammas,
        lls,
        log_likelihood,
    )


@app.cell(hide_code=True)
def __(delta_grid, gamma_grid, lls, np, plt):
    min_ll, max_ll = np.min(lls), np.max(lls)
    levels = max_ll - np.geomspace(1, max_ll - min_ll + 1, num=15)
    levels = np.sort(levels)

    contour_plot = plt.contour(gamma_grid, delta_grid, lls, levels=levels, linewidths=0.75)
    plt.clabel(contour_plot, fontsize=8)
    plt.xlabel('γ')
    plt.ylabel('δ')
    plt.title('Contour Plot of Beta Geometric Log-Likelihood Function')
    return contour_plot, levels, max_ll, min_ll


@app.cell(hide_code=True)
def __(mo):
    mo.md("""### Explore Beta Distribution PDF""")
    return


@app.cell(hide_code=True)
def __(mo):
    gamma_slider = mo.ui.slider(start=0, stop=6, step=0.001, label='Gamma', value=1.5)
    delta_slider = mo.ui.slider(start=0, stop=6, step=0.001, label='Delta', value=4.5)

    mo.vstack(
        [
            gamma_slider,
            delta_slider
        ],
        align = 'start'
    )
    return delta_slider, gamma_slider


@app.cell(hide_code=True)
def __(beta, delta_slider, gamma_slider, go, np):
    theta_x = np.linspace(beta.ppf(0, gamma_slider.value, delta_slider.value), beta.ppf(0.999, gamma_slider.value, delta_slider.value), 100)
    pdf_y = beta.pdf(theta_x, gamma_slider.value, delta_slider.value)

    beta_dist = go.Figure()

    beta_dist.add_trace(go.Scatter(
        x=theta_x,
        y=pdf_y,
        mode='lines',
        line=dict(color='blue'),
        name='Beta PDF'
    ))

    # Update layout for styling
    beta_dist.update_layout(
        title="Beta Distribution",
        xaxis_title='Theta',
        yaxis_title='PDF',
        template='plotly_white'
    )
    return beta_dist, pdf_y, theta_x


if __name__ == "__main__":
    app.run()
