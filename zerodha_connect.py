import json
import logging
import time

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://kite.zerodha.com"
LOGIN_URL = "https://kite.zerodha.com/api/login"
TWOFA_URL = "https://kite.zerodha.com/api/twofa"


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

        self.login()

    _default_root_uri = "https://kite.zerodha.com"

    def load_session(self, path=None):
        self.enc_token = self.reqsession.cookies['enctoken']

    def _user_agent(self) -> str:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

    def login_step1(self) -> dict:
        self.r = self.reqsession.get(BASE_URL)
        self.r = self.reqsession.post(LOGIN_URL,
                                      data={"user_id": self.userId,
                                            "password": self.password})
        j = json.loads(self.r.text)
        return j

    def login_step2(self, j) -> dict:
        data = {"user_id": self.userId,
                "request_id": j['data']["request_id"],
                "twofa_value": self.twofa}
        self.r = self.s.post(TWOFA_URL, data=data)
        j = json.loads(self.r.text)
        return j

    def login(self) -> dict:
        j = self.login_step1()
        if j['status'] == 'error':
            raise Exception(j['message'])

        j = self.login_step2(j)
        if j['status'] == 'error':
            raise Exception(j['message'])
        self.enc_token = self.r.cookies['enctoken']

        return j

    def oms_headers(self) -> dict:
        return {'authorization': f"enctoken {self.enc_token}", 'referer': 'https://kite.zerodha.com/dashboard',
                'x-kite-version': '2.4.0', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty', 'x-kite-userid': self.userId}

    def profile(self):

        return requests.request("GET",
                                BASE_URL + "/oms/user/profile/full",
                                headers=self.oms_headers(),
                                data={})

    def position(self):
        return requests.request("GET",
                                BASE_URL + "/oms/portfolio/positions",
                                headers=self.oms_headers(),
                                data={})

    def holdings(self):

        return requests.request("GET",
                                BASE_URL + "/oms/portfolio/holdings",
                                headers=self.oms_headers(),
                                data={})

    def MarketWatch(self):

        return requests.request("GET",
                                BASE_URL + "/api/marketwatch",
                                headers=self.oms_headers(),
                                data={})

    def marketOverview(self):

        return requests.request("GET",
                                BASE_URL + "/api/market-overview",
                                headers=self.oms_headers(),
                                data={})

    # get funds
    def margin(self):

        return requests.request("GET",
                                BASE_URL + "/oms/user/margins",
                                headers=self.oms_headers(),
                                data={})

    def orders(self):

        return requests.request("GET",
                                BASE_URL + "/oms/orders",
                                headers=self.oms_headers(),
                                data={})

    def _order(self,
               URL: str,
               params: str):

        return requests.request("POST",
                                URL,
                                headers=self.oms_headers(),
                                data=params)

    def place_order(self,
                    type: str,
                    variety: str,
                    exchange: str,
                    tradingsymbol: str,
                    transaction_type: str,
                    quantity: int,
                    product: str,
                    order_type: str,
                    price: float = None,
                    validity: str = None,
                    disclosed_quantity: int = None,
                    trigger_price: float = None,
                    squareoff: float = None,
                    stoploss: float = None,
                    trailing_stoploss: float = None,
                    tag=None
                    ):
        params = locals()
        del (params['self'])

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])
        if type == 'place_order':
            URL = BASE_URL + '/oms/nudge/orders'
        if type == 'cost':
            URL = BASE_URL + '/oms/margins/orders'

        del (params['type'])

        return self._order(URL,
                           params=json.dumps([params])
                           )

    def chart(self,
              instrument,
              timeframe,
              from_time,
              to_time):

        return requests.request('GET',
                                BASE_URL + f"/oms/instruments/historical/{instrument}/15minute?user_id={self.userId}&oi=1&"
                                           f"from={from_time}&to={to_time}&ciqrandom={time.time() * 1000}",
                                headers=self.oms_headers()
                                )

    def instrument(self):
        return requests.request('GET',
                                'https://api.kite.trade/instruments',
                                headers=self.oms_headers())

    def main(self):
        self.login()

    def instrument_to_csv(self):
        response = self.instrument().text
        file1 = open("instrument.csv", "w")
        file1.write(response)
        file1.close()

        return response
