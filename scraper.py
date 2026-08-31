import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase credentials from the GitHub Secret environment variable
cred_json = os.environ.get('FIREBASE_CREDENTIALS')
cred_dict = json.loads(cred_json)

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://YOUR-DATABASE-NAME.firebaseio.com/' # Replace with your Firebase DB URL
})

def scrape_and_update_gold_price():
    url = "https://example-gold-tracking-site.com/live-price" # Replace with your target site
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch page")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    price_element = soup.find("span", {"class": "live-gold-price"}) # Update based on target site HTML
    
    if price_element:
        raw_price = price_element.text.strip()
        clean_price = float(raw_price.replace("$", "").replace(",", ""))
        
        ref = db.reference('metadata/current_gold_price')
        ref.set({
            'price': clean_price,
            'updated_at': {".sv": "timestamp"}
        })
        print(f"Successfully updated Firebase with gold price: {clean_price}")

if __name__ == "__main__":
    scrape_and_update_gold_price()
