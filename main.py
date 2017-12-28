import author
import requests
import pandas as pd
import json
import urllib
import sqlite3
import sql_tools as st
import ryan_tools as rt
from datetime import datetime
from dateutil.relativedelta import relativedelta



def get_sites():
    r = requests.get('https://www.googleapis.com/webmasters/v3/sites', params = doc.sign({}) )
    sites = []
    for site in r.json()['siteEntry']:
        sites.append(site['siteUrl'])
    return sites

def get_website_info(start_row, start_date, end_date):
    
    
    url = 'https://www.googleapis.com/webmasters/v3/sites/{}/searchAnalytics/query'.format(site)
    
    
    filters = [{
                "dimension": 'country',
              "operator": 'equals',
              "expression": 'USA'
        }]
    
    filters = {'filters': filters}
    
    params = { 
    "startDate": to_google_date(start_date),
    "endDate": to_google_date(end_date),
    "dimensions": ['query'],
    'startRow': start_row, 
    'dimensionFilterGroups': [filters]
    }
    
    headers = {'Content-type': 'application/json',
               'Authorization' : 'Bearer %s' % doc.sign({})['access_token']}
    
    r = requests.post(url,data = json.dumps(params),  headers = headers)
    json_data = r.json()
    try:
        rows = json_data['rows']
    except KeyError:
        print(json_data)
        raise KeyError
    return rows


def get_until_exhausted(start_date, end_date):
    done = False
    rows = []
    i = 0
    while not done:
        try:
            result = get_website_info(i, start_date, end_date)
            i = i + 1000
            print(i)
            rows.extend(result)
        except KeyError:
            done = True
            
            
    x = pd.DataFrame(rows)
    x['query'] = x['keys'].apply(lambda x: x[0])
    del x['keys']
    return x
    
    
def save_data(data):
    data['updatedate'] = datetime.today()
    pick =  st.IcePick(sqlite3, 'marketing.db')
    try:
        max_id = pick.read_sql('SELECT MAX(id) max from keywords').loc[0]['max']
        data.index = range(max_id, max_id + len(data))
    except :
        pass
    data.index.name = 'id'
    with sqlite3.connect('marketing.db', check_same_thread = False) as con:
        data.to_sql('keywords', con, if_exists = 'append')
        con.commit()
    con.close()
    
def to_google_date(date):
    return date.strftime('%Y-%m-%d')
    


def get_month_year(month, year):
    start = pd.to_datetime('{}/{}/01'.format(year, month))
    end = rt.last_date_of_month(start)
    data = get_until_exhausted(start, end)
    data['month'] = month
    data['year'] = year
    return data
    
if __name__ == '__main__':
    doc = author.Author(['https://www.googleapis.com/auth/webmasters.readonly'])
    site = get_sites()[0]
    site = urllib.parse.quote_plus(site)