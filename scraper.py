import json
import os
import requests


def update_firebase_rates():
    # 1. جلب مفتاح الأمان لـ Firebase من متغيرة البيئة
    db_secret = os.environ.get('FIREBASE_DB_SECRET')

    # 2. بناء الرابط المباشر لقاعدة البيانات مع التوثيق (Auth)
    if db_secret:
        db_url = f'https://gold-tracker-6d16f-default-rtdb.firebaseio.com/currency_rates/latest.json?auth={db_secret}'
    else:
        # رابط احتياطي في حال تم فتح الـ Rules يدويًا
        db_url = 'https://gold-tracker-6d16f-default-rtdb.firebaseio.com/currency_rates/latest.json'

    # 3. جلب الأسعار المباشرة من الـ API
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
            print('لم يتم استلام بيانات من الـ API.')
            return

        rates_data = data.get('data')

        # 4. إعداد الهيكل المُراد حفظه في Firebase
        payload = {
            'rates': rates_data,
            'updated_at': {'.sv': 'timestamp'},
        }

        # 5. إرسال البيانات مباشرة إلى Firebase
        put_response = requests.put(db_url, json=payload, timeout=10)

        if put_response.status_code == 200:
            print('==================================================')
            print('تم تحديث البيانات بنجاح في Realtime Database!')
            print(f'سعر شراء صنعاء (USD): {rates_data.get("sanaa_usd_buy")}')
            print(f'سعر شراء عدن (USD): {rates_data.get("aden_usd_buy")}')
            print('==================================================')
        else:
            print(f'فشل التحديث. كود الاستجابة: {put_response.status_code}')
            print(f'السبب: {put_response.text}')

    except Exception as e:
        print(f'حدث خطأ غير متوقع: {e}')


if __name__ == '__main__':
    update_firebase_rates()
    
