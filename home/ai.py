import requests
import json

def get_ai_reply(question):
    try:
        response = requests.get(
            "https://yw85opafq6.execute-api.us-east-1.amazonaws.com/default/boss_mode_15aug",
            params={"text": question, "country": "Asia", "user_id": "usery3peypi26p"},
            timeout=10
        )

        # بررسی نوع پاسخ
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = response.json()
        else:
            # اگر رشته برگشت داده شده، تلاش کن دستی پارس کنیم
            try:
                data = json.loads(response.text)
            except Exception:
                return f"پاسخ غیرمنتظره از سرور: {response.text[:100]}..."

        if isinstance(data, dict):
            return data.get("reply", "AI پاسخی ارسال نکرد.")
        else:
            return f"پاسخ در قالب دیکشنری نبود: {data}"

    except Exception as e:
        return f"خطا در تماس با API: {e}"
