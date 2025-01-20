from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from home.models import Question, Reply, UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="johndoe")  # Create the user
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.user_profile.first_name, "John")
        self.assertEqual(self.user_profile.last_name, "Doe")


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            title="Sample Question",
            content="What is Django?",
            dislikes_count=0,
        )
        # If likes_count is ManyToManyField, assign related objects:
        # related_user = User.objects.create(username="test_user")
        # self.question.likes_count.set([related_user])

    def test_question_creation(self):
        self.assertEqual(self.question.title, "Sample Question")
        # Add checks for ManyToManyField if necessary:
        # self.assertEqual(self.question.likes_count.count(), 1)


class ReplyModelTest(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            title="Sample Question", content="What is Django?"
        )
        self.reply = Reply.objects.create(
            question=self.question,
            content="Django is a web framework.",
        )

    def test_reply_creation(self):
        self.assertEqual(self.reply.question.title, "Sample Question")
        self.assertEqual(self.reply.content, "Django is a web framework.")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("index")  # Adjust as per your URLs
        self.login_url = reverse("login")  # Adjust as needed

    def test_home_page_status_code(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_template(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, "login.html")

