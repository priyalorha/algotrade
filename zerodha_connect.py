import json
import logging

import requests

log = logging.getLogger(__name__)

base_url = "https://kite.zerodha.com"
login_url = "https://kite.zerodha.com/api/login"
twofa_url = "https://kite.zerodha.com/api/twofa"


class ZerodhaConnection:

    def __init__(self,
                 userId,
                 password,
                 two_fa):
        self.userId = userId
        self.password = password
        self.twofa = two_fa
        self.s = self.reqsession = requests.Session()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        }
        self.reqsession.headers.update(headers)
        self.chunkjs = {}

    _default_root_uri = "https://kite.zerodha.com"

    def load_session(self, path=None):
        self.enc_token = self.reqsession.cookies['enctoken']

    def _user_agent(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

    def login_step1(self):
        self.r = self.reqsession.get(base_url)
        self.r = self.reqsession.post(login_url,
                                      data={"user_id": self.userId,
                                            "password": self.password})
        j = json.loads(self.r.text)
        return j

    def login_step2(self, j):
        data = {"user_id": self.userId,
                "request_id": j['data']["request_id"],
                "twofa_value": self.twofa}
        self.r = self.s.post(twofa_url, data=data)
        j = json.loads(self.r.text)
        return j

    def login(self):
        j = self.login_step1()
        if j['status'] == 'error':
            raise Exception(j['message'])

        j = self.login_step2(j)
        if j['status'] == 'error':
            raise Exception(j['message'])
        self.enc_token = self.r.cookies['enctoken']
        print(self.enc_token)
        return j

    def oms_headers(self):
        h = {'authorization': f"enctoken {self.enc_token}", 'referer': 'https://kite.zerodha.com/dashboard',
             'x-kite-version': '2.4.0', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors',
             'sec-fetch-dest': 'empty', 'x-kite-userid': self.userId}
        return h

    def profile(self):
        import requests

        url = "https://kite.zerodha.com/oms/user/profile/full"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)
        return response.text

    def position(self):
        import requests

        url = "https://kite.zerodha.com/oms/portfolio/positions"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    def holdings(self):
        import requests

        url = "https://kite.zerodha.com/oms/portfolio/holdings"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    def MarketWatch(self):
        import requests

        url = "https://kite.zerodha.com/api/marketwatch"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    def marketOverview(self):
        import requests

        url = "https://kite.zerodha.com/api/market-overview"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    # get funds
    def margin(self):
        import requests

        url = "https://kite.zerodha.com/oms/user/margins"

        payload = {}

        response = requests.request("GET", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    def orders(self):
        import requests

        url = "https://kite.zerodha.com/oms/orders"

        payload = {}

        response = requests.request("GET", url,
                                    headers=self.oms_headers(), data=payload)

        print(response.text)

    def cost(self,
             exchange,
             trading_symbol,
             transaction_type,
             variety,
             product,
             order_type,
             quantity,
             price):
        import requests

        url = "https://kite.zerodha.com/oms/margins/orders"

        payload = [{"exchange": exchange,
                    "tradingsymbol": trading_symbol,
                    "transaction_type": transaction_type,
                    "variety": variety,
                    "product": product,
                    "order_type": order_type,
                    "quantity": quantity,
                    "price": price

                    }]

        payload = json.dumps(payload)

        response = requests.request("POST", url, headers=self.oms_headers(), data=payload)

        print(response.text)

    def main(self):
        self.login()






