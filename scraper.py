import json
import os
import requests


def test_and_update():
    # 1. التحقق مما إذا كان GitHub السر يمر بشكل صحيح
    cred_json = os.environ.get('FIREBASE_CREDENTIALS')

    if not cred_json:
        print(
            '❌ خطأ قاتل: لم يتم العثور على FIREBASE_CREDENTIALS! قم بإضافته في GitHub Secrets.'
        )
        return
    else:
        print('✅ تم التحديث: تم العثور على FIREBASE_CREDENTIALS بنجاح.')

    # 2. جلب الأسعار المباشرة
    api_url = 'https://cygrlhmnmckoefefnsjc.supabase.co/functions/v1/public-api/latest'
    try:
        res = requests.get(api_url, timeout=10)
        data = res.json().get('data', {})
        print(f'📊 تم جلب البيانات: USD Aden = {data.get("aden_usd_buy")}')
    except Exception as e:
        print(f'❌ خطأ في جلب بيانات API: {e}')
        return

    # 3. محاولة الكتابة المباشرة إلى Firebase
    db_url = 'https://gold-tracker-6d16f-default-rtdb.firebaseio.com/rates.json'
    payload = {'rates': data, 'status': 'updated'}

    put_res = requests.put(db_url, json=payload, timeout=10)

    print(f'🔄 استجابة Firebase (Code): {put_res.status_code}')
    print(f'📝 نص استجابة Firebase: {put_res.text}')

    if put_res.status_code == 200:
        print('🎉 تم الحفظ بنجاح داخل Firebase!')
    else:
        print(
            '❌ فشلت عملية الكتابة. يرجى التحقق من Rules أو صلاحيات Firebase.'
        )


if __name__ == '__main__':
    test_and_update()
    
