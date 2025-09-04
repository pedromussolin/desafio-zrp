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

def get_asset_price(asset_code):
    """
    Simula uma chamada para API externa para buscar preço do ativo.

    Para simular latência da API e rate limiting:
    - Adiciona um delay aleatório
    - Simula falhas intermitentes (1 em cada 10 chamadas)
    - Simula rate limit (se mais de 5 chamadas em 60 segundos)

    Args:
        asset_code (str): Código do ativo a ser precificado

    Returns:
        float: Preço do ativo

    Raises:
        Exception: Se falha ou rate limit
    """
    # Simular delay API
    time.sleep(random.uniform(0.2, 1.5))

    # Simular falha (1 em cada 10)
    if random.randint(1, 10) == 1:
        logger.warning(f"Simulated API failure for {asset_code}")
        raise Exception("API Error: Pricing service temporarily unavailable")

    # Simular price range para diferentes ativos
    base_price = 0

    # Preços baseados no código do ativo
    if "PETR" in asset_code:
        base_price = 28.5
    elif "VALE" in asset_code:
        base_price = 68.2
    elif "ITUB" in asset_code:
        base_price = 32.7
    elif "BBDC" in asset_code:
        base_price = 19.8
    elif "MGLU" in asset_code:
        base_price = 4.5
    else:
        # Para outros ativos, preço aleatório entre 10-100
        base_price = random.uniform(10, 100)

    # Adicionar variação aleatória (+/- 5%)
    variation = random.uniform(-0.05, 0.05)
    final_price = round(base_price * (1 + variation), 2)

    logger.info(f"Price for {asset_code}: {final_price}")
    return final_price

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

# Alias para compatibilidade com testes antigos
fetch_price = get_asset_price
