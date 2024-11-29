## 5. Creating a "Shifted" Transactions Summary

and copy it down to cell F359 (NB: not F307). The shifted week variable is created by adding this offset to the value of the Week field. In cell G2 we type the formula $=\mathrm{B} 2+\mathrm{F} 2$ and copy it down to cell G359. The corresponding records for panelists 20014 and 20069 are given in Figure 8. We observe that the desired "shifting" of purchase dates has occurred.

The next step is to create a table that tells us how many trial, first repeat, etc. purchases occurred in each week. We create a pivot table in which we use shWeek as the row field, DoR as the column field, and ID as the data item. (Don't forget to include the records with a depth-of-repeat level of -1.$)$ The resulting table is reported in the Pivot Table 3 worksheet. A cleaned-up summary that reports these weekly transactions in cumulative form is given in the DoR -- 'shifted'' transactions worksheet.

|  | A | B | C | D | E | F | G |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | ID | Week | Day | Units | DoR | Offset | shWeek |
| 16 | 20014 | 4 | 2 | 1 | 0 | 0 | 4 |
| 17 | 20014 | 4 | 4 | 1 | 1 | 1 | 5 |
| 18 | 20014 | 6 | 6 | 2 | 2 | 0 | 6 |
| 19 | 20014 | 7 | 2 | 3 | 3 | 0 | 7 |
| 20 | 20014 | 7 | 6 | 3 | 4 | 1 | 8 |
| 21 | 20014 | 12 | 5 | 2 | 5 | 0 | 12 |
| 22 | 20014 | 17 | 6 | 1 | 6 | 0 | 17 |
| 23 | 20014 | 23 | 4 | 2 | 7 | 0 | 23 |
| 24 | 20014 | 47 | 6 | 2 | 8 | 0 | 47 |
| 148 | 20069 | 18 | 1 | 1 | 0 | 0 | 18 |
| 149 | 20069 | 18 | 5 | 1 | 1 | 1 | 19 |
| 150 | 20069 | 19 | 4 | 2 | 2 | 1 | 20 |

Figure 8: "Shifted" Transaction Histories for Panelists 20014 and 20069

The differences between the "raw" and "shifted" cumulative transaction counts by depth-of-repeat level are small; there are only nine depth-of-repeat/week occasions on which the two sets of numbers differ, and the maximum deviation is one transaction. Perhaps the most obvious difference is with respect to first repeat. Looking at the "raw" numbers, we observe a first repeat purchase in the first week the product was on the market. Under the assumption that a trial and first repeat purchase cannot occur in the same week, this first repeat purchase is shifted to week 2 in the "shifted" numbers.

Now, how do we create a "shifted" sales volume summary? That should be obvious by now ... and is left as an exercise for the interested reader.

## References

Clarke, Darral G. (1984), "G. D. Searle \& Co.: Equal Low-Calorie Sweetener (B)," Harvard Business School Case 9-585-011.

Eskin, Gerald J. (1973), "Dynamic Forecasts of New Product Demand Using a Depth of Repeat Model," Journal of Marketing Research, 10 (May), 115-129.

Fader, Peter S. and Bruce G. S. Hardie (2004), "The Value of Simple Models in New Product Forecasting and Customer-Base Analysis," Applied Stochastic Models in Business and Industry, forthcoming.
Parfitt, John (1986), "Panel Research," in Robert M. Worcester and John Downham (eds.), Consumer Market Research Handbook, third revised and enlarged edition, London: McGraw-Hill.

Rangan, V. Kasturi and Marie Bell (1994), "Nestlé Refrigerated Foods: Contadina Pasta \& Pizza (A)," Harvard Business School Case 9-595-035.

Sudman, Seymour and Brian Wansink (2002), Consumer Panels, second edition, Chicago, IL: American Marketing Association.
