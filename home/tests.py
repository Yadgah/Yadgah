from django.test import Client, TestCase
from django.urls import reverse
from home.models import Question, Reply, UserProfile
from home.forms import QuestionForm  # Ensure the form exists and is imported


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user_profile = UserProfile.objects.create(
            user_id=1,  # Example ID; adjust for your schema
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
            likes_count=5,  # Adjust field usage as needed
            dislikes_count=0,
        )

    def test_question_creation(self):
        self.assertEqual(self.question.title, "Sample Question")
        self.assertEqual(self.question.likes_count, 5)


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


class FormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "title": "A Valid Question",
            "content": "This is a valid question content.",
        }
        self.invalid_data = {"title": "", "content": ""}

    def test_question_form_valid(self):
        form = QuestionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_question_form_invalid(self):
        form = QuestionForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())

