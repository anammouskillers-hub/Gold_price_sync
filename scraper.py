import json
import os
import google.auth.transport.requests
from google.oauth2 import service_account
import requests


def get_access_token():
    """توليد Access Token معتمد باستخدام Service Account JSON"""
    cred_json = os.environ.get('FIREBASE_CREDENTIALS')
    if not cred_json:
        raise Exception('لم يتم العثور على FIREBASE_CREDENTIALS في Secrets!')

    cred_dict = json.loads(cred_json)
    scopes = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/firebase.database',
    ]

    credentials = service_account.Credentials.from_service_account_info(
        cred_dict, scopes=scopes
    )
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    return credentials.token


def update_firebase_rates():
    # 1. جلب Token التوثيق
    try:
        access_token = get_access_token()
    except Exception as e:
        print(f'فشل التوثيق: {e}')
        return

    # 2. جلب الأسعار المباشرة من الـ API
    api_url = 'https://cygrlhmnmckoefefnsjc.supabase.co/functions/v1/public-api/latest'
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('success'):
            print('لم يتم استلام بيانات صالحة من الـ API.')
            return

        rates_data = data.get('data')

        # 3. إعداد البيانات المُراد حفظها
        payload = {
            'rates': rates_data,
            'status': 'success',
            'updated_at': {'.sv': 'timestamp'},
        }

        # 4. الكتابة المباشرة في الجذر الأساسي لقاعدة البيانات
        db_url = (
            'https://gold-tracker-6d16f-default-rtdb.firebaseio.com/.json'
        )
        db_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        put_response = requests.put(
            db_url, json=payload, headers=db_headers, timeout=10
        )

        if put_response.status_code == 200:
            print('==================================================')
            print(' تم تحديث البيانات بنجاح في Realtime Database!')
            print(f'سعر شراء صنعاء (USD): {rates_data.get("sanaa_usd_buy")}')
            print('==================================================')
        else:
            print(f'فشل التحديث. كود الاستجابة: {put_response.status_code}')
            print(f'التفاصيل: {put_response.text}')

    except Exception as e:
        print(f'حدث خطأ أثناء التنفيذ: {e}')


if __name__ == '__main__':
    update_firebase_rates()
    
