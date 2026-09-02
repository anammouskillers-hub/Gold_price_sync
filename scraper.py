import json
import os
import requests


def update_firebase_via_rest():
    # 1. جلب البيانات من الـ API المباشر
    api_url = "https://cygrlhmnmckoefefnsjc.supabase.co/functions/v1/public-api/latest"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print("لم يتم العثور على بيانات من المصدر.")
            return

        rates_data = data.get("data")
        print("تم جلب البيانات بنجاح من الـ API:")
        print(rates_data)

        # 2. تجهيز البيانات للتخزين
        payload = {
            "rates": rates_data,
            "updated_at": {
                ".sv": "timestamp"
            },  # توقيت Firebase التلقائي
        }

        # 3. إرسال البيانات مباشرة لقاعدة بيانات Firebase عبر REST API
        # هذا الرابط المباشر يضمن الكتابة بدون مشاكل الاعتماديات
        db_url = "https://gold-tracker-6d16f-default-rtdb.firebaseio.com/currency_rates/latest.json"

        # طلب PUT لتحديث أو إنشاء البيانات مباشرة
        put_response = requests.put(db_url, json=payload, timeout=10)

        if put_response.status_code == 200:
            print(
                "==========================================================="
            )
            print(" تم تحديث البيانات بنجاح في Realtime Database!")
            print(
                "==========================================================="
            )
        else:
            print(
                f"فشل التحديث في Firebase. كود الاستجابة: {put_response.status_code}"
            )
            print(f"التفاصيل: {put_response.text}")

    except Exception as e:
        print(f"حدث خطأ أثناء تنفيذ العملية: {e}")


if __name__ == "__main__":
    update_firebase_via_rest()
    
