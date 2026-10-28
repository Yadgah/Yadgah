from io import BytesIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from . import ai as ai_module
from .ai import get_ai_user
from .models import Label, Question, Reply, Slide, UserProfile


def make_image_file(name="image.jpg", size=(3000, 1200), mode="RGB", fmt="JPEG"):
    buffer = BytesIO()
    Image.new(mode, size, color=(30, 120, 60)).save(buffer, format=fmt)
    return SimpleUploadedFile(name, buffer.getvalue())


class AiAgentUserTests(TestCase):
    """Issue #167: AI_Agent user must be created after migrations."""

    def test_ai_agent_user_exists(self):
        self.assertTrue(User.objects.filter(username="AI_Agent").exists())

    def test_default_labels_exist(self):
        self.assertGreaterEqual(Label.objects.count(), 9)


class ThreadedReplyTests(TestCase):
    """Issue #187: replying to answers & chatting with the AI."""

    def setUp(self):
        self.owner = User.objects.create_user(
            "owner1", "o@example.com", "test-pass-12345"
        )
        self.question = Question.objects.create(
            title="چطور پایتون یاد بگیرم؟",
            content="برای شروع پایتون چه کار کنم؟",
            user=self.owner,
        )
        self.ai_reply = Reply.objects.create(
            content="اول مبانی را یاد بگیر.",
            question=self.question,
            user=get_ai_user(),
        )
        self.url = f"/question/{self.question.id}/"
        self.client.force_login(self.owner)

    def test_reply_to_ai_triggers_ai_followup(self):
        with mock.patch(
            "home.views.get_ai_followup_reply", return_value="ادامه پاسخ AI"
        ) as followup:
            response = self.client.post(
                self.url,
                {"content": "کدوم منبع بهتره؟", "parent_id": self.ai_reply.id},
            )

        self.assertEqual(response.status_code, 302)
        user_reply = Reply.objects.get(parent=self.ai_reply, user=self.owner)
        ai_followup = Reply.objects.get(parent=user_reply)
        self.assertEqual(ai_followup.user.username, "AI_Agent")
        self.assertEqual(ai_followup.content, "ادامه پاسخ AI")

        # The AI received the conversation chain and the new user message.
        _, chain, user_message = followup.call_args[0]
        self.assertIn("اول مبانی را یاد بگیر.", [r.content for r in chain])
        self.assertEqual(user_message, "کدوم منبع بهتره؟")

    def test_plain_reply_is_top_level_and_skips_ai(self):
        with mock.patch("home.views.get_ai_followup_reply") as followup:
            response = self.client.post(self.url, {"content": "پاسخ معمولی"})

        self.assertEqual(response.status_code, 302)
        followup.assert_not_called()
        reply = Reply.objects.get(content="پاسخ معمولی")
        self.assertIsNone(reply.parent)

    def test_reply_to_human_does_not_trigger_ai(self):
        human_reply = Reply.objects.create(
            content="پاسخ انسان", question=self.question, user=self.owner
        )
        with mock.patch("home.views.get_ai_followup_reply") as followup:
            response = self.client.post(
                self.url,
                {"content": "ریپلای روی انسان", "parent_id": human_reply.id},
            )

        self.assertEqual(response.status_code, 302)
        followup.assert_not_called()
        nested = Reply.objects.get(content="ریپلای روی انسان")
        self.assertEqual(nested.parent, human_reply)

    def test_anonymous_post_does_not_crash_or_save(self):
        self.client.logout()
        response = self.client.post(self.url, {"content": "ناشناس"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reply.objects.filter(content="ناشناس").exists())

    def test_thread_is_rendered_nested_with_quote(self):
        Reply.objects.create(
            content="پاسخ تو در تو",
            question=self.question,
            parent=self.ai_reply,
            user=self.owner,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "reply-children")
        self.assertContains(response, "در پاسخ به")
        self.assertContains(response, "هوش مصنوعی")  # AI badge
        self.assertContains(response, "پاسخ تو در تو")

    def test_parent_from_other_question_is_ignored(self):
        other_question = Question.objects.create(
            title="سوال دیگر", content="محتوا", user=self.owner
        )
        other_reply = Reply.objects.create(
            content="پاسخ سوال دیگر", question=other_question, user=self.owner
        )
        self.client.post(self.url, {"content": "پاسخ", "parent_id": other_reply.id})
        reply = Reply.objects.get(content="پاسخ", question=self.question)
        self.assertIsNone(reply.parent)


class AiFollowupPromptTests(TestCase):
    """The pre-prompt must tell apart user and AI messages (#187)."""

    def test_prompt_labels_speakers(self):
        owner = User.objects.create_user("owner2", "o2@example.com", "pass12345x")
        question = Question(title="عنوان سوال", content="متن سوال", user=owner)
        ai_reply = Reply(content="جواب AI", user=get_ai_user())
        user_msg = Reply(content="سوال بعدی کاربر", user=owner)

        with mock.patch.object(ai_module, "_request_ai") as request_ai:
            ai_module.get_ai_followup_reply(
                question, [ai_reply, user_msg], "و سوال آخر"
            )

        prompt = request_ai.call_args[0][0]
        self.assertIn("[Question] عنوان سوال", prompt)
        self.assertIn("[AI] جواب AI", prompt)
        self.assertIn("[User] سوال بعدی کاربر", prompt)
        self.assertIn("[User] و سوال آخر", prompt)


class ImageOptimizationTests(TestCase):
    """Issue #175: blog's WebP optimization reused in home."""

    def tearDown(self):
        for slide in Slide.objects.all():
            if slide.thumbnail:
                slide.thumbnail.delete(save=False)
        for profile in UserProfile.objects.all():
            if profile.avatar:
                profile.avatar.delete(save=False)

    def test_slide_thumbnail_converted_to_webp_and_downscaled(self):
        slide = Slide.objects.create(
            title="اسلاید تست",
            description="توضیح",
            thumbnail=make_image_file("thumb.jpg", size=(3000, 1200)),
        )
        self.assertTrue(slide.thumbnail.name.endswith(".webp"))
        with slide.thumbnail.open("rb") as f:
            width, _ = Image.open(f).size
        self.assertLessEqual(width, 1600)

    def test_slide_thumbnail_not_reconverted_on_resave(self):
        slide = Slide.objects.create(
            title="اسلاید تست",
            description="توضیح",
            thumbnail=make_image_file("thumb.jpg"),
        )
        name_after_create = slide.thumbnail.name
        slide.title = "عنوان جدید"
        slide.save()
        self.assertEqual(slide.thumbnail.name, name_after_create)

    def test_avatar_converted_to_webp_and_downscaled(self):
        user = User.objects.create_user("avataruser", "a@example.com", "pass12345x")
        profile = user.userprofile
        profile.avatar = make_image_file("avatar.jpg", size=(1200, 1200))
        profile.save()
        self.assertTrue(profile.avatar.name.endswith(".webp"))
        with profile.avatar.open("rb") as f:
            width, _ = Image.open(f).size
        self.assertLessEqual(width, 512)
