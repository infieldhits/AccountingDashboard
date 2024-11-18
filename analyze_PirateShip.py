# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 11:48:00 2024

@author: ryanb
"""
import pandas as pd

import config

def analyze():
    # %% Analyze Pirate Ship transactions.
    #file = "Pirate Ship.xlsx"
    #path = os.path.join(directory, file)
    pirate_ship = pd.read_excel(config.PirateShip.file)
    
    # Remove the time zones from the transaction date strings. These cause
    # warnings to appear.
    pirate_ship['Date'] = pirate_ship['Date'].str.replace('MDT', '').str.strip()
    pirate_ship['Date'] = pirate_ship['Date'].str.replace('MST', '').str.strip()
    
    pirate_ship.rename(columns={"Date": "Transaction creation date",
                                "Total": "Net amount",
                                "Description": "Item title"},
                       inplace=True)
    
    pirate_ship['Transaction creation date'] = pd.to_datetime(pirate_ship['Transaction creation date'])
    
    pirate_ship['Type'] = pirate_ship['Type'].replace('Label', 'Shipping label')
    
    pirate_ship['Type'] = pirate_ship['Type'].replace('Carrier Adjustment', 'Shipping label')
    pirate_ship['Type'] = pirate_ship['Type'].replace('Carrier Adjustment Refund', 'Shipping label')
    
    # Ignore payments.
    pirate_ship = pirate_ship[pirate_ship['Type'] != 'Payment']
    
    pirate_ship = pirate_ship[['Transaction creation date', 'Type', 'Item title',
                               'Net amount']]
    
    pirate_ship['Platform'] = "Pirate Ship"
    pirate_ship['Project'] = ''
    pirate_ship['Expense type'] = 'Business'
    
    return pirate_ship