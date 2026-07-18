# plot_dirichlet
import matplotlib.pyplot as plt
import numpy as np

def plot_dirichlet(dobj):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(dobj.nbrand)
    width = 0.35

    observed = dobj.brand_pen_obs
    predicted = [dobj.brand_pen(j) for j in range(dobj.nbrand)]

    ax.bar(x - width/2, observed, width, label='Observed')
    ax.bar(x + width/2, predicted, width, label='Predicted')

    ax.set_ylabel('Penetration')
    ax.set_title(f'Observed vs Predicted Brand Penetration (t={dobj.M/dobj.M0:.1f})')
    ax.set_xticks(x)
    ax.set_xticklabels(dobj.brand_name, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    return fig