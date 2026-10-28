import json
from urllib.parse import quote

import requests
from django.contrib.auth.models import User

AI_USERNAME = "AI_Agent"

AI_API_BASE_URL = "https://text.pollinations.ai/"

# Pre-prompt that explains the conversation format to the AI when a user
# replies (quotes) a previous AI answer, so the AI knows which messages
# were written by the user and which ones are its own previous answers.
FOLLOWUP_PRE_PROMPT = (
    "You are the AI assistant of Yadgah, a Persian Q&A website.\n"
    "Below is an ongoing conversation about a question. Messages are "
    "labelled so you can tell who wrote what:\n"
    '- Lines starting with "[Question]" are the original question.\n'
    '- Lines starting with "[AI]" are your own previous answers.\n'
    '- Lines starting with "[User]" are follow-up messages from the user '
    "who asked the question.\n"
    "The last [User] message is a reply to your previous answer. Continue "
    "the conversation and answer it directly, taking the whole "
    "conversation into account. Answer in the same language as the user "
    "(usually Persian). Do not repeat the labels in your answer.\n"
    "\n--- Conversation ---\n"
)


def get_ai_user():
    """Return the (inactive) user account that AI replies are posted as."""
    ai_user, _ = User.objects.get_or_create(
        username=AI_USERNAME,
        defaults={
            "is_active": False,
            "email": "ai@yadgahh.com",
            "first_name": "AI",
            "last_name": "Agent",
        },
    )
    return ai_user


def _request_ai(prompt):
    """Send a prompt to the AI API and return its textual reply."""
    try:
        response = requests.get(
            AI_API_BASE_URL + quote(prompt, safe=""),
            timeout=30,
        )

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


def get_ai_reply(question_content):
    """
    Get reply from AI based only on the question content (@mmd-dll AI API)

    Args:
        question_content (str): Only the content/text of the question

    Returns:
        str: AI's reply
    """
    return _request_ai(question_content)


def get_ai_followup_reply(question, thread_replies, user_message):
    """
    Get a follow-up reply from the AI for an ongoing thread.

    The whole conversation is sent to the AI together with a pre-prompt
    (see FOLLOWUP_PRE_PROMPT) that marks which messages belong to the
    user and which ones are the AI's own previous answers, so the AI can
    continue the discussion in context (issue #187).

    Args:
        question: The Question the thread belongs to.
        thread_replies: Replies of the thread so far, oldest first,
            ending with the AI reply the user replied to.
        user_message (str): The new follow-up message written by the user.

    Returns:
        str: AI's follow-up reply
    """
    lines = [f"[Question] {question.title}\n{question.content}"]
    for reply in thread_replies:
        if reply.user is not None and reply.user.username == AI_USERNAME:
            speaker = "AI"
        else:
            speaker = "User"
        lines.append(f"[{speaker}] {reply.content}")
    lines.append(f"[User] {user_message}")

    prompt = FOLLOWUP_PRE_PROMPT + "\n\n".join(lines)
    return _request_ai(prompt)
