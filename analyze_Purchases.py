# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 14:55:19 2024

@author: ryanb
"""
# %%
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

# %%

def analyze():
    
    sheet_id = '1jb5O3L3yiCH6HhfQQP4yJ21wJEcMA2evyGqeF6belXM'
    input_sheet = 'Purchases'
    input_cell_range = 'A:M'
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
    purchases = pd.DataFrame(result.get('values', []))
    
    # Massage the spreadsheet.
    purchases.columns = purchases.iloc[0]  # Make the 0th row values the column headers.
    purchases = purchases[1:]  # Forget the 0th row, as it is now the headers!
    
    #print(purchases)
    
    #purchases = pd.read_csv(config.Purchases.file)
    
    purchases['Transaction creation date'] = pd.to_datetime(purchases['Transaction creation date'])
    
    columns_with_dollars = ['Item subtotal', 'Tax', 'Shipping and handling']
    
    for column in columns_with_dollars:
        
        purchases[column] = purchases[column].replace('\$', '', regex=True).astype(float)
    
    # TODO Change 'Vendor' to 'Platform' in source .csv file.
    columns_for_blanks = ['Project', 'Platform', 'Note']
    
    for column in columns_for_blanks:
        
        purchases[column].fillna('', inplace=True)
    
    # Adjust project...
    
    purchases = purchases[['Transaction creation date', 'Type', 'Expense type',
                          'Item title', 'Project', 'Item subtotal', 'Tax',
                          'Shipping and handling', 'Platform', 'Quantity', 'Note']]
    
    # Add the date string for purchases that have a project (and thus, are not
    # empty strings).
    purchases.loc[purchases['Project'] != '', 'Project'] = purchases['Project'] + purchases['Transaction creation date'].dt.strftime('%m%d%Y')
    
    #purchases['Net amount'] = purchases['Item subtotal'] + purchases['Tax'] + purchases['Shipping and handling']
    purchases['Net amount'] = purchases['Item subtotal'] + purchases['Tax'] + purchases['Shipping and handling']
    
    return purchases

if __name__ == '__main__':
    purchases = analyze()