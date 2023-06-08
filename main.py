import requests
import time
import json
import hmac
import hashlib

class OKEx:
    def __init__(self, api_key, api_secret, passphrase, is_testnet=False):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.API_PASSPHRASE = passphrase
        self.endpoint = 'https://www.okex.com'
        if is_testnet:
            self.endpoint = 'https://www.okex.com'  # testnet endpoint here
        
    def _generate_signature(self, method, request_path, timestamp, body=''):
        prehash = str(timestamp) + method.upper() + request_path
        if body:
            prehash += body
        signature = hmac.new(bytes(self.API_SECRET, 'utf-8'), bytes(prehash, 'utf-8'), hashlib.sha256).hexdigest()
        return signature
        
    def _make_request(self, method, path, params=None, data=None, auth=True):
        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}
        if auth:
            timestamp = str(int(time.time() * 1000))
            headers['OK-ACCESS-KEY'] = self.API_KEY
            headers['OK-ACCESS-SIGN'] = self._generate_signature(method, path, timestamp, data)
            headers['OK-ACCESS-TIMESTAMP'] = timestamp
            headers['OK-ACCESS-PASSPHRASE'] = self.API_PASSPHRASE
        resp = requests.request(method, url, headers=headers, params=params, data=data)
        try:
            return resp.json()
        except ValueError:
            return resp.text
        
    def get_spot_accounts(self):
        path = '/api/v5/account/balance'
        params = {'ccy': 'USD'}
        return self._make_request('GET', path, params=params)
    
    def get_spot_ticker(self, symbol):
        path = f'/api/v5/market/ticker?instId={symbol}'
        return self._make_request('GET', path)
    
    def get_future_accounts(self, symbol):
        path = '/api/v5/account/balance'
        params = {'uType': 'isolated', 'instId': symbol, 'ccy': 'USD'}
        return self._make_request('GET', path, params=params)
    
    def get_future_ticker(self, symbol):
        path = f'/api/v5/market/ticker?instId={symbol}'
        return self._make_request('GET', path)
    
    def place_order(self, symbol, side, quantity, price, order_type, leverage=None):
        if 'SWAP' in symbol:
            path = '/api/v5/trade/order'
            params = {'instId': symbol, 'tdMode': 'cross', 'ordType': order_type, 'px': price, 'sz': quantity}
            data = json.dumps(params)
        else:
            path = '/api/v5/trade/order'
            params = {'instId': symbol, 'tdMode': 'isolated', 'side': side, 'ordType': order_type, 'px': price, 'sz': quantity}
            if leverage:
                params['lev'] = leverage
            data = json.dumps(params)
        return self._make_request('POST', path, data=data, auth=True)

# Example usage
okex = OKEx('API_KEY_HERE', 'API_SECRET_HERE', 'API_PASSPHRASE_HERE')
spot_accounts = okex.get_spot_accounts()
spot_ticker = okex.get_spot_ticker('BTC-USDT')
future_accounts = okex.get_future_accounts('BTC-USD-211231')
future_ticker = okex.get_future_ticker('BTC-USD-211231')
place_order = okex.place_order('BTC-USD-211231', 'buy', 10, 60000, 'limit', leverage=10)