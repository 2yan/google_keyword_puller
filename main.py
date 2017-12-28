import author
import requests
import time
import json
import urllib
doc = author.Author(['https://www.googleapis.com/auth/webmasters.readonly'])


def get_sites():
    r = requests.get('https://www.googleapis.com/webmasters/v3/sites', params = doc.sign({}) )
    sites = []
    for site in r.json()['siteEntry']:
        sites.append(site['siteUrl'])
    return sites

site = get_sites()[0]

site = urllib.parse.quote_plus(site)


def get_website_info(start_row):
    url = 'https://www.googleapis.com/webmasters/v3/sites/{}/searchAnalytics/query'.format(site)
    params = { 
    "startDate": "2017-12-01",
    "endDate": "2017-12-02",
     "dimensions": ['query'],
     'startRow': start_row
    }
    
    headers = {'Content-type': 'application/json',
               'Authorization' : 'Bearer %s' % doc.sign({})['access_token']}
    
    r = requests.post(url,data = json.dumps(params),  headers = headers)

    json_data = r.json()
    
    rows = json_data['rows']
    return rows
    return r
    

rows = get_website_info(start_row)

