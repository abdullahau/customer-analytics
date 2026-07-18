# NBDDirichlet: Python vs R Implementation Comparison

## Model Parameters

|    |    R |   Python |   Difference |
|:---|-----:|---------:|-------------:|
| M  | 1.46 |     1.46 |         0    |
| K  | 0.78 |     0.78 |         0    |
| S  | 1.3  |     1.55 |         0.25 |

## Buy Summary

|                                       |    R |   Python |   Difference |
|:--------------------------------------|-----:|---------:|-------------:|
| ('Colgate DC', 'pen.brand')           | 0.2  |     0.2  |         0    |
| ('Colgate DC', 'pur.brand')           | 1.82 |     1.78 |         0.04 |
| ('Colgate DC', 'pur.cat')             | 3.16 |     3.2  |         0.04 |
| ('Macleans', 'pen.brand')             | 0.16 |     0.16 |         0    |
| ('Macleans', 'pur.brand')             | 1.76 |     1.72 |         0.04 |
| ('Macleans', 'pur.cat')               | 3.22 |     3.26 |         0.04 |
| ('Close Up', 'pen.brand')             | 0.09 |     0.09 |         0    |
| ('Close Up', 'pur.brand')             | 1.68 |     1.63 |         0.05 |
| ('Close Up', 'pur.cat')               | 3.3  |     3.35 |         0.05 |
| ('Signal', 'pen.brand')               | 0.09 |     0.09 |         0    |
| ('Signal', 'pur.brand')               | 1.68 |     1.63 |         0.05 |
| ('Signal', 'pur.cat')                 | 3.3  |     3.35 |         0.05 |
| ('ultrabrite', 'pen.brand')           | 0.08 |     0.08 |         0    |
| ('ultrabrite', 'pur.brand')           | 1.67 |     1.62 |         0.05 |
| ('ultrabrite', 'pur.cat')             | 3.31 |     3.36 |         0.05 |
| ('Gibbs SR', 'pen.brand')             | 0.07 |     0.07 |         0    |
| ('Gibbs SR', 'pur.brand')             | 1.66 |     1.61 |         0.05 |
| ('Gibbs SR', 'pur.cat')               | 3.32 |     3.37 |         0.05 |
| ('Boots Priv. Label', 'pen.brand')    | 0.03 |     0.03 |         0    |
| ('Boots Priv. Label', 'pur.brand')    | 1.62 |     1.56 |         0.06 |
| ('Boots Priv. Label', 'pur.cat')      | 3.37 |     3.43 |         0.06 |
| ('Sainsbury Priv. Lab.', 'pen.brand') | 0.02 |     0.02 |         0    |
| ('Sainsbury Priv. Lab.', 'pur.brand') | 1.61 |     1.55 |         0.06 |
| ('Sainsbury Priv. Lab.', 'pur.cat')   | 3.38 |     3.44 |         0.06 |

## Freq Summary

|                                |    R |   Python |   Difference |
|:-------------------------------|-----:|---------:|-------------:|
| ('Colgate DC', '0')            | 0.8  |     0.8  |         0    |
| ('Colgate DC', '1')            | 0.12 |     0.12 |         0    |
| ('Colgate DC', '2')            | 0.04 |     0.04 |         0    |
| ('Colgate DC', '3')            | 0.02 |     0.02 |         0    |
| ('Colgate DC', '4')            | 0.01 |     0.01 |         0    |
| ('Colgate DC', '5')            | 0    |     0    |         0    |
| ('Colgate DC', '6+')           | 0.01 |     0    |         0.01 |
| ('Macleans', '0')              | 0.84 |     0.84 |         0    |
| ('Macleans', '1')              | 0.1  |     0.1  |         0    |
| ('Macleans', '2')              | 0.03 |     0.03 |         0    |
| ('Macleans', '3')              | 0.01 |     0.01 |         0    |
| ('Macleans', '4')              | 0.01 |     0.01 |         0    |
| ('Macleans', '5')              | 0    |     0    |         0    |
| ('Macleans', '6+')             | 0    |     0    |         0    |
| ('Close Up', '0')              | 0.91 |     0.91 |         0    |
| ('Close Up', '1')              | 0.06 |     0.06 |         0    |
| ('Close Up', '2')              | 0.02 |     0.02 |         0    |
| ('Close Up', '3')              | 0.01 |     0.01 |         0    |
| ('Close Up', '4')              | 0    |     0    |         0    |
| ('Close Up', '5')              | 0    |     0    |         0    |
| ('Close Up', '6+')             | 0    |     0    |         0    |
| ('Signal', '0')                | 0.91 |     0.91 |         0    |
| ('Signal', '1')                | 0.06 |     0.06 |         0    |
| ('Signal', '2')                | 0.02 |     0.02 |         0    |
| ('Signal', '3')                | 0.01 |     0.01 |         0    |
| ('Signal', '4')                | 0    |     0    |         0    |
| ('Signal', '5')                | 0    |     0    |         0    |
| ('Signal', '6+')               | 0    |     0    |         0    |
| ('ultrabrite', '0')            | 0.92 |     0.92 |         0    |
| ('ultrabrite', '1')            | 0.05 |     0.05 |         0    |
| ('ultrabrite', '2')            | 0.02 |     0.02 |         0    |
| ('ultrabrite', '3')            | 0.01 |     0.01 |         0    |
| ('ultrabrite', '4')            | 0    |     0    |         0    |
| ('ultrabrite', '5')            | 0    |     0    |         0    |
| ('ultrabrite', '6+')           | 0    |     0    |         0    |
| ('Gibbs SR', '0')              | 0.93 |     0.93 |         0    |
| ('Gibbs SR', '1')              | 0.05 |     0.05 |         0    |
| ('Gibbs SR', '2')              | 0.01 |     0.01 |         0    |
| ('Gibbs SR', '3')              | 0.01 |     0    |         0.01 |
| ('Gibbs SR', '4')              | 0    |     0    |         0    |
| ('Gibbs SR', '5')              | 0    |     0    |         0    |
| ('Gibbs SR', '6+')             | 0    |     0    |         0    |
| ('Boots Priv. Label', '0')     | 0.97 |     0.97 |         0    |
| ('Boots Priv. Label', '1')     | 0.02 |     0.02 |         0    |
| ('Boots Priv. Label', '2')     | 0.01 |     0    |         0.01 |
| ('Boots Priv. Label', '3')     | 0    |     0    |         0    |
| ('Boots Priv. Label', '4')     | 0    |     0    |         0    |
| ('Boots Priv. Label', '5')     | 0    |     0    |         0    |
| ('Boots Priv. Label', '6+')    | 0    |     0    |         0    |
| ('Sainsbury Priv. Lab.', '0')  | 0.98 |     0.98 |         0    |
| ('Sainsbury Priv. Lab.', '1')  | 0.01 |     0.01 |         0    |
| ('Sainsbury Priv. Lab.', '2')  | 0    |     0    |         0    |
| ('Sainsbury Priv. Lab.', '3')  | 0    |     0    |         0    |
| ('Sainsbury Priv. Lab.', '4')  | 0    |     0    |         0    |
| ('Sainsbury Priv. Lab.', '5')  | 0    |     0    |         0    |
| ('Sainsbury Priv. Lab.', '6+') | 0    |     0    |         0    |

## Heavy Summary

|                                               |    R |   Python |   Difference |
|:----------------------------------------------|-----:|---------:|-------------:|
| ('Colgate DC', 'Penetration')                 | 0.34 |     0.33 |         0.01 |
| ('Colgate DC', 'Avg Purchase Freq')           | 1.61 |     1.42 |         0.19 |
| ('Macleans', 'Penetration')                   | 0.27 |     0.26 |         0.01 |
| ('Macleans', 'Avg Purchase Freq')             | 1.57 |     1.39 |         0.18 |
| ('Close Up', 'Penetration')                   | 0.15 |     0.14 |         0.01 |
| ('Close Up', 'Avg Purchase Freq')             | 1.51 |     1.34 |         0.17 |
| ('Signal', 'Penetration')                     | 0.15 |     0.14 |         0.01 |
| ('Signal', 'Avg Purchase Freq')               | 1.51 |     1.34 |         0.17 |
| ('ultrabrite', 'Penetration')                 | 0.13 |     0.13 |         0    |
| ('ultrabrite', 'Avg Purchase Freq')           | 1.5  |     1.33 |         0.17 |
| ('Gibbs SR', 'Penetration')                   | 0.12 |     0.11 |         0.01 |
| ('Gibbs SR', 'Avg Purchase Freq')             | 1.49 |     1.33 |         0.16 |
| ('Boots Priv. Label', 'Penetration')          | 0.05 |     0.04 |         0.01 |
| ('Boots Priv. Label', 'Avg Purchase Freq')    | 1.46 |     1.3  |         0.16 |
| ('Sainsbury Priv. Lab.', 'Penetration')       | 0.03 |     0.03 |         0    |
| ('Sainsbury Priv. Lab.', 'Avg Purchase Freq') | 1.45 |     1.3  |         0.15 |

## Dup Summary

|                      |    R |   Python |   Difference |
|:---------------------|-----:|---------:|-------------:|
| Colgate DC           | 1    |     1    |         0    |
| Macleans             | 0.19 |     0.2  |         0.01 |
| Close Up             | 0.1  |     0.11 |         0.01 |
| Signal               | 0.1  |     0.11 |         0.01 |
| ultrabrite           | 0.09 |     0.1  |         0.01 |
| Gibbs SR             | 0.08 |     0.09 |         0.01 |
| Boots Priv. Label    | 0.03 |     0.04 |         0.01 |
| Sainsbury Priv. Lab. | 0.02 |     0.02 |         0    |

## Notes on Comparison

1. Values are rounded to 2 decimal places for comparison.
2. Differences greater than 0.01 are highlighted for review.
3. Missing values in the Python output are indicated by 'None'.
