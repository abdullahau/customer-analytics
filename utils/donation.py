import polars as pl
import os 

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(current_dir, '..', 'data', 'Donation-Incidence', '1995_cohort_binary.csv')

class Donation():
    def __init__(self, calib_p=6) -> None:
        start_year, duration = 1995, 11
        self.years = [str(start_year + i) for i in range(duration+1)]
        self.data = (
            pl.scan_csv(filepath,
                        has_header=False,
                        separator=',',                        
                        schema={'ID': pl.Int32, **{str(i): pl.Int8 for i in self.years}})
        )
        self.calib_p = calib_p
        
    def rfm_data(self) -> pl.LazyFrame:
        calib_columns = [str(1996 + i) for i in range(self.calib_p)]
        valid_columns = [str(2002 + i) for i in range(len(self.years) - self.calib_p)]

        return (
            self.data
            .with_columns(
                pl.sum_horizontal(pl.all().exclude(['ID', '1995', *[str(i) for i in valid_columns]])).alias('P1X'),
                pl.sum_horizontal(pl.all().exclude(['ID', '1995', *[str(i) for i in calib_columns]])).alias('P2X'),
                pl.max_horizontal(
                    *[pl.when(pl.col(year) == 1).then(int(year) - 1995).otherwise(None) for year in calib_columns]
                ).alias("t_x"),
                pl.lit(self.calib_p).alias('np1x'), # n transaction opportunities in calibration period
                pl.lit(len(self.years) - 1 - self.calib_p).alias('np2x') # n transaction opportunities  in validation period
            ).fill_null(0)
            .select('ID', 'P1X', 't_x', 'np1x', 'P2X', 'np2x')
        )        

    def p1x_data(self) -> pl.LazyFrame:
        rfm_summary = self.rfm_data()
        return (
            rfm_summary
            .group_by('P1X','t_x', 'np1x')
            .agg(pl.len().alias('Count'))
            .sort(['t_x', 'P1X'], descending=True)         
        )

    def p2x_data(self):
        rfm_summary = self.rfm_data()
        return (
            rfm_summary
            .group_by('P2X', 'np2x')
            .agg(pl.len().alias('Count'))
            .sort(['P2X'], descending=True)         
        )
