from celery import shared_task
import requests
from app.models.price import Price
from app import db

@shared_task
def fetch_asset_price(asset_code):
    try:
        response = requests.get(f'https://api.example.com/prices/{asset_code}')
        response.raise_for_status()
        price_data = response.json()
        
        price = Price(
            asset_code=asset_code,
            current_price=price_data['current_price'],
            timestamp=price_data['timestamp']
        )
        
        db.session.add(price)
        db.session.commit()
        
        return {'status': 'success', 'data': price_data}
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'message': str(e)}