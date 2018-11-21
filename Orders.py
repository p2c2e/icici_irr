
# coding: utf-8

# In[82]:


import csv
import numpy as np
import pandas as pd
from dateutil.parser import parse
import datetime
import glob
import numpy as np
from scipy.optimize import fsolve
from datetime import date


def load_xls_files(path='.', delimiter=',', header=0):
    allFiles = glob.glob(path + "/*.xls")
    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        df = pd.read_csv(file_, delimiter=delimiter, index_col=None, header=header)
        list_.append(df)
    frame = pd.concat(list_, ignore_index=True)
    return frame


# In[83]:

def date_diff(df, column_name, fmt='%d-%m-%Y'):
    # '%d-%m-%Y %H:%M:%S'
    df['DateDiff'] = df[column_name].apply(lambda x: datetime.datetime.strptime(x, fmt))
    df['DateDiff'] = df['DateDiff'].apply(lambda x: datetime.datetime.now() - x)
    df['DateDiff'] = df['DateDiff']/ np.timedelta64(1, 'D')
    df['DateDiff'] = -df['DateDiff']/ 365

data = load_xls_files(path='./OrderBooks', delimiter='\t', header=0)
date_diff(data, 'Date', fmt='%d-%m-%Y %H:%M:%S')
data.loc[data['Transaction Type'].isin(['SO', 'Redemption']), 'Amount'] = -data['Amount']
data = data[['Scheme Name', 'Amount', 'DateDiff']]

divdata = load_xls_files(path='./Dividends', delimiter='\t', header=0)
divdata.rename(columns={'Gross Amount(rs.)':'Amount'}, inplace=True)
date_diff(divdata, 'Record Date')
divdata = divdata[['Scheme Name', 'Amount', 'DateDiff']]
divdata['Amount'] = - divdata['Amount'] # incoming amount ...


# In[84]:

def npv(irr, cfs, yrs):  
    return np.sum(cfs / (1. + irr) ** yrs)

def irr(cfs, yrs, x0, **kwargs):
    return np.asscalar(fsolve(npv, x0=x0, args=(cfs, yrs), **kwargs))

df = pd.concat([data, divdata])

# In[89]:

# Load the positions file ....
positions = pd.read_csv('8500544984_PortFolioMF (1).xls', delimiter='\t')
positions.head()
positions = positions[['Scheme', 'Value at NAV']]
positions['Amount'] = -positions['Value at NAV'] # We can use rename after testing

positions = positions[['Scheme', 'Amount']]
positions.rename(columns={'Scheme':'Scheme Name'}, inplace=True)
positions['DateDiff'] = 0

df = df.append(positions)
#pvals = positions['Scheme Name'].unique()
#dvals = df['Scheme Name'].unique()
#print([x for x in dvals if x not in pvals])

results = pd.DataFrame(columns=['Scheme Name', 'Status', 'Invested', 'P/L', 'Curr Value', 'IRR', 'Yrs'])

for i, dft in df.groupby('Scheme Name'):
    # print('--------------------------------------------')
    # print(i)
    if any(i in s for s in positions['Scheme Name'].values):
        #print(dft)
        cash_flow = dft['Amount'].values
        latest_value = positions.loc[positions['Scheme Name'] == i]['Amount'].values[0]
        #cash_flow = np.append(cash_flow, [latest_value])
        #print(cash_flow)
        years = dft['DateDiff'].values
        #years = np.append(years, [0])
        #print(years)
        #x = irr(cash_flow, years, x0=0.1, maxfev=10000)
        #print(x)
        rate = irr(cash_flow, years, x0=0.1, maxfev=10000) * 100
        #print('id:', i, 'irr:', "{0:.2f}%".format(rate),' max yrs: ','{0:.2f}'.format(-min(years)))
        #print(dft['Amount'].values)
        #print(dft['DateDiff'].values)
        results = results.append({'Scheme Name': i, 'Status': 'Active', 'Invested': np.sum(cash_flow[:-1]), 'P/L': -np.sum(cash_flow), 'Curr Value': -latest_value, 'IRR': rate, 'Yrs': -min(years)}, ignore_index=True)
    else:
        print(i+" is not in the positions <<<<<<<<<<<<<")
        cash_flow = dft['Amount'].values
        years = dft['DateDiff'].values
        #print(cash_flow)
        #print(years)
        rate = irr(cash_flow, years, x0=0.1, maxfev=10000) * 100
        # sum only the positive (investment) flows ....
        results = results.append({'Scheme Name': i, 'Status': 'Completed', 'Invested': np.where(cash_flow>0, cash_flow,0).sum(0), 'P/L': -np.sum(cash_flow), 'Curr Value': 0, 'IRR': rate, 'Yrs': -min(years)}, ignore_index=True)
                       
#from IPython.display import display, HTML
#display(HTML(results.to_html()))
from tabulate import tabulate
#results = results[results['Curr Value'] != 0]    # Remove rows with Amount == 0
print(tabulate(results, headers='keys', tablefmt='psql'))

