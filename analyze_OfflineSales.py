# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 13:43:14 2024

@author: ryanb
"""

# %% Import packages.
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Import modules.
import config

def analyze():
# %% Offline sales
    #offline_sales_file = config.OfflineSales.file
    #offline_transactions = pd.read_csv(offline_sales_file)
    
    sheet_id = '1jb5O3L3yiCH6HhfQQP4yJ21wJEcMA2evyGqeF6belXM'
    input_sheet = 'Offline Sales'
    input_cell_range = 'A:L'
    #output_sheet = 'Output'
    
    # Read the API credentials.
    #logger.info("Connecting to Google API.")
    creds = service_account.Credentials.from_service_account_file(
        r'C:\Users\ryanb\.google\ebay-uploader-438416-d4ae87275c5b.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    # Call the service to read the spreadsheet.
    #logger.info("Calling service to read Google Sheet.")
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=input_sheet+'!'+input_cell_range).execute()
    offline_transactions = pd.DataFrame(result.get('values', []))
    
    # Massage the spreadsheet.
    offline_transactions.columns = offline_transactions.iloc[0]  # Make the 0th row values the column headers.
    offline_transactions = offline_transactions[1:]  # Forget the 0th row, as it is now the headers!
    
    #print(offline_transactions)
    
    columns_with_dollars = ['Item subtotal', 'Shipping and handling', 'Total Sale',
                            'Final Value Fee - variable']
    
    for column in columns_with_dollars:
        
        offline_transactions[column] = offline_transactions[column].replace('\$', '', regex=True).astype(float)
    
    offline_transactions['Transaction creation date'] = pd.to_datetime(offline_transactions['Transaction creation date'])
    
    offline_transactions.sort_values(by='Transaction creation date',
                                     inplace=True)
    
    offline_transactions.drop(['Total Sale', 'Postage', 'Net amount'],
                              axis=1,
                              inplace=True)
    
    # TODO Address eBay postage.
    
    offline_transactions['Gross transaction amount'] = offline_transactions[['Item subtotal', 'Shipping and handling']].sum(axis=1)
    offline_transactions['Net amount'] = offline_transactions[['Item subtotal', 'Shipping and handling', 'Final Value Fee - variable']].sum(axis=1)
    
    offline_transactions['Type'] = 'Order'
    offline_transactions['Expense type'] = 'Business'
    
    return offline_transactions

if __name__ == '__main__':
    offline_transactions = analyze()