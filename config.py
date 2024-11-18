# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 09:32:28 2024

@author: ryanb
"""
# %% Import packages.
import os

# %%
def accounting_directory():
    
    directory = r'C:\Users\ryanb\Documents\Baseball Cards\Accounting'
    return directory

# %%
class eBay:
    
    directory = accounting_directory()
    
    
    files = [r"Transaction_report_20220101_20221231.csv",
             r"Transaction_report_20230101_20231231.csv",
             r"Transaction_report_20240101_20241116.csv"]
    
    file_paths = []
    for file in files:
        file_paths.append(os.path.join(directory, file))
    

    
    #active_listings_directory = r"C:\Users\ryanb\Documents\SchoolhouseAll"
    #active_listings_file = r'eBay-all-active-listings-report-2024-07-18-11172879240.csv'
    #active_listings_path = os.path.join(active_listings_directory, active_listings_file)
    

# %%
class PayPal:
    directory = accounting_directory()
    files = ["PayPal_2021.csv",
             "PayPal_2022.csv",
             "PayPal_2023.csv"]
    
    file_paths = []
    for file in files:
        file_paths.append(os.path.join(directory, file))
    #file_paths = [os.path.join(directory, file) for file in files]
    

#%%
class PirateShip:
    directory = accounting_directory()
    file = "Pirate Ship.xlsx"
    file = os.path.join(directory, file)

# %%
class OfflineSales:
    directory = accounting_directory()
    file = 'Sales Log v2 - OffEbaySales.csv'
    file = os.path.join(directory, file)

# %%
class Purchases:
    directory = accounting_directory()
    file = 'Sales Log v2 - Purchases.csv'
    file = os.path.join(directory, file)

# %%
class Income:
    directory = accounting_directory()
    file = 'Sales Log v2 - Income.csv'
    file = os.path.join(directory, file)