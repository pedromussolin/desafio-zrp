import random
import time
import logging
import redis
from flask import current_app
import requests

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

class ExternalPriceError(Exception):
    pass

_redis_client = None

def _redis():
    global _redis_client
    if _redis_client is None:
        url = current_app.config["CELERY_BROKER_URL"]
        _redis_client = redis.Redis.from_url(url)
    return _redis_client

def get_asset_price(asset_code: str) -> float:
    cfg = current_app.config
    # Rate limit key
    minute_key = f"price_rl:{int(time.time() // 60)}"
    r = _redis()
    pipe = r.pipeline()
    pipe.incr(minute_key)
    pipe.expire(minute_key, 70)
    count, _ = pipe.execute()

    if count > cfg["PRICE_API_RATE_LIMIT_PER_MINUTE"]:
        logger.warning("Rate limit exceeded")
        raise RateLimitError("Rate limit exceeded")

    # Simular falha
    if random.random() < cfg["PRICE_API_FAILURE_RATE"]:
        logger.error("Simulated external API failure")
        raise ExternalPriceError("External API failure")

    price = round(random.uniform(10, 100), 2)
    if price <= 0:
        raise ExternalPriceError("Invalid price <= 0")

    logger.info(f"Price fetched asset={asset_code} price={price}")
    return price

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
