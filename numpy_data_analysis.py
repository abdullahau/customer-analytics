import polars as pl
import numpy as np

# Dataset Sample & Its Summaries

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

TransMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='PurchDay', aggregate_function='max', maintain_order=True)
    .fill_null(0)
    .to_numpy()    
)

QuantMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='Quant', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
    .to_numpy()    
)

SpendMAT = (
    CDNOW_sample
    .collect()
    .pivot(on='DoR', index='CustID', values='Spend Scaled', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
    .to_numpy()
)


# The number of repeat transactions made by each customer in each period
calwk = 273 # 39 week calibration period
NumHH = len(TransMAT)

# The number of repeat transactions made by each customer in each period
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
T = ((calwk - TransMAT[:, 1])/7).reshape(-1,1)

# Master Dataset Summaries
CDNOW_master = (
    pl.scan_csv(source = 'data/CDNOW/CDNOW_master.csv', 
                has_header=False, 
                separator=',', 
                schema={'CustID': pl.Int32,     # customer id
                        'Date': pl.String,      # transaction date
                        'Quant': pl.Int16,      # number of CDs purchased
                        'Spend': pl.Float64})   # dollar value (excl. S&H)
    .with_columns(pl.col('Date').str.to_date("%Y%m%d"))
    .with_columns((pl.col('Date') - pl.date(1996,12,31)).dt.total_days().cast(pl.UInt16).alias('PurchDay'))
    .with_columns((pl.col('Spend')*100).round(0).cast(pl.Int64).alias('Spend Scaled'))
    .group_by('CustID', 'Date')
    .agg(pl.col('*').exclude('PurchDay').sum(), pl.col('PurchDay').max()) # Multiple transactions by a customer on a single day are aggregated into one
    .sort('CustID', 'Date')
    .with_columns((pl.col("CustID").cum_count().over("CustID") - 1).cast(pl.UInt16).alias("DoR"))    
)

master_TransMAT = (
    CDNOW_master
    .collect()
    .pivot(on='DoR', index='CustID', values='PurchDay', aggregate_function='max', maintain_order=True)
    .fill_null(0)
    .to_numpy()    
)

master_QuantMAT = (
    CDNOW_master
    .collect()
    .pivot(on='DoR', index='CustID', values='Quant', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
    .to_numpy()    
)

master_SpendMAT = (
    CDNOW_master
    .collect()
    .pivot(on='DoR', index='CustID', values='Spend Scaled', aggregate_function='sum', maintain_order=True)
    .fill_null(0)
    .to_numpy()
)

NumCust = len(master_TransMAT)
MaxPurchNum = master_TransMAT.shape[1] - 1

# Compute total spend for each customer - Vectorized Method in Numpy - Using Masks
# Step 1: Calculate x (number of valid transactions)
x = np.sum(((master_TransMAT[:, 2:] > 0) & (master_TransMAT[:, 2:] <= 273)), axis=1, dtype='int16')
# Step 2: Create a mask to include only valid columns for each customer
mask = ((master_TransMAT[:, 2:] > 0) & (master_TransMAT[:, 2:] <= 273))  # Exclude ID Column & Trial
RptSpend = np.sum(master_SpendMAT[:,2:] * mask, axis=1, dtype='float64')


# What is the total number of CDs purchased each week?
TotQuant = np.zeros((78,1))
for i in range(1, 79):
    weekQuant = np.zeros((NumCust,1))
    for j in range(1, MaxPurchNum+1):
        isbuyer = np.where((master_TransMAT[:,j] > (7*(i-1))) & (master_TransMAT[:,j] <= (7*i)))[0]
        weekQuant[isbuyer] += master_QuantMAT[isbuyer,j].reshape(-1,1)
    TotQuant[i-1] = np.sum(weekQuant)

# How many people made their first-ever (“trial”) purchase each week?
NumTriers = np.zeros((12,1))
for i in range(12):
    istrier = np.where((master_TransMAT[:,1] > (7*i)) & (master_TransMAT[:,1] <= (7*(i+1))))[0]
    NumTriers[i] = len(istrier)

# What is the total number of CDs purchased by triers in their trial week?
TrialQuant = np.zeros((12,1))
for i in range(12):
    istrier = np.where((master_TransMAT[:, 1] > 7 * i) & (master_TransMAT[:, 1] <= 7 * (i + 1)))[0]    
    for j in range(len(istrier)):
        not_done = True
        k = 1
        while not_done:
            TrialQuant[i] += master_QuantMAT[istrier[j],k]     
            not_done = (master_TransMAT[istrier[j], k+1] > (7 * i)) & (master_TransMAT[istrier[j], k+1] <= (7 * (i + 1)))     
            k += 1

# What is the distribution of the number of units purchased in each of the first 12 weeks?
weekQuant = np.zeros((NumCust, 12), dtype=np.int32)
for i in range(12):
    for k in range(1, MaxPurchNum+1):
        isbuyer = np.where((master_TransMAT[:,k] > (7*i)) & (master_TransMAT[:,k] <= (7*(i+1))))[0]
        weekQuant[isbuyer, i] += master_QuantMAT[isbuyer,k]

MaxQuant = np.max(weekQuant)     
QuantDist = np.zeros((MaxQuant, 12), dtype=np.int32)
for i in range(12):
    counts, _ = np.histogram(weekQuant[:, i], bins=np.arange(1, MaxQuant + 2))
    QuantDist[:,i] = counts

TableOne = np.zeros((11,12), dtype=np.int32)
TableOne[1:10,:] = QuantDist[0:9,:]
TableOne[10,:] = np.sum(QuantDist[9:,:], axis=0)
TableOne[0,:] = np.cumsum(NumTriers) - np.sum(TableOne[1:,:], axis=0)