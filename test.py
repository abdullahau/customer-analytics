import polars as pl

df = pl.DataFrame(
    {
        "month": [1, 2, 3],
        "day": [4, 5, 6],
    }
)
df2=df.with_columns(pl.date(2024, pl.col("month"), pl.col("day")))
print(df2.with_columns(((pl.col('date') - pl.col('date').min()).dt.total_days() + 1).alias('PuchDay')))