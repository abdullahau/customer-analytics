import polars as pl
from typing import Union

class RFM(object):
    def __init__(self, 
                 data: Union[pl.LazyFrame, pl.DataFrame], 
                 dateformat: str, 
                 calib_p: int) -> None:
        '''
        Initialize the RFM object with the given data, date format, and calibration period.
        
        Parameters
        ----------        
        data : ~Union[polars.Dataframe, polars.LazyFrame]
            Transaction log (unique transaction on each row) of LazyFrame/DataFrame data type with the following schema:
                * `ID`[Union[pl.Int32, pl.Categorical, pl.String]]: Customer identifier linked to the transaction
                * `Date`[pl.String]: Transaction date (as string type for conversion and processing as pl.Expr (date))
                * `Quant`[pl.Int16]: Purchase quantity
                * `Spend`[pl.Float64]: Purchase spend
        
        dateformat : str
            string containing the date format in the transaction log data, eg. "%Y%m%d"
        
        calib_p : int
            Calibration period (in days) - split data into calibration and validation (longitudinal holdout) period  
        
        '''
        self._data = None  # Use a private attribute to store the data
        self.dateformat = dateformat
        self.calib_p = calib_p
        self.data = data  # Triggers the setter to preprocess data
    
    @property
    def data(self) -> Union[pl.LazyFrame, pl.DataFrame]:
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = self.__data_prep(data)
    
    def __data_prep(self, data):
        '''
        1) Convert date to pl.Date format using the `dateformat`provided
        2) Compute purchase day since the start of observation
        3) Scale spend by 100 so that 2 d.p. (cents) floats are cast as pl.Int64 for better performance and precision 
        4) Group data by 'ID' and 'Date' to aggregate multiple transactions by the same customer on the same day.
        5) Compute Depth of Repeat (DoR) for each transaction by a customer ('Transaction' time/level: starts with 0 as trial, 1 as 1st repeat, 2 as 2nd repeat and so on)
        '''
        return (
            data
            .with_columns(pl.col('Date').str.to_date(self.dateformat))
            .with_columns(((pl.col('Date') - pl.col('Date').min()).dt.total_days() + 1).cast(pl.UInt16).alias('PurchDay'))
            .with_columns((pl.col('Spend')*100).round(0).cast(pl.Int64).alias('Spend Scaled'))
            .group_by('ID', 'Date')
            .agg(pl.col('*').exclude('PurchDay').sum(), pl.col('PurchDay').max())                  # Multiple transactions by a customer on a single day are aggregated into one
            .sort('ID', 'Date')
            .with_columns((pl.col("ID").cum_count().over("ID") - 1).cast(pl.UInt16).alias("DoR"))  # DoR = Depth of Repeat ('Transaction' time: starts with 0 as trial, 1 as 1st repeat and so on)          
        )

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
                .filter((pl.col('PurchDay') <= self.calib_p) & (pl.col('DoR') > 0))
                .count()
                .alias('P1X'), # Period 1: Calibration Period

                pl.col('PurchDay')
                .filter((pl.col('PurchDay') > self.calib_p) & (pl.col('DoR') > 0))
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
        '''
        Recency (t_{x}) - Time of last calibration period repeat purchase (in weeks)
        T - Effective calibration period (in weeks)
        '''
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
                ((self.calib_p - pl.col('Trial Day'))/7).alias('T') # effective calibration period (in weeks)            
            )
            .drop('PurchDay', 'Trial Day')
        )      
        
        return ttlrp
    
    __frequency = frequency
    __spend_quant = spend_quant
    __avg_spend = avg_spend
    __t_x_T = t_x_T
