import json
import os
import firebase_admin
from firebase_admin import credentials, db
import requests

# 1. تهيئة الاتصال بـ Firebase
cred_json = os.environ.get('FIREBASE_CREDENTIALS')

if cred_json:
    try:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)

        # رابط قاعدة البيانات الخاص بك
        firebase_admin.initialize_app(
            cred,
            {
                'databaseURL': (
                    'https://gold-tracker-6d16f-default-rtdb.firebaseio.com'
                )
            },
        )
        print('تم الاتصال بـ Firebase بنجاح!')
    except Exception as e:
        print(f'خطأ في إعداد Firebase Credentials: {e}')


def update_yemen_rates():
    # رابط API مباشر لجلب الأسعار
    api_url = "https://cygrlhmnmckoefefnsjc.supabase.co/functions/v1/public-api/latest"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            rates_data = result.get("data")

            # 2. الكتابة في الجذر الأساسي لقاعدة البيانات للتأكد من وصولها
            ref = db.reference('/')
            ref.update(
                {
                    'latest_rates': rates_data,
                    'last_updated': {'.sv': 'timestamp'},
                }
            )

            print('>>> تم حفظ البيانات بنجاح داخل Firebase! <<<')
            print(rates_data)
        else:
            print('الـ API لم يرجع بيانات صالحة.')

    except Exception as e:
        print(f'حدث خطأ أثناء كتابة البيانات: {e}')


if __name__ == '__main__':
    update_yemen_rates()
    
