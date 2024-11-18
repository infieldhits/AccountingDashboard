# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:43:12 2024

@author: ryanb
"""
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

def analyze():
    
    #file = "Sales Log v2 - Income.csv"
    #path = os.path.join(directory, file)
    #income = pd.read_csv(path)
    #income = pd.read_csv(config.Income.file)
    
    sheet_id = '1jb5O3L3yiCH6HhfQQP4yJ21wJEcMA2evyGqeF6belXM'
    input_sheet = 'Income'
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
    income = pd.DataFrame(result.get('values', []))
    
    # Massage the spreadsheet.
    income.columns = income.iloc[0]  # Make the 0th row values the column headers.
    income = income[1:]  # Forget the 0th row, as it is now the headers!
    
    
    income['Transaction creation date'] = pd.to_datetime(income['Transaction creation date'])
    
    income['Net amount'] = income['Net amount'].replace('\$', '', regex=True).astype(float)
    
    columns_for_blanks = ['Item title', 'Project', 'Platform', 'Note']
    
    for column in columns_for_blanks:
        
        income[column].fillna('', inplace=True)
        
    income = income[['Transaction creation date', 'Type', 'Expense type',
                     'Item title', 'Project', 'Net amount', 'Platform', 'Note']]
    
    return income

if __name__ == '__main__':
    income = analyze()