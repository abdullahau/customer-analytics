from .RFM import RFM
import polars as pl
import os 
from typing import Union

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Constructs the relative path
# '..' in the path moves up one directory level from the script's location to the root directory
sampledata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_sample.csv')
masterdata_file_path = os.path.join(current_dir, '..', 'data', 'CDNOW', 'CDNOW_master.csv')

class CDNOW(RFM):
    def __init__(self, master:bool = True, calib_p:int = 273, remove_unauthorized=False):
        # Select and preprocess the data
        data = self.__select_data(master=master)
        super().__init__(data=data, dateformat="%Y%m%d", calib_p=calib_p)  # Call the superclass initializer
        
        # Filter unauthorized resellers
        if remove_unauthorized:
            self._data = self.filter_unauthorized(self._data)                
        
    def __select_data(self, master:bool=True) -> Union[pl.LazyFrame, pl.DataFrame]:
        'Select between master or sample version of CDNOW data'
        if master:
            data = (
                pl.scan_csv(source=masterdata_file_path, 
                            has_header=False, 
                            separator=',', 
                            schema={'ID': pl.Int32,         # customer id
                                    'Date': pl.String,      # transaction date
                                    'Quant': pl.Int16,      # number of CDs purchased
                                    'Spend': pl.Float64})   # dollar value (excl. S&H)
            )    
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
                .drop('CustID')                
            )   
        return data
    
    def filter_unauthorized(self, data: Union[pl.LazyFrame, pl.DataFrame], threshold: int = 4000):
        'Remove unauthorized resellers with total repeat spend exceeding exceeding $4,000.'
        unauthorized_resellers = (
            data.filter(pl.col('DoR') != 0)
            .group_by('ID')
            .agg(pl.col('Spend Scaled').sum())
            .filter(pl.col('Spend Scaled') > threshold * 100)
            .collect()
        )
        return data.filter(~pl.col('ID').is_in(unauthorized_resellers.select('ID')))