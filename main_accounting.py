# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 13:00:50 2024

@author: ryanb
"""

# %% Import packages.
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date


# Import modules.
import analyze_eBay, analyze_OfflineSales, analyze_Purchases, analyze_Income, \
    analyze_PirateShip
    
    
    
# %% Define function.
def splice_project(project_name):
    
    if len(str(project_name)) > 8 and project_name[-8:].isdigit():

        project_name = project_name[:-8]
    
    return project_name

def burdened_costs(df, start_date, end_date):
    """

    Parameters
    ----------
    start_date : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.

    Returns
    -------
    burdened_rate : TYPE
        DESCRIPTION.

    """
    
    #first_date = min(df['Transaction creation date'])
    #today = date.today()
    date_range = pd.date_range(start_date, end_date)

    df_orders = df[df['Type'] == 'Order']

    df_orders = df_orders[['Transaction creation date', 'Type']].resample('d', on='Transaction creation date').count()
    df_orders = df_orders.reindex(date_range, fill_value=0)
    df_orders = df_orders.rename(columns={'Type': 'Orders'})

    df_supplies = df[df['Type'] == 'Supplies']
    df_supplies = df_supplies.resample('d', on='Transaction creation date')['Net amount'].sum()
    df_supplies = df_supplies.reindex(date_range, fill_value=0)
    df_supplies = df_supplies.rename('Supplies')

    df_shipping = df[df['Type'] == 'Shipping label']
    df_shipping = df_shipping.resample('d', on='Transaction creation date')['Net amount'].sum()
    df_shipping = df_shipping.reindex(date_range, fill_value=0)
    df_shipping = df_shipping.rename('Shipping')

    df_other = df[df['Type'] == 'Other fee']
    df_other = df_other.resample('d', on='Transaction creation date')['Net amount'].sum()
    df_other = df_other.reindex(date_range, fill_value=0)
    df_other = df_other.rename('Other')

    df_costs = pd.concat([df_orders, df_supplies, df_shipping, df_other], axis=1)

    df_costs['Total'] = df_costs[['Supplies', 'Shipping', 'Other']].sum(axis=1)

    df_costs['Cumulative orders'] = df_costs['Orders'].cumsum()
    df_costs['Cumulative costs'] = df_costs['Total'].cumsum()
    df_costs['Costs per order'] = df_costs['Cumulative costs'] / df_costs['Cumulative orders']
    
    df_costs.index = pd.to_datetime(df_costs.index)
    df_costs.index = df_costs.index.rename('Transaction creation date')
    
    burdened_rate = df_costs['Costs per order'][-1]
    
    return burdened_rate


# %%
eBay = analyze_eBay.analyze()
offline = analyze_OfflineSales.analyze()
purchases = analyze_Purchases.analyze()
income = analyze_Income.analyze()
pirate_ship = analyze_PirateShip.analyze()

df = pd.concat([eBay,
                offline,
                purchases,
                income,
                pirate_ship]).sort_values(by='Transaction creation date',
                                   ascending=True)

#df.index = pd.to_datetime(df.index)             
#df['Transaction creation date'] = df['Transaction creation date']                       
                                          
#df['Transaction creation date'] = pd.to_datetime(df['Transaction creation date'])             
df['Parent Project'] = df['Project'].apply(splice_project)

start =  pd.to_datetime('2024/01/01')
end = pd.to_datetime(date.today())

# Filter to the desired date range.
df_range = df[(df['Transaction creation date'] >= start) &
              (df['Transaction creation date'] <= end)]

df_range = df_range[['Transaction creation date',
                     'Type',
                     'Net amount',
                     'Project',
                     'Parent Project',
                     'Item subtotal',
                     'Shipping and handling',
                     'Final Value Fee - fixed',
                     'Final Value Fee - variable',
                     'International fee',
                     'Gross transaction amount',
                     'Expense type',
                     'Tax',
                     ]]

burdened_rate = burdened_costs(df, start, end)

projects = ['completeset',
            'vintage',
            'mike',
            'misc',
            'portraits',
            'cb',
            'ip', 'hofgraded', 'gold']


for project in projects:
    
    fig, ax = plt.subplots(dpi=200)

    df_project = df_range[df_range['Parent Project'] == project]
    df_project_daily = df_project.resample('d', on='Transaction creation date')[['Net amount']].sum()
    
    df_project_orders = df_project[df_project['Type'] == 'Order']
    df_project_orders = df_project_orders.resample('d', on='Transaction creation date')[['Type']].count()
    df_project_orders = df_project_orders.rename(columns={'Type': 'Orders'})
    
    daily_with_burden = df_project_daily.join(df_project_orders)
    daily_with_burden.fillna(0.0, inplace=True)
    daily_with_burden['Burdened costs'] = daily_with_burden['Orders'] * burdened_rate
    daily_with_burden['Burdened total'] = daily_with_burden['Net amount'] + daily_with_burden['Burdened costs']
    daily_with_burden['Cumulative burdened total'] = daily_with_burden['Burdened total'].cumsum()
    daily_with_burden['Total orders'] = daily_with_burden['Orders'].cumsum()
    daily_with_burden['Direct total'] = daily_with_burden['Net amount'].cumsum()
    
    plt.plot(daily_with_burden.index,
             daily_with_burden['Cumulative burdened total'])
    
    plt.plot(daily_with_burden.index,
             daily_with_burden['Direct total'])
    
    plt.title(project)
    
    plt.show()

#check_rate = burdened_costs(min(df['Transaction creation date']), date.today())
#test.index.rename('Transaction creation date', inplace=True)


#orders = df[df['Type'] == 'Order']

#daily_orders = orders.resample('d', on='Transaction creation date')['Type'].count()
#daily_money = orders.resample('d', on='Transaction creation date')['Net amount'].sum()

#daily = pd.concat([daily_orders, daily_money], axis=1)
#daily = daily.rename(columns={'Type': 'Orders'})

#daily['Burdened costs'] = daily['Orders'] * check_rate
#daily['Burdened profit'] = daily['Net amount'] + daily['Burdened costs']

# test_join = daily.join(test['Costs per order'],
#                        how='left')

# rate = test_join['Costs per order'][-1]

# test_join['Burdened costs'] = test_join['Orders'] * rate
# test_join['Burdened profit'] = test_join['Net amount'] + test_join['Burdened costs']

# test_merge = pd.merge(left=daily,
#                       right=test,
#                       how='left',
#                       left_index=True,
#                       right_index=True)
# test_merge.set_index('Transaction creation date',
#                      drop=True,
#                      inplace=True)

#test_join = df.join(test)

# Let's calculate burdened costs per order. We want a dataframe with the 
# following columns:
# Date, cum orders, cum supplies, cum shipping, daily supplies, daily shipping


# # Perform analysis on revenue and costs.
# revenue = df[df['Type'].isin(['Order', 'Refund'])]
# costs = df[~df['Type'].isin(['Order', 'Refund'])]

# # Cumulative.
# fig, ax = plt.subplots(dpi=100)
# plt.plot(df['Transaction creation date'],
#          df['Gross transaction amount'].cumsum())
# plt.title('Net profit')
# # plt.plot(revenue['Transaction creation date'],
# #          revenue['Gross transaction amount'].cumsum())

# # plt.plot(costs['Transaction creation date'],
# #          costs['Gross transaction amount'].cumsum())


# revenue_monthly = revenue.resample('MS', on='Transaction creation date')['Gross transaction amount'].sum()
# fig, ax = plt.subplots(dpi=100)
# plt.bar(revenue_monthly.index,
#         revenue_monthly,
#         width=20,
#         color='green',
#         label='Revenue')

# costs_monthly = costs.resample('MS', on='Transaction creation date')['Gross transaction amount'].sum()
# #fig, ax = plt.subplots(dpi=100)
# plt.bar(costs_monthly.index,
#         -costs_monthly,
#         width=20,
#         color='red',
#         label='Costs')

# plt.title('Monthly Revenue and Costs')
# plt.legend()