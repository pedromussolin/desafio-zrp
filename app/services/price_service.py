from flask import current_app
import requests
import random
import time

class PriceService:
    def __init__(self):
        self.api_url = current_app.config['PRICE_API_URL']
        self.rate_limit = current_app.config['PRICE_API_RATE_LIMIT']

    def fetch_price(self, asset_code):
        self.simulate_rate_limiting()
        response = requests.get(f"{self.api_url}/prices/{asset_code}")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def simulate_rate_limiting(self):
        if random.random() < self.rate_limit:
            time.sleep(1)  # Simulate a delay for rate limiting

    def fetch_prices_bulk(self, asset_codes):
        prices = {}
        for code in asset_codes:
            try:
                prices[code] = self.fetch_price(code)
            except Exception as e:
                prices[code] = {'error': str(e)}
        return prices