import json

import requests


def get_ai_reply(question_content):
    """
    Get reply from AI based only on the question content (@mmd-dll AI API)

    Args:
        question_content (str): Only the content/text of the question

    Returns:
        str: AI's reply
    """
    try:
        response = requests.get(
            "https://text.pollinations.ai/hello",
            params={
                "text": "Say the answer in Persian, and keep the words that don't have a Persian equivalent in English :"
                + question_content,  # noqa: W503
                "country": "Iran",
                "user_id": "usery3peypi26p",
            },
            timeout=10,
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
                return f"{response.text}"

        if isinstance(data, dict):
            return data.get("reply", "AI پاسخی ندارد.")
        else:
            return f"{data}"

    except Exception as e:
        return f"خطا در تماس با API: {e}"
