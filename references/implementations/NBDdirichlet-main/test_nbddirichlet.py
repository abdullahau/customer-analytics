import numpy as np
from nbddirichlet import Dirichlet, plot_dirichlet, summary_dirichlet, print_dirichlet

# Input data from the R example
cat_pen = 0.56  # Category Penetration
cat_buyrate = 2.6  # Category Buyer's Average Purchase Rate in a given period
brand_share = [0.25, 0.19, 0.1, 0.1, 0.09, 0.08, 0.03, 0.02]  # Brands' Market Share
brand_pen_obs = [0.2, 0.17, 0.09, 0.08, 0.08, 0.07, 0.03, 0.02]  # Brand Penetration
brand_name = ["Colgate DC", "Macleans", "Close Up", "Signal", "Ultrabrite",
              "Gibbs SR", "Boots Priv. Label", "Sainsbury Priv. Lab."]

# Create Dirichlet model instance
dobj = Dirichlet(cat_pen, cat_buyrate, brand_share, brand_pen_obs, brand_name, t=8)

# Print model parameters for the base time period
print("Base Time Period:")
print_dirichlet(dobj)
print(f"M: {dobj.M:.2f}, K: {dobj.K:.3f}, S: {dobj.S:.3f}")

# Generate and print summary statistics for the base time period
summary = summary_dirichlet(dobj)
print("\nBase Time Period Summary:")
print(summary['buy'])

# Adjust the time period (e.g., to 8 quarters)
dobj.period_set(t=2)

# Print the adjusted values
print(f"\nAdjusted Time Period (t={dobj.t}):")
print_dirichlet(dobj)
print(f"M: {dobj.M:.2f}, K: {dobj.K:.3f}, S: {dobj.S:.3f}")

# Generate and print summary statistics for the adjusted time period
summary_adjusted = summary_dirichlet(dobj)
print("\nAdjusted Time Period Summary:")
print(summary_adjusted['buy'])

# Compare base and adjusted summaries
print("\nDifferences between Base and Adjusted Summaries:")
diff = summary_adjusted['buy'] - summary['buy']
print(diff)

# Plot results for the adjusted time period
plot_dirichlet(dobj)