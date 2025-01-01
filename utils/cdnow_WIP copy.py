import polars as pl
import os 
from typing import Union

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Constructs the relative path
# '..' in the path moves up one directory level from the script's location to the root directory
sampledata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_sample.csv')
masterdata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_master.csv')

class RFMData(object):
    def __init__(self, data: Union[pl.LazyFrame, pl.DataFrame], calwk: int) -> None:
        '''
        Create an RFM summary using a transaction log of LazyFrame/DataFrame data type with the following schema:
        'ID'[Union[pl.Int32, pl.Categorical, pl.String]]  - Customer IDs linked to the transaction, 
        'Date'[pl.Date] - Transaction Date, 
        'Quant'[pl.Int16] - Purchase Quantity, 
        'Spend'[pl.Float64] - Purchase Spend
        
        Note: Aggregate transactions by the same customer on the same day.
        '''
        self.data = data
        self.calwk = calwk

    def rfm_summary(self) -> Union[pl.LazyFrame, pl.DataFrame]:
        'Return a LazyFrame/DataFrame with recency (t_x), frequency (x), monetary value (m_x), total repeat spend, and quant in calibration and validation period'
        # The number of repeat transactions made by each customer in each period
        freq_x = self.__frequency()
        
        # The number of CDs purchased and total spend across these repeat transactions
        pSpendQuant = self.__spend_quant(freq_x)

        # The average spend per repeat transaction
        m_x = self.__avg_spend(pSpendQuant, freq_x)
        
        # time of last calibration period repeat purchase (in weeks) - Recency
        ttlrp = self.__t_x_T(freq_x)

        rfm_data = (
            m_x
            .join(other=ttlrp, on="ID", how="left")
            .with_columns(
                pl.when(pl.col('P1X') > 0)
                .then(pl.col('P1X Spend') / pl.col('P1X')) # average spend per repeat transaction
                .otherwise(0)
                .alias('zbar') # customer’s observed average transaction value, an imperfect estimate of their (unobserved) mean transaction value
            )        
        )
        
        return rfm_data

    def frequency(self) -> Union[pl.LazyFrame, pl.DataFrame]:
        'Frequency (x) - The number of repeat transactions made by each customer in calibration and validation period'
        freq_x = (
            self.data
            .group_by('ID', maintain_order=True)
            .agg(
                pl.col('PurchDay')
                .filter((pl.col('PurchDay') <= self.calwk) & (pl.col('DoR') > 0))
                .count()
                .alias('P1X'), # Period 1: Calibration Period

                pl.col('PurchDay')
                .filter((pl.col('PurchDay') > self.calwk) & (pl.col('DoR') > 0))
                .count()
                .alias('P2X')  # Period 2: Longitudinal Holdout Period      
            )
        )      
        
        return freq_x

    def spend_quant(self, freq_x: Union[pl.LazyFrame, pl.DataFrame]) -> Union[pl.LazyFrame, pl.DataFrame]:
        'The number of CDs purchased and total spend across repeat transactions in calibration and validation periods'
        
        pSpendQuant = (
            self.data
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


    def avg_spend(self, pSpendQuant: Union[pl.LazyFrame, pl.DataFrame], freq_x: Union[pl.LazyFrame, pl.DataFrame]) -> Union[pl.LazyFrame, pl.DataFrame]:
        'Monetary Value (m_{x}) - The average spend per repeat transaction for the calibration and validation periods'
        m_x = (
            pSpendQuant
            .join(freq_x, on='ID', how='left')
            .with_columns(
                (pl.col('P1X Spend') / pl.col('P1X')).alias('m_x_calib'),
                (pl.col('P2X Spend') / pl.col('P2X')).alias('m_x_valid')
            ).fill_nan(0)
        )   
        
        return m_x 

    def t_x_T(self, freq_x: Union[pl.LazyFrame, pl.DataFrame]) -> Union[pl.LazyFrame, pl.DataFrame]:
        'Recency (t_{x}) - Time of last calibration period repeat purchase (in weeks)'
        
        ttlrp = (
            self.data
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
                ((self.calwk - pl.col('Trial Day'))/7).alias('T') # effective calibration period (in weeks)            
            )
            .drop('PurchDay', 'Trial Day')
        )      
        
        return ttlrp
    
    __frequency = frequency
    __spend_quant = spend_quant
    __avg_spend = avg_spend
    __t_x_T = t_x_T
    

class CDNOW(RFMData):
    def __init__(self, master:bool = True, remove_unauthorized:bool = False, calwk:int = 273):
        self.data = self.__select_data(master=master, remove_unauthorized=remove_unauthorized)
        self.calwk = calwk
        
    def __select_data(self, master:bool=True, remove_unauthorized:bool=False) -> Union[pl.LazyFrame, pl.DataFrame]:
        if master:
            data = (
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
                    data.filter(pl.col('DoR') != 0)
                    .group_by('ID').agg(pl.col('Spend Scaled').sum())
                    .filter(pl.col('Spend Scaled') > 400000).collect()
                )

                data = data.filter(~pl.col('ID').is_in(unauthorized_resellers.select('ID')))    
        else: 
            data = (
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
        return data
        

if __name__ == "__main__":
    cdnow = CDNOW(master=False, calwk=273)
    print(cdnow)
    print(cdnow.data.schema)