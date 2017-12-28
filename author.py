import os, random, string
import requests
import json
import pyperclip
from datetime import datetime, timedelta
import copy

class Author():
    params = {}
    secrets = None
    
    
    def __init__(self, scope = ['https://www.googleapis.com/auth/webmasters.readonly']):
        self.secrets = json.load(open('client_secrets.json'))['installed']
        
        try:
            self.load()
            if set(scope) != set(self.params['scope']):
                self.do_flow(scope)
        except FileNotFoundError:
            self.do_flow(scope)
            self.load()
            
            
    def sign(self, params):
        now = datetime.now()
        if self.params['expiry_date'] < now:
            self.refresh_token()
        params['access_token'] = self.params['access_token']
        return params
    
    def create_random_string(self):
        length = 100
        chars = string.ascii_letters + string.digits + '-._~'
        random.seed = (os.urandom(1024))
        return ''.join(random.choice(chars) for i in range(length))
    
    def get_url(self, scope):
        params = {
                'client_id':self.secrets['client_id'],
                'redirect_uri':'urn:ietf:wg:oauth:2.0:oob',
                'response_type':'code',
                'scope':' '.join(scope),
                'code_challenge':self.params['code_challange'],
                'code_challenge_method':'plain'
                  }
        return requests.Request('GET', 'https://accounts.google.com/o/oauth2/v2/auth',params = params).prepare().url
    
    
    def exchange(self, code):
        params = {
                'code':code,
                'client_id': self.secrets['client_id'],
                'client_secret': self.secrets['client_secret'],
                'redirect_uri':'urn:ietf:wg:oauth:2.0:oob',
                'grant_type':'authorization_code',
                'code_verifier': self.params['code_challange']
                }
        return requests.post('https://www.googleapis.com/oauth2/v4/token',params = params)
    
    
    def refresh_token(self):
        params = {
                'refresh_token': self.params['refresh_token'],
                'client_id': self.secrets['client_id'],
                'client_secret': self.secrets['client_secret'],
                'grant_type':'refresh_token'
                }
        r = requests.post('https://www.googleapis.com/oauth2/v4/token', params = params)
        result = r.json()
        self.params['expiry_date'] = datetime.now() + timedelta(seconds = result['expires_in'] - 60)
        self.params['access_token'] = result['access_token']
        self.save()
        return r
        
    def save(self):
        params = copy.deepcopy(self.params)
        params['expiry_date'] = str(params['expiry_date'])
        json.dump(params,  open('author.json', 'w'))
    
    def load(self):
        self.params = json.load(open('author.json', 'r'))
        self.params['expiry_date'] = datetime.strptime(self.params['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
        return self.params
            
    def do_flow(self, scope):
        
        
        self.params['code_challange'] = self.create_random_string()
        url = self.get_url(scope)
        pyperclip.copy(url)
        print('GO TO THIS URL: < IT HAS ALSO BEEN COPIED TO YOUR CLIPBOARD ALREADY > ')
        print(url)
        code = input('INPUT CODE HERE:')
        if len(code) < 3:
            code = pyperclip.paste()
        final = self.exchange(code)
        
        result = final.json()
        self.params['refresh_token'] = result['refresh_token']
        self.params['expiry_date'] = datetime.now() + timedelta(seconds = result['expires_in'] - 60)
        self.params['access_token'] = result['access_token']
        self.params['scope'] = scope
        self.save()