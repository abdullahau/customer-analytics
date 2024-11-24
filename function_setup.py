import polars as pl
import numpy as np

grocery_lf = pl.scan_csv(source="data/panel-datasets/edible_grocery.csv",
                         has_header=True,
                         separator=",",
                         schema={'panel_id': pl.UInt32,
                                 'trans_id': pl.Int32,
                                 'week': pl.UInt16,
                                 'sku_id': pl.UInt8,
                                 'units': pl.Int16,
                                 'price': pl.Float32,
                                 'brand': pl.Categorical})

sku_lf = pl.scan_csv(source="data/panel-datasets/sku_weight.csv",
                         has_header=True,
                         separator=",",
                         schema={'sku_id': pl.UInt8,
                                 'weight': pl.Int16})

def weekly_spend_summary(brand, year=2, lf=grocery_lf):
    summary = (
        lf
        .select(['week', 'units', 'price', 'brand'])
        .with_columns(((pl.col('units') * pl.col('price'))).alias('spend'))
    )
    
    if brand == 'Category': # Return LazyFrame of total category
        summary = summary.group_by('week')
    elif brand == 'All': # Return LazyFrame of all brands
        summary = summary.group_by('week', 'brand')
    else:  # Return LazyFrame of specified brand
        summary = summary.filter(
            pl.col('brand') == brand
        ).group_by('week', 'brand')
        
    summary = summary.agg(
        pl.col("spend").sum().alias('Weekly Spend') 
    ).sort('week')
    
    return summary

def weekly_vol_summary(brand, lf):
    with pl.StringCache():
        lf = (
            lf
            .join(
                other=sku_lf,
                left_on="sku_id",
                right_on="sku_id"            
            )
            .select(['week', 'units', 'brand', 'weight'])
        )
        
        if brand != 'All': 
            brand = [brand] if type(brand) == str else brand
            lf = lf.filter(
                pl.col('brand').is_in(*[brand])
            )
            
        summary = lf.with_columns(
            (((pl.col('units') * pl.col('weight'))/1000)).alias('volume')
        ).group_by('week', 'brand').agg(
            pl.col("volume").sum().alias('Weekly Volume')
        ).sort('week')
        
    return summary

def annual_sales_summary():
    summary = (
        weekly_spend_summary('All', grocery_lf)
        .with_columns((pl.col("week") / 52).ceil().alias('year'))
        .group_by(['year', 'brand'])
        .agg(pl.col("Weekly Spend").sum().alias('Yearly Sales'))
    ).sort('year')
    
    return summary

def trans_summary(brand, lf, year):
    
    # Primary Step: Filter by Year 1 and Remove Unused Columns
    filtered_lf = lf.filter(
        (pl.col('week') <= (year * 52)) &
        (pl.col('week') > ((year - 1) * 52))
    ).drop(
        pl.col('week','sku_id')
    )

    # Intermediate Step: Group by trans_id, panel_id, and brand
    group_trans = filtered_lf.drop(
        pl.col('price', 'units')
    ).group_by(
        'trans_id', 'panel_id', 'brand'
    ).n_unique()
    
    if brand == "Category":
        # Panellist-level category transaction summary
        summary = group_trans.group_by(
            'panel_id'
        ).n_unique()
    else:
        # Panellist-level brand transaction summary
        summary = group_trans.filter(
            pl.col('brand') == brand
        ).group_by(
            'panel_id'
        ).n_unique()
    
    return summary.select(
        pl.col('panel_id'),
        pl.col('trans_id').alias('# of Purchases'),
        pl.col('brand').alias('Brands Purchased')
    )
    
def trans_pivot(lf, year):
    
    # Primary Step: Filter by Year 1 and Remove Unused Columns
    filtered_lf = lf.filter(
        (pl.col('week') <= (year * 52)) &
        (pl.col('week') > ((year - 1) * 52))
    ).drop(
        pl.col('week','sku_id')
    )

    # Intermediate Step: Group by trans_id, panel_id, and brand
    group_trans = filtered_lf.drop(
        pl.col('price', 'units')
    ).group_by(
        'trans_id', 'panel_id', 'brand'
    ).n_unique() # count of unique entires
    
    summary = group_trans.collect().pivot(
        on='brand',
        index='panel_id',
        values='panel_id',
        aggregate_function="len"
        
    ).join(
        other=group_trans.group_by('panel_id').n_unique().drop('brand').collect(),
        on='panel_id'
    ).rename(
        {'trans_id': 'Category'}
    ).drop(
        pl.col('panel_id')
    )
    
    return summary

def spend_summary(brand, lf, year):
    
    group_spend = lf.filter(
        (pl.col('week') <= (year * 52)) &
        (pl.col('week') > ((year - 1) * 52))
    ).drop(
        pl.col('week','sku_id')
    ).with_columns(
        ((pl.col('units') * pl.col('price'))).alias('spend')
    )
    
    if brand == "Category":
        # Panellist-level category spend summary
        summary = group_spend.drop(
            pl.col('units', 'price', 'brand')
        ).group_by(
            'panel_id'
        ).agg(
            pl.col('spend').sum()
        )
    else:
        # Panellist-level brand spend summary
        summary = group_spend.drop(
            pl.col('units', 'price')
        ).group_by(
            'panel_id', 'brand'
        ).agg(
            pl.col('spend').sum()
        ).filter(
            pl.col('brand') == brand
        ).drop('brand')
        
    return summary

def spend_pivot(lf, year):
    
    group_spend = lf.filter(
        (pl.col('week') <= (year * 52)) &
        (pl.col('week') > ((year - 1) * 52))
    ).drop(
        pl.col('week','sku_id')
    ).with_columns(
        ((pl.col('units') * pl.col('price'))).alias('spend')
    ).collect().pivot(
        on='brand',
        index='panel_id',
        values='spend',
        aggregate_function='sum'
    ).select(
        'Alpha', 'Bravo', 'Charlie', 'Delta', 'Other'
    )

    return group_spend

def vol_summary(brand, lf, year):
    with pl.StringCache():
        group_vol = lf.filter(
            (pl.col('week') <= (year * 52)) &
            (pl.col('week') > ((year - 1) * 52))
        ).join(
            other=sku_lf,
            left_on='sku_id',
            right_on='sku_id'
        ).drop(
            pl.col('week','sku_id')
        ).with_columns(
            # volume column that is the product of weight of each SKU and the units of SKU sold
            (((pl.col('units') * pl.col('weight'))/1000)).alias('volume') # # weight from grams to kilograms
        ).drop(
            pl.col('units', 'price', 'weight')
        )
        
        if brand == "Category":
            # Panellist-level category volume sales summary
            summary = group_vol.drop(
                pl.col('brand')
            ).group_by(
                'panel_id'
            ).agg(
                pl.col('volume').sum()
            )
        else:
            # Panellist-level brand volume sales summary
            summary = group_vol.group_by(
                'panel_id', 'brand'
            ).agg(
                pl.col('volume').sum()
            ).filter(
                pl.col('brand') == brand
            ).drop('brand')
        
    return summary

def vol_pivot(lf, year):
    with pl.StringCache():
        group_vol = lf.filter(
            (pl.col('week') <= (year * 52)) &
            (pl.col('week') > ((year - 1) * 52))
        ).join(
            other=sku_lf,
            left_on='sku_id',
            right_on='sku_id'
        ).drop(
            pl.col('week','sku_id')
        ).with_columns(
            # volume column that is the product of weight of each SKU and the units of SKU sold
            (((pl.col('units') * pl.col('weight'))/1000)).alias('volume') # # weight from grams to kilograms
        ).drop(
            pl.col('units', 'price', 'weight')
        ).collect().pivot(
            on='brand',
            index='panel_id',
            values='volume',
            aggregate_function='sum'
        ).select(
            'Alpha', 'Bravo', 'Charlie', 'Delta', 'Other'
        )
        
    return group_vol


def panel_summary(lf=grocery_lf, brand=None):
    
    if brand is not None:
        lf = (lf.filter(pl.col("brand") == brand))
    
    pass