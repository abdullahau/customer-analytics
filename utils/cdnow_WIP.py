import polars as pl
import os 


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Constructs the relative path
# '..' in the path moves up one directory level from the script's location to the root directory
sampledata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_sample.csv')
masterdata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_master.csv')

class CDNOW():
    def __init__(self, calwk=273, remove_unauthorized=False) -> None:
        self.calwk = calwk
        self.sample_data = (
            pl.scan_csv(source=sampledata_file_path,
                        has_header=False,
                        separator=',',
                        schema={'CustID': pl.Int32,
                                'ID': pl.Int32,
                                'Date': pl.String,
                                'Quant': pl.Int16,
                                'Spend': pl.Float64})
            .with_columns(pl.col('Date').str.to_date("%Y%m%d"))
            .with_columns((pl.col('Date') - pl.date(1996,12,31)).dt.total_days().cast(pl.UInt16).alias('PurchDay'))
            .with_columns((pl.col('Spend')*100).round(0).cast(pl.Int64).alias('Spend Scaled'))
            .group_by('ID', 'Date')
            .agg(pl.col('*').exclude('PurchDay').sum(), pl.col('PurchDay').max())
            .sort('ID', 'Date')
            .with_columns((pl.col("ID").cum_count().over("ID") - 1).cast(pl.UInt16).alias("DoR"))      
            .drop('CustID')
        )
        self.master_data = (
            pl.scan_csv(source = 'data/CDNOW/CDNOW_master.csv', 
                        has_header=False, 
                        separator=',', 
                        schema={'ID': pl.Int32,     # customer id
                                'Date': pl.String,      # transaction date
                                'Quant': pl.Int16,      # number of CDs purchased
                                'Spend': pl.Float64})   # dollar value (excl. S&H)
            .with_columns(pl.col('Date').str.to_date("%Y%m%d"))
            .with_columns((pl.col('Date') - pl.date(1996,12,31)).dt.total_days().cast(pl.UInt16).alias('PurchDay'))
            .with_columns((pl.col('Spend')*100).round(0).cast(pl.Int64).alias('Spend Scaled'))
            .group_by('ID', 'Date')
            .agg(pl.col('*').exclude('PurchDay').sum(), pl.col('PurchDay').max()) # Multiple transactions by a customer on a single day are aggregated into one
            .sort('ID', 'Date')
            .with_columns((pl.col("ID").cum_count().over("ID") - 1).cast(pl.UInt16).alias("DoR"))  # DoR = Depth of Repeat ('Transaction' time: starts with 0 as trial, 1 as 1st repeat and so on)
        )
        
        if remove_unauthorized:
            unauthorized_resellers = (
                self.master_data.filter(pl.col('DoR') != 0)
                .group_by('ID').agg(pl.col('Spend Scaled').sum())
                .filter(pl.col('Spend Scaled') > 400000).collect()
            )

            self.master_data = (
                self.master_data
                .filter(~pl.col('ID').is_in(unauthorized_resellers.select('ID')))
            )     


def rfm_summary(dataset, calwk=273):
    # The number of repeat transactions made by each customer in each period
    freq_x = frequency(dataset, calwk)
    
    # The number of CDs purchased and total spend across these repeat transactions
    pSpendQuant = spend_quant(dataset, freq_x)

    # The average spend per repeat transaction
    m_x = avg_spend(pSpendQuant, freq_x)
    
    # time of last calibration period repeat purchase (in weeks) - Recency
    ttlrp = t_x_T(dataset, freq_x, calwk)

    rfm_data = (
        m_x
        .join(other=ttlrp, on="ID", how="left")
        .with_columns(
            pl.when(pl.col('P1X') > 0)
            .then(pl.col('P1X Spend') / pl.col('P1X')) # average spend per repeat transaction
            .otherwise(0)
            .alias('zbar') 
        )        
    )
    
    return rfm_data

def frequency(dataset, calwk=273):
    # The number of repeat transactions made by each customer in each period
    freq_x = (
        dataset
        .group_by('ID', maintain_order=True)
        .agg(
            pl.col('PurchDay')
            .filter((pl.col('PurchDay') <= calwk) & (pl.col('DoR') > 0))
            .count()
            .alias('P1X'), # Period 1: Calibration Period

            pl.col('PurchDay')
            .filter((pl.col('PurchDay') > calwk) & (pl.col('DoR') > 0))
            .count()
            .alias('P2X')  # Period 2: Longitudinal Holdout Period      
        )
    )      
    
    return freq_x

def spend_quant(dataset, freq_x):
    # The number of CDs purchased and total spend across these repeat transactions
    pSpendQuant = (
        dataset
        .join(freq_x, on='ID', how='left')
        .group_by('ID', maintain_order=True)
        .agg(
            
            pl.col('Spend Scaled')
            .filter((pl.col('DoR') > 0) & (pl.col('DoR') <= pl.col('P1X')) & (pl.col('P1X') != 0))
            .sum()
            .alias('P1X Spend'),
            
            pl.col('Quant')
            .filter((pl.col('DoR') > 0) & (pl.col('DoR') <= pl.col('P1X')) & (pl.col('P1X') != 0))
            .sum()
            .alias('P1X Quant'),        
            
            pl.col('Spend Scaled')
            .filter((pl.col('DoR') > 0) & (pl.col('DoR') > pl.col('P1X')))
            .sum()
            .alias('P2X Spend'),
            
            pl.col('Quant')
            .filter((pl.col('DoR') > 0) & (pl.col('DoR') > pl.col('P1X')))
            .sum()
            .alias('P2X Quant')                
        )
    )      
    
    return pSpendQuant


def avg_spend(pSpendQuant, freq_x):
    # The average spend per repeat transaction
    m_x = (
        pSpendQuant
        .join(freq_x, on='ID', how='left')
        .with_columns(
            (pl.col('P1X Spend') / pl.col('P1X')).alias('m_x_calib'),
            (pl.col('P2X Spend') / pl.col('P2X')).alias('m_x_valid')
        ).fill_nan(0)
    )   
    
    return m_x 

def t_x_T(dataset, freq_x, calwk):
    # time of last calibration period repeat purchase (in weeks) - Recency
    ttlrp = (
        dataset
        .join(freq_x, on='ID', how='left')
        .with_columns(
            pl.col('PurchDay').filter(pl.col('DoR') == 0)
            .first()
            .over('ID')
            .alias('Trial Day')
        )
        .group_by('ID', maintain_order=True)
        .agg(
            pl.col('PurchDay', 'Trial Day')
            .filter(pl.col('DoR') <= pl.col('P1X'))
            .max()
            # .alias('LastPurch')
        )
        .with_columns(
            (pl.col('PurchDay')/7).alias('p1rec'), # Calendar week of the last observed purchase - Calendar Recency
            ((pl.col('PurchDay') - pl.col('Trial Day')) / 7).alias('t_x'), # Time to Last Repeat Purchase from Trial - Model Recency
            ((calwk - pl.col('Trial Day'))/7).alias('T') # effective calibration period (in weeks)            
        )
        .drop('PurchDay', 'Trial Day')
    )      
    
    return ttlrp