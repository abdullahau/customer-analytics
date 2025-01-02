### Pandas Group By & Aggregate - Method 1

```python
acquired = df.sort_values(by=['cust_id', 'order_date'])
acquired['initial_purch'] = (~acquired['cust_id'].duplicated()).astype(int)
acquired['repeat_purch'] = (acquired['cust_id'].duplicated()).astype(int)
grouped = acquired.groupby([acquired.index.year, acquired.index.month]).agg({
    'initial_purch': 'sum',
    'repeat_purch': 'sum'
})
```

### Pandas Group By & Aggregate - Method 2

```python
acquired = df.sort_values(by=['cust_id', 'order_date'])
acquired['initial_purch'] = (~acquired['cust_id'].duplicated())
grouped = acquired.groupby([acquired.index.year, acquired.index.month, acquired['initial_purch']])['initial_purch'].count()
```

### Pandas Group By 'Quarter'

```python
df.groupby(df['birthday'].dt.to_period('Q'))['net_sales'].sum()
df.groupby(df.index.to_period('Q'))['net_sales'].sum()

# cross-tabular grouping with both axis as dates, each measured at quarters
test = df.groupby([df['birthday'].dt.to_period('Q'), df.index.to_period('Q')])['net_sales'].sum()
test.unstack()
```