# -*- coding: utf-8 -*-
"""
Created on Sun May 19 12:05:21 2024

@author: ryanb
"""

# %% Import packages.
import numpy as np
import pandas as pd
import os

# Import modules.
import config

directory = config.Accounting.directory

# eBay
eBay_transactions_files = config.Accounting.eBay

eBay_transactions = pd.DataFrame()
for file in eBay_transactions_files:
    
    transactions = pd.read_csv(os.path.join(directory, file),
                               skiprows=11)
    
    eBay_transactions = pd.concat([eBay_transactions, transactions],
                                  ignore_index=True)

eBay_transactions = eBay_transactions[eBay_transactions.columns].replace('--', np.nan)


float_columns = ['Net amount', 'Item subtotal', 'Shipping and handling', 'Seller collected tax',
                 'eBay collected tax',
                 'Final Value Fee - fixed', 'Final Value Fee - variable',
                 'Very high "item not as described" fee',
                 'Below standard performance fee',
                 'International fee',
                 'Deposit processing fee',
                 'Gross transaction amount']

for column in float_columns:
    eBay_transactions[column] = eBay_transactions[column].astype(float)
    
# int_columns = ['Quantity']
# for column in int_columns:
#     eBay_transactions[column] = eBay_transactions[column].astype(int)

eBay_transactions['Expense type'] = 'Business'
eBay_transactions['Platform'] = 'eBay'

eBay_transactions['Transaction creation date'] = pd.to_datetime(eBay_transactions['Transaction creation date'])

eBay_transactions.sort_values('Transaction creation date',
                              ascending=True,
                              inplace=True,
                             )

eBay_transactions.reset_index(drop=True, inplace=True)


ad_fees = eBay_transactions['Description'].isin(['Ad Fee Express ', 'Ad Fee Standard '])  # TODO Trim before
eBay_transactions.loc[ad_fees, 'Type'] = 'Marketing'


# %% Offline sales
offline_sales_file = config.Accounting.offline_sales
offline_transactions = pd.read_csv(os.path.join(directory, offline_sales_file))

columns_with_dollars = ['Item subtotal', 'Shipping and handling', 'Total Sale',
                        'Final Value Fee - variable']

for column in columns_with_dollars:
    
    offline_transactions[column] = offline_transactions[column].replace('\$', '', regex=True).astype(float)

# %% Pirate Ship
pirate_ship_file = config.Accounting.pirate_ship_report
pirate_ship_transactions = pd.read_excel(os.path.join(directory, pirate_ship_file))

# %% PayPal

# %% Concatenate everything.
transactions = pd.concat([eBay_transactions])

print("Accounting module complete.")