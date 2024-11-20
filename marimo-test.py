import marimo

__generated_with = "0.9.20"
app = marimo.App(layout_file="layouts/marimo-test.grid.json")


@app.cell
def __():
    import marimo as mo

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    from scipy.optimize import minimize
    from scipy.stats import beta
    return PercentFormatter, beta, minimize, mo, np, plt


@app.cell(hide_code=True)
def __(mo):
    mo.md("""### Probability Distribution Plotting""")
    return


@app.cell
def __(beta, np, plt):
    gamma1, delta1 = np.array([0.5, 1.5]), np.array([3, 0.5])

    x = np.linspace(beta.ppf(0, gamma1[0], delta1[0]), beta.ppf(1, gamma1[0], delta1[0]), 100)
    fig, axes = plt.subplots(2, 2, figsize=(7,6))
    for i in range(2):
        for j in range(2):
            ax = axes[i][j]
            ax.plot(x, beta.pdf(x, gamma1[i], delta1[j]), label=f'γ={gamma1[i]}, δ={delta1[j]}', color='black', lw=0.75)
            ax.set_xlim(0,1)
            ax.set_xlabel('θ')
            ax.legend(fontsize=6)

    ax
    return ax, axes, delta1, fig, gamma1, i, j, x


@app.cell
def __(np):
    year, alive = np.loadtxt('data/hardie-sample-retention.csv', dtype='object', delimiter=',', unpack=True, skiprows=1) 
    year = year.astype(int)
    alive = alive.astype(float)
    train_year = year[:5]
    train_alive = alive[:5]
    return alive, train_alive, train_year, year


@app.cell
def __(minimize, np, train_alive, train_year):
    def log_likelihood(x):
        gamma, delta = x[0], x[1]
        
        p_churn = np.zeros_like(train_alive[1:])
        p_churn[0] = gamma / (gamma + delta) # Define the base probability for t=1
        terms = (delta + train_year[2:] - 2) / (gamma + delta + train_year[2:] - 1) # Define the sequence for t=2,3, ...
        p_churn[1:] = np.cumprod(terms) * p_churn[0] # Calculate cumulative products for probabilities
        
        n_lost = train_alive[:-1] - train_alive[1:]
        ll_churn = np.sum(n_lost * np.log(p_churn))
        ll_alive = train_alive[-1] * np.log(1-np.sum(p_churn))
        return -(ll_churn + ll_alive)

    guess = [1, 1]
    bnds = [(0, np.inf), (0, np.inf)]
    result = minimize(log_likelihood, guess, bounds=bnds)
    gamma, delta = result.x[0], result.x[1]
    ll = -result.fun
    print(f'γ = {gamma:.3f}\nδ = {delta:.3f}\nLog-Likelihood = {ll:,.2f}')
    return bnds, delta, gamma, guess, ll, log_likelihood, result


@app.cell
def __(PercentFormatter, alive, delta, gamma, np, plt, year):
    train_marker_x = [5 for _ in np.arange(0,1.2,0.1)]
    train_marker_y = [_ for _ in np.arange(0,1.2,0.1)]

    retention = alive / alive[0]
    p_churn = np.zeros_like(alive)
    p_churn[1] = gamma / (gamma + delta)
    terms = (delta + year[2:] - 2) / (gamma + delta + year[2:] - 1)
    p_churn[2:] = np.cumprod(terms) * p_churn[1]

    e_retention = np.ones_like(alive)
    for t in range(1, len(alive)):
        e_retention[t] = e_retention[t - 1] - p_churn[t]

    plt.figure(figsize=(8,4), dpi=100)
    plt.plot(retention, "b-o", label='Actual')
    plt.plot(e_retention, "r--o", label='Predicted - sBG')
    plt.plot(train_marker_x, train_marker_y, "k-", linewidth=0.5)
    plt.title('Shifted Beta Geometric (sBG) - Survival Curve Projection')
    plt.xlabel("Tenure (years)")
    plt.ylabel("% Surviving")
    plt.ylim(0,1.1)
    plt.legend()
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.gca()
    return (
        e_retention,
        p_churn,
        retention,
        t,
        terms,
        train_marker_x,
        train_marker_y,
    )


if __name__ == "__main__":
    app.run()
