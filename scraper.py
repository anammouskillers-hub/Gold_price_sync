import json
import os
import firebase_admin
from firebase_admin import credentials, db
import requests

# 1. تهيئة الاتصال بـ Firebase
cred_json = os.environ.get('FIREBASE_CREDENTIALS')

if cred_json:
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)

    # تم وضع رابط قاعدة البيانات الخاص بك هنا
    firebase_admin.initialize_app(
        cred,
        {
            'databaseURL': (
                'https://gold-tracker-6d16f-default-rtdb.firebaseio.com'
            )
        },
    )


def update_yemen_rates_to_firebase():
    # رابط الـ API المباشر لأسعار اليمن (صنعاء وعدن والذهب)
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

            # 2. رفع الأسعار إلى المسار المحدد داخل قاعدة بياناتك
            ref = db.reference("currency_rates/latest")
            ref.set(
                {
                    "rates": rates_data,
                    "updated_at": {
                        ".sv": "timestamp"
                    },  # توقيت التحديث التلقائي من Firebase
                }
            )

            print("تم التحديث بنجاح في قاعدة البيانات gold-tracker!")
            print(f"سعر صنعاء (USD): {rates_data.get('sanaa_usd_buy')}")
            print(f"سعر عدن (USD): {rates_data.get('aden_usd_buy')}")
        else:
            print("فشل في استلام البيانات من الـ API")

    except Exception as e:
        print(f"حدث خطأ أثناء التحديث: {e}")


if __name__ == "__main__":
    update_yemen_rates_to_firebase()
    
