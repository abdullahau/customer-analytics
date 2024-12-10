import polars as pl
import numpy as np

CDNOW_sample = (
    pl.scan_csv(source='data/CDNOW/CDNOW_sample.csv',
                has_header=False,
                separator=',',
                schema={'CustID': pl.Int32,
                        'NewID': pl.Int32,
                        'Date': pl.String,
                        'Quant': pl.Int16,
                        'Spend': pl.Float64})
    .with_columns(pl.col('Date').str.to_date("%Y%m%d"))
    .with_columns((pl.col('Date') - pl.date(1996,12,31)).dt.total_days().cast(pl.UInt16).alias('PurchDay'))
    .with_columns((pl.col('Spend')*100).round(0).cast(pl.Int64).alias('Spend Scaled'))
    .group_by('CustID', 'Date')
    .agg(pl.col('*').exclude('PurchDay').sum(), pl.col('PurchDay').max())
    .sort('CustID', 'Date')
    .with_columns((pl.col("CustID").cum_count().over("CustID") - 1).cast(pl.UInt16).alias("DoR"))      
)

sample_TransMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='PurchDay', aggregate_function='max', maintain_order=True)
    .fill_null(0)
)

sample_QuantMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='Quant', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
)

sample_SpendMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='Spend Scaled', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
)


# The number of repeat transactions made by each customer in each period
calwk = 273 # 39 week calibration period
NumHH = len(sample_TransMAT)

# The number of repeat transactions made by each customer in each period
TransMAT = sample_TransMAT.to_numpy()
QuantMAT = sample_QuantMAT.to_numpy()
SpendMAT = sample_SpendMAT.to_numpy()

p1x = np.sum(((TransMAT[:,2:] > 0) & (TransMAT[:,2:] <= calwk)), axis=1, keepdims=True)
p2x = np.sum(((TransMAT[:,2:] > 0) & (TransMAT[:,2:] > calwk)), axis=1, keepdims=True)

# The number of CDs purchased and total spend across these repeat transactions
p1Quant = np.zeros((NumHH, 1), dtype=np.int16)
p2Quant = np.zeros((NumHH, 1), dtype=np.int16)
p1Spend = np.zeros((NumHH, 1), dtype=np.int64)
p2Spend = np.zeros((NumHH, 1), dtype=np.int64)

for i in range(NumHH):
    if p1x[i,0] == 0:
        p1Quant[i] = 0
        p1Spend[i] = 0
    else:
        p1Quant[i] = np.sum(QuantMAT[i, 2:2+p1x[i,0]])
        p1Spend[i] = np.sum(SpendMAT[i, 2:2+p1x[i,0]])
    p2Quant[i] = np.sum(QuantMAT[i,2+p1x[i,0]:])
    p2Spend[i] = np.sum(SpendMAT[i,2+p1x[i,0]:])
    
# The average spend per repeat transaction
mx = np.zeros((NumHH, 1))
tmpindx = p1x > 0
mx[tmpindx] = p1Spend[tmpindx] / p1x[tmpindx]


# time of last calibration period repeat purchase (in weeks)
tx = np.zeros((NumHH, 1), dtype=np.int16)
for i in range(NumHH):
    tx[i] = TransMAT[i, 1+p1x[i,0]] - TransMAT[i, 1]
tx = tx/7
# effective calibration period (in weeks)
T = (calwk - TransMAT[:, 1])/7
T.reshape(-1, 1)