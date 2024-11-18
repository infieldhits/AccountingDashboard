# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 11:28:17 2024

@author: ryanb
"""

# %% Import packages.
import pandas as pd
import numpy as np
import dash
import plotly.express as px
from dash import dash_table
#import dash_core_components as dcc
#import dash_html_components as html
from dash import html
from dash import dcc
from dash import Input, Output
from datetime import datetime
from datetime import date

# Import modules.
import main_accounting

# %% Retrieve and prepare the data. Resampling will take place based on user
# selections.
transactions = main_accounting.df
#revenue = main_accounting.revenue

shipping = pd.DataFrame()
supplies = pd.DataFrame()
other_fees = pd.DataFrame()

# Save variables for key dates.
first_date = date(2021, 1, 1)
today = date(datetime.now().year, datetime.now().month, datetime.now().day)

# %% Construct the application.
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True  # For nested callbacks
server = app.server
app.title = "Infield Hits Financial Dashboard"

# %% Tabs
TAB_SELECTED_STYLE = {'font-weight': 'bold',
                      'border-color': 'blue',
                      }

tabs = [dcc.Tab(label='Accounting',
                value='tab-accounting',
                selected_style=TAB_SELECTED_STYLE),
        dcc.Tab(label='Projects',
                value='tab-projects',
                selected_style=TAB_SELECTED_STYLE),
        ]

# %% Establish the layout.
app.layout = html.Div([# Logo and title
                      
                      # Tabs
                      dcc.Tabs(id='tabs',
                               children=tabs,
                               value='tab-accounting'),
                      
                      # User selections.
                      dcc.Checklist(id='filters',
                                    options=['Business', 'Personal'],
                                    value=['Business', 'Personal'],
                                    inline=True),
                      
                      dcc.DatePickerRange(id='date-range',
                                          min_date_allowed=first_date,
                                          max_date_allowed=today,
                                          initial_visible_month=today,
                                          start_date=date(datetime.now().year, 1, 1),
                                          end_date=today),
                      
                      # Container for callback
                      html.Div(id='content')
                      ])


# %% Construct a callback for the page content.
@app.callback(Output('content', 'children'),
              [Input('tabs', 'value'),
               Input('filters', 'value'),
               Input('date-range', 'start_date'),
               Input('date-range', 'end_date')])
def update_content(tab_selection, type_filter, start_date, end_date):
    
    filtered_transactions = transactions[(transactions['Transaction creation date'] >= start_date) &
                                         (transactions['Transaction creation date'] <= end_date)]
    
    burdened_rate = main_accounting.burdened_costs(filtered_transactions, start_date, end_date)
    
    if tab_selection == 'tab-accounting':
        
        # Filter based on the tab selection.
        revenue = filtered_transactions[filtered_transactions['Type'].isin(['Order', 'Refund'])]
        revenue_filtered = revenue[revenue['Expense type'].isin(type_filter)]
        
        revenue_monthly = revenue_filtered.resample('MS', on='Transaction creation date')['Gross transaction amount'].sum()
        
        print("\n\n\n\n\nTotal revenue in time range:", revenue_monthly.sum())
        
        fig = px.bar(revenue_monthly,
                     x=np.array(revenue_monthly.index),
                     y=revenue_monthly,
                     title='Revenue',
                     labels={'x': 'Month',
                             'y': 'Revenue ($)'}
                     )
        
        revenue_bars = dcc.Graph(figure=fig)
        
        profit_filtered = filtered_transactions[filtered_transactions['Expense type'].isin(type_filter)]
        
        profit_daily = profit_filtered.resample('d', on='Transaction creation date')['Net amount'].sum()

        fig = px.line(profit_daily,
                      x=profit_daily.index,
                      y=profit_daily.values.cumsum(),
                      title='Profit',
                      labels={'Transaction creation date': 'Date',
                              'y': 'Profit ($)'})
        
        profit_plot = dcc.Graph(figure=fig)
        
        # Costs.
        burdened_costs = cumulative_table(filtered_transactions)
        
        fig = px.line(burdened_costs,
                      x=burdened_costs.index,
                      y=['Costs per order', 'Supplies costs per order', 'Shipping costs per order', 'Other fees per order'],
                      hover_data={'value': ':.2f',
                                  'variable': False},
                      #custom_data=['Supplies costs per order', 'Shipping costs per order', 'Other fees per order', 'Costs per order'],
                      )
        fig.update_layout(hovermode='x unified')
        fig.update_layout(yaxis_range=[-4, 0])
        costs_per_order = dcc.Graph(figure=fig)
        
        
        # Compile the plots for the tab.
        content = [revenue_bars,
                   profit_plot,
                   costs_per_order]
        
    elif tab_selection == 'tab-projects':
        
        projects = ['completeset', 'portraits', 'cb', 'ip', 'gold', 'misc', 'mike', 'vintage']
        
        
        content = []
        for project in projects:
            
            temp = filtered_transactions[filtered_transactions['Parent Project'] == project]
            
            print(temp.head)
            
            
            
            #daily = temp.resample('d', on='Transaction creation date').sum()
            
            #print(daily)
            
            
            
            temp_orders = temp[temp['Type'] == 'Order']
            
            project_daily_orders = temp_orders.resample('d', on='Transaction creation date')[['Type']].count()
            project_daily_orders = project_daily_orders.rename(columns={'Type': 'Orders'})
            
            project_daily = temp.resample('d', on='Transaction creation date')[['Net amount']].sum()
            
            #print(project_daily_orders)
            #print(project_daily)
            
            project_daily_all = project_daily.join(project_daily_orders)
            
            project_daily_all['Burdened costs'] = project_daily_all['Orders'] * burdened_rate
            project_daily_all['Burdened profit'] = project_daily_all['Net amount'] + project_daily_all['Burdened costs']
            
            #print(project_daily_all)
            
            p_act = project_daily[['Net amount']]
            p_act['source'] = 'Actual'
            p_bur = project_daily_all[['Burdened profit']]
            p_bur = p_bur.rename(columns={'Burdened profit': 'Net amount'})
            p_bur['source'] = 'Burdened'
            
            p = pd.concat([p_act, p_bur])
            
            
            # print("Total sales profit:", project_daily.values.cumsum()[-1])
            # print(project_daily)
            
            # fig = px.line(project_daily,
            #               project_daily.index,
            #               project_daily.values.cumsum(),
            #               title=project,
            #               labels={'y': 'Profit ($)'})
            
            fig = px.line(p,
                          p.index,
                          p['Net amount'].cumsum(),
                          title=project,
                          color='source',
                          labels={'y': 'Profit ($)'})
            
            
            plot = dcc.Graph(figure=fig)
            content.append(plot)
        
        # temp = filtered_transactions[filtered_transactions['Project'] == 'vintage08052024']
        # project_daily = temp.resample('d', on='Transaction creation date')['Net amount'].sum()
        # fig = px.line(project_daily,
        #               project_daily.index,
        #               project_daily.values.cumsum(),
        #               title='vintage08052024',
        #               labels={'y': 'Profit ($)'})
        # plot = dcc.Graph(figure=fig)
        # content.append(plot)
        
        # temp = filtered_transactions[filtered_transactions['Project'] == 'vintage09032024']
        # project_daily = temp.resample('d', on='Transaction creation date')['Net amount'].sum()
        # fig = px.line(project_daily,
        #               project_daily.index,
        #               project_daily.values.cumsum(),
        #               title='vintage09032024',
        #               labels={'y': 'Profit ($)'})
        # plot = dcc.Graph(figure=fig)
        # content.append(plot)
    
    
    return content

# %%
def cumulative_table(df):
    
    # Costs.
    orders = df[df['Type'] == 'Order']
    #orders.sort_values('Transaction creation date', inplace=True)
    orders_daily = orders.groupby('Transaction creation date').count()['Type']
    #orders_daily.sort_values('Transaction creation date', inplace=True)
    

    daily_supplies = df[df['Type'] == 'Supplies'].resample('d', on='Transaction creation date')['Net amount'].sum()
    daily_shipping = df[df['Type'] == 'Shipping label'].resample('d', on='Transaction creation date')['Net amount'].sum()
    daily_other = df[df['Type'] == 'Other fee'].resample('d', on='Transaction creation date')['Net amount'].sum()
    
    daily_orders_and_supplies = pd.merge(left=orders_daily,
                                         right=daily_supplies,
                                         on='Transaction creation date',
                                         how='outer')
    daily_orders_and_supplies.rename(columns={'Type': 'Number of orders',
                                              'Net amount': 'Supplies'},
                                     inplace=True)
    
    #daily_orders_and_supplies['Supplies costs per order'] = daily_orders_and_supplies['Supplies'] / daily_orders_and_supplies['Number of orders']

    burdened_costs = pd.merge(left=daily_orders_and_supplies,
                              right=daily_shipping,
                              on='Transaction creation date',
                              how='outer')
    burdened_costs.rename(columns={'Net amount': 'Shipping'},
                          inplace=True)
    
    # Incorporate other fees.
    burdened_costs = pd.merge(left=burdened_costs,
                              right=daily_other,
                              on='Transaction creation date',
                              how='outer')
    burdened_costs.rename(columns={'Net amount': 'Other fees'},
                          inplace=True)
    
    burdened_costs.fillna(0, inplace=True)
    burdened_costs.sort_index(inplace=True)
    
    # We want cumulative sums.
    burdened_costs['Number of orders'] = burdened_costs['Number of orders'].cumsum()
    burdened_costs['Shipping'] = burdened_costs['Shipping'].cumsum()
    burdened_costs['Supplies'] = burdened_costs['Supplies'].cumsum()
    burdened_costs['Other fees'] = burdened_costs['Other fees'].cumsum()
    #burdened_costs['Costs per order'] = burdened_costs[['Shipping costs per order', 'Supplies costs per order', 'Other fees per order']].sum(axis=1)

    # Now, calculate the averages.
    burdened_costs['Shipping costs per order'] = burdened_costs['Shipping'] / burdened_costs['Number of orders']
    burdened_costs['Supplies costs per order'] = burdened_costs['Supplies'] / burdened_costs['Number of orders']
    burdened_costs['Other fees per order'] = burdened_costs['Other fees'] / burdened_costs['Number of orders']
    burdened_costs['Costs per order'] = burdened_costs[['Shipping costs per order',
                                                        'Supplies costs per order',
                                                        'Other fees per order']].sum(axis=1)
    
    burdened_costs.sort_values('Transaction creation date')
    
    return burdened_costs

def get_burdened_rates(cumulative_df):
    
    burdened_supplies = cumulative_df['Supplies costs per order'][-1]
    burdened_shipping = cumulative_df['Shipping costs per order'][-1]
    burdened_other = cumulative_df['Other fees per order'][-1]
    burdened_rates = {'supplies': burdened_supplies,
                      'shipping': burdened_shipping,
                      'other': burdened_other}
    
    return burdened_rates
    
# %% Sections.

# %% Run the application.
if __name__ == "__main__":
    app.run_server(host="localhost",
                   debug=True,
                   use_reloader=False)