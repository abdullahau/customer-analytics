import streamlit as st
import numpy as np
import pandas as pd
from nbddirichlet import Dirichlet, plot_dirichlet, summary_dirichlet, print_dirichlet
import io
import sys
import matplotlib.pyplot as plt

def capture_output(func, *args, **kwargs):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    func(*args, **kwargs)
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    return output

def format_number(x):
    if x == 0:
        return '-'
    elif isinstance(x, (int, float)):
        return f'{x:.2f}'
    return x

st.title('Dirichlet Model Web Interface')

# Default values from test_nbddirichlet.py
default_cat_pen = 0.56
default_cat_buyrate = 2.6
default_brand_share = [0.25, 0.19, 0.1, 0.1, 0.09, 0.08, 0.03, 0.02]
default_brand_pen_obs = [0.2, 0.17, 0.09, 0.08, 0.08, 0.07, 0.03, 0.02]
default_brand_name = ["Colgate DC", "Macleans", "Close Up", "Signal", "ultrabrite",
                      "Gibbs SR", "Boots Priv. Label", "Sainsbury Priv. Lab."]

# Input fields
cat_pen = st.number_input('Category Penetration', value=default_cat_pen, format='%.2f')
cat_buyrate = st.number_input('Category Buyer\'s Average Purchase Rate', value=default_cat_buyrate, format='%.2f')

# Add input for time period multiple
t_value = st.number_input('Time Period Multiple', value=1, min_value=1, max_value=99, step=1)

st.subheader('Brand Information')
num_brands = st.number_input('Number of Brands', min_value=1, value=len(default_brand_name), step=1)

brand_share = []
brand_pen_obs = []
brand_name = []

for i in range(int(num_brands)):
    col1, col2, col3 = st.columns(3)
    with col1:
        default_name = default_brand_name[i] if i < len(default_brand_name) else f'Brand {i+1}'
        brand_name.append(st.text_input(f'Brand {i+1} Name', value=default_name))
    with col2:
        default_share = default_brand_share[i] if i < len(default_brand_share) else 0.1
        brand_share.append(st.number_input(f'Brand {i+1} Market Share', value=default_share, format='%.2f'))
    with col3:
        default_pen = default_brand_pen_obs[i] if i < len(default_brand_pen_obs) else 0.1
        brand_pen_obs.append(st.number_input(f'Brand {i+1} Penetration', value=default_pen, format='%.2f'))

if st.button('Run Dirichlet Model'):
    # Create Dirichlet model instance for base case (t=1)
    base_dobj = Dirichlet(cat_pen, cat_buyrate, brand_share, brand_pen_obs, brand_name)

    # Generate summary statistics for base case
    base_summary = summary_dirichlet(base_dobj)

    # Format and display base summary statistics
    for key in base_summary:
        if isinstance(base_summary[key], pd.DataFrame):
            base_summary[key] = base_summary[key].map(format_number)
        elif isinstance(base_summary[key], pd.Series):
            base_summary[key] = base_summary[key].map(format_number)

    st.header('Base Case (t=1)')

    st.subheader('Buy Summary')
    st.dataframe(base_summary['buy'])

    st.subheader('Frequency Summary')
    st.dataframe(base_summary['freq'])

    st.subheader('Heavy Buyers Summary')
    st.dataframe(base_summary['heavy'])

    st.subheader('Duplication Summary')
    st.dataframe(base_summary['dup'])

    # Plot results for base case
    st.subheader('Dirichlet Plot (Base Case)')
    base_fig = plot_dirichlet(base_dobj)
    st.pyplot(base_fig)

    # Display base M, K, and S values
    st.write(f"Base M value: {base_dobj.M:.2f}")
    st.write(f"Base K value: {base_dobj.K:.2f}")
    st.write(f"Base S value: {base_dobj.S:.2f}")

    # Heterogeneity Analysis
    st.subheader('Heterogeneity Analysis')
    try:
        chi2, p_value = base_dobj.chi_square_test()
        st.write(f"Chi-square statistic: {chi2:.4f}")
        st.write(f"p-value: {p_value:.4f}")
    except ValueError as e:
        st.write("Chi-square test could not be performed due to frequency mismatch.")
        st.write(f"Error details: {str(e)}")

    st.write(f"MAPE: {base_dobj.mape():.2f}%")
    st.write(f"RMSE: {base_dobj.rmse():.4f}")
    st.write(f"Correlation: {base_dobj.correlation():.4f}")

    # Display percent differences
    st.subheader('Percent Differences (Predicted - Observed)')
    percent_diff = base_dobj.percent_differences()
    st.dataframe(percent_diff.map(lambda x: f"{x:.2f}%"))

    # Interpretation
    if 'p_value' in locals():
        if p_value < 0.05:
            st.write("The chi-square test suggests significant heterogeneity in the market (p < 0.05).")
        else:
            st.write("The chi-square test does not indicate significant heterogeneity in the market (p >= 0.05).")

    if base_dobj.mape() > 10:
        st.write("The MAPE is relatively high, suggesting considerable differences between observed and predicted values.")
    else:
        st.write("The MAPE is relatively low, suggesting good agreement between observed and predicted values.")

    # If t > 1, show additional output for the user-selected time period
    if t_value > 1:
        st.header(f'Adjusted Case (t={t_value})')

        # Create Dirichlet model instance for adjusted case
        adj_dobj = Dirichlet(cat_pen, cat_buyrate, brand_share, brand_pen_obs, brand_name)
        adj_dobj.period_set(t_value)

        # Generate summary statistics for adjusted case
        adj_summary = summary_dirichlet(adj_dobj)

        # Format and display adjusted summary statistics
        for key in adj_summary:
            if isinstance(adj_summary[key], pd.DataFrame):
                adj_summary[key] = adj_summary[key].map(format_number)
            elif isinstance(adj_summary[key], pd.Series):
                adj_summary[key] = adj_summary[key].map(format_number)

        st.subheader('Adjusted Buy Summary')
        st.dataframe(adj_summary['buy'])

        st.subheader('Adjusted Frequency Summary')
        st.dataframe(adj_summary['freq'])

        st.subheader('Adjusted Heavy Buyers Summary')
        st.dataframe(adj_summary['heavy'])

        st.subheader('Adjusted Duplication Summary')
        st.dataframe(adj_summary['dup'])

        # Plot results for adjusted case
        st.subheader(f'Dirichlet Plot (t={t_value})')
        adj_fig = plot_dirichlet(adj_dobj)  # Pass the adjusted Dirichlet object
        st.pyplot(adj_fig)

        # Display adjusted M, K, and S values
        st.write(f"Adjusted M value: {adj_dobj.M:.2f}")
        st.write(f"Adjusted K value: {adj_dobj.K:.2f}")
        st.write(f"S value: {adj_dobj.S:.2f} (unchanged)")

        # Display adjusted category metrics
        st.subheader('Adjusted Category Metrics')
        adjusted_cat_pen = 1 - (1 - adj_dobj.cat_pen) ** t_value
        adjusted_cat_buyrate = adj_dobj.M / adjusted_cat_pen
        st.write(f"Adjusted Category Penetration: {adjusted_cat_pen:.4f}")
        st.write(f"Adjusted Category Buy Rate: {adjusted_cat_buyrate:.4f}")

        # Display adjusted brand metrics
        st.subheader('Adjusted Brand Metrics')
        adjusted_brand_metrics = pd.DataFrame({
            'Brand': adj_dobj.brand_name,
            'Adjusted Penetration': [adj_dobj.brand_pen(j) for j in range(adj_dobj.nbrand)],
            'Adjusted Buy Rate': [adj_dobj.brand_buyrate(j) for j in range(adj_dobj.nbrand)]
        })
        st.dataframe(adjusted_brand_metrics.set_index('Brand').map(format_number))