from django.test import Client, TestCase
from django.urls import reverse

from home.models import Question, Reply, UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user_profile = UserProfile.objects.create(
            user_id=1,  # Example ID; adjust for your schema
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
        )

    def test_user_profile_creation(self):
        """Test the creation of a UserProfile instance."""
        self.assertEqual(self.user_profile.first_name, "John")
        self.assertEqual(self.user_profile.last_name, "Doe")
        self.assertEqual(
            str(self.user_profile), "John Doe"
        )  # Adjust based on `__str__`


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            title="Sample Question",
            content="What is Django?",
            likes_count=5,
            dislikes_count=0,
        )

    def test_question_creation(self):
        """Test the creation of a Question instance."""
        self.assertEqual(self.question.title, "Sample Question")
        self.assertEqual(self.question.likes_count, 5)


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
        """Test the creation of a Reply instance."""
        self.assertEqual(self.reply.question.title, "Sample Question")
        self.assertEqual(self.reply.content, "Django is a web framework.")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home:index")  # Adjust based on your URL patterns
        self.login_url = reverse("home:login")  # Adjust as needed

    def test_home_page_status_code(self):
        """Test if the home page loads successfully."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_template(self):
        """Test if the login page uses the correct template."""
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
        """Test the form with valid data."""
        form = QuestionForm(data=self.valid_data)  # Replace with your form class
        self.assertTrue(form.is_valid())

    def test_question_form_invalid(self):
        """Test the form with invalid data."""
        form = QuestionForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())
