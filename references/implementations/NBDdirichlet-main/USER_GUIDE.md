# Dirichlet Model Web Interface: User Guide

## Introduction

The Dirichlet Model Web Interface is a powerful tool for analyzing market share and brand performance data using the Dirichlet model. This application allows you to input category and brand-level data, run the Dirichlet model, and visualize the results for both a base case and an adjusted time period.

## Getting Started

1. Open the web application in your browser.
2. You'll see input fields for category-level data and brand information.

## Input Data

### Category-Level Data
- **Category Penetration**: The proportion of the population that purchased the category at least once in the given period.
- **Category Buyer's Average Purchase Rate**: The average number of purchases made by category buyers in the given period.
- **Time Period Multiple**: An integer (1-99) representing the multiple of the base time period you want to analyze.

### Brand Information
- **Number of Brands**: Select the number of brands you want to analyze.
- For each brand, enter:
  - **Brand Name**
  - **Market Share**: The brand's share of total category sales.
  - **Penetration**: The proportion of the population that purchased the brand at least once.

## Running the Model

After entering all the data, click the "Run Dirichlet Model" button to process the information and generate results.

## Interpreting the Results

The application will display results in two main sections:

### 1. Base Case (t=1)

This section shows the results for the original time period:

- **Buy Summary**: Shows penetration, purchase frequency, and category purchase for each brand.
- **Frequency Summary**: Displays the distribution of purchase frequencies.
- **Heavy Buyers Summary**: Provides insights into the behavior of heavy category buyers.
- **Duplication Summary**: Shows the likelihood of buyers of one brand also buying other brands.
- **Dirichlet Plot**: A visual comparison of observed vs. predicted brand penetrations.
- **Model Parameters**: Displays the M, K, and S values of the Dirichlet model.

### 2. Heterogeneity Analysis

This section provides statistical measures to assess market heterogeneity:

- **Chi-square test**: Indicates if there's significant heterogeneity in the market.
- **MAPE (Mean Absolute Percentage Error)**: Measures the average percentage difference between observed and predicted values.
- **RMSE (Root Mean Square Error)**: Measures the average magnitude of prediction errors.
- **Correlation**: Shows the linear relationship between observed and predicted values.
- **Percent Differences**: Displays the percentage difference between predicted and observed penetrations for each brand.

### 3. Adjusted Case (if t > 1)

If you set a Time Period Multiple greater than 1, this section will show how the model results change over the extended time period:

- Adjusted versions of all the summaries and plots from the Base Case.
- Adjusted Category Metrics: Shows how category penetration and buying rate change over time.
- Adjusted Brand Metrics: Displays how individual brand penetrations and buying rates change over time.

## Technical Details

### Dirichlet Model Parameters

- **M**: The average number of purchases per buyer in the category.
- **K**: The shape parameter of the Negative Binomial Distribution.
- **S**: The shape parameter of the Dirichlet Distribution.

### Key Calculations

1. **Brand Penetration**: Calculated using the `brand_pen` method, which considers the probability of non-zero purchases for a brand.

2. **Brand Buy Rate**: Calculated using the `brand_buyrate` method, which considers the average number of purchases for buyers of a specific brand.

3. **Weighted Probability**: Calculated using the `wp` method, which considers the probability of purchase weighted by the number of category purchases.

4. **Chi-square Test**: Compares observed and expected brand penetrations to assess market heterogeneity.

5. **MAPE and RMSE**: Provide measures of the average difference between observed and predicted brand penetrations.

### Adjusting for Different Time Periods

When a time period multiple (t) greater than 1 is selected:

1. The M value is adjusted: `M = M0 * t`
2. The K value is re-estimated based on the new M value.
3. The S value remains unchanged.

This adjustment allows for projecting market behavior over longer time periods.

## Tips for Interpretation

- Look for discrepancies between observed and predicted values to identify potential market anomalies or brand-specific effects.
- Use the heterogeneity analysis to understand if the market follows the expected Dirichlet patterns or if there are significant deviations.
- Compare the base case with the adjusted case to understand how brand performance metrics might change over longer time periods.
- Pay attention to the chi-square test p-value: a value less than 0.05 suggests significant market heterogeneity.
- Consider MAPE values: values above 10% indicate considerable differences between observed and predicted values.

## Need Help?

If you encounter any issues or have questions about interpreting the results, please contact our support team for assistance.

## Acknowledgments

This Dirichlet Model Web Interface is based on the NBDDirichlet package, which is a Python implementation of the NBD-Dirichlet model. The NBD-Dirichlet model is a powerful tool for analyzing and predicting consumer behavior in marketing contexts.

We would like to acknowledge the contributions of the original authors and researchers whose work on the NBD-Dirichlet model forms the foundation of this application. Their pioneering efforts in the field of marketing analytics have made tools like this possible.

Special thanks to the developers and contributors of the NBDDirichlet package, whose implementation we have built upon to create this web interface.

This project stands on the shoulders of giants in the field of marketing analytics, and we are grateful for their contributions to the advancement of our understanding of consumer behavior and market dynamics.

For more information about the NBDDirichlet package and its features, please visit the project's GitHub repository or documentation page.

## License

This project is licensed under the MIT License. For more details, please refer to the LICENSE file in the project repository.
