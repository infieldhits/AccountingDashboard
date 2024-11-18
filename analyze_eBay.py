# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 11:47:49 2024

@author: ryanb
"""
# %% Import packages.
import pandas as pd
import numpy as np
import os

# Import modules.
import config

# %% Define the function.
def analyze():

    eBay_transactions_files = config.eBay.file_paths
    
    eBay_transactions = pd.DataFrame()
    for file in eBay_transactions_files:
        
        transactions = pd.read_csv(file,
                                   skiprows=11)
        
        eBay_transactions = pd.concat([eBay_transactions, transactions],
                                      ignore_index=True)
    
    eBay_transactions = eBay_transactions[eBay_transactions.columns].replace('--', np.nan)
    
    # Fix static errors. These were typos on the original eBay listings. Ugh.
    eBay_transactions['Custom label'] = eBay_transactions['Custom label'].replace('gold0502024', 'gold05022024')
    eBay_transactions['Custom label'] = eBay_transactions['Custom label'].replace('misc0622204', 'misc06222024')
    
    
    float_columns = ['Net amount',
                     'Item subtotal',
                     'Shipping and handling',
                     'Seller collected tax',
                     'eBay collected tax',
                     'Final Value Fee - fixed',
                     'Final Value Fee - variable',
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
    
    # Remove columns that are entirely nan.
    eBay_transactions.dropna(axis=1,
                             how='all',
                             inplace=True)
    
    # Ignore payouts.
    eBay_transactions = eBay_transactions[eBay_transactions['Type'] != 'Payout']
    
    # Drop columns we do not care about.
    eBay_transactions.drop(['Payout ID',
                            'Payout date',
                            'Payout method',
                            'Payout status',
                            'Reference ID',
                            'Legacy order ID',
                            'Transaction currency'],
                           axis=1,
                           inplace=True)
    
    # Adjust column naming.
    eBay_transactions.rename(columns={"Custom label": "Project"}, inplace=True)
    
    return eBay_transactions