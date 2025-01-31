from django.contrib.auth.models import User
from django.test import TestCase

from home.models import Label, News, Question, QuestionReaction, Reply, UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johndoe", password="password123")
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user, defaults={"first_name": "John", "last_name": "Doe"}
        )
        self.user_profile.first_name = "John"
        self.user_profile.last_name = "Doe"
        self.user_profile.save()

    def test_user_profile_creation(self):
        """Test UserProfile creation and string representation."""
        self.assertEqual(self.user_profile.first_name, "John")
        self.assertEqual(self.user_profile.last_name, "Doe")
        self.assertEqual(str(self.user_profile), "johndoe Profile")

    def test_user_profile_association(self):
        """Test UserProfile is linked to the correct user."""
        self.assertEqual(self.user_profile.user.username, "johndoe")
        self.assertTrue(isinstance(self.user_profile, UserProfile))


class QuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.label, _ = Label.objects.get_or_create(
            name="Python", defaults={"color": "#3776AB"}
        )

        cls.user = User.objects.create_user(username="janedoe", password="password123")
        cls.question = Question.objects.create(
            title="What is Django?",
            content="Can someone explain Django's purpose?",
            user=cls.user,
        )
        cls.question.labels.add(cls.label)

    def test_question_labels(self):
        self.assertIn(self.label, self.question.labels.all())

    def test_question_user(self):
        self.assertEqual(self.question.user, self.user)

    def test_label_name(self):
        self.assertEqual(self.label.name, "Python")

    def test_question_instance(self):
        """Test the Question instance."""
        self.assertIsInstance(self.question, Question)


class ReplyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="janedoe", password="password123")
        self.question = Question.objects.create(
            title="What is Django?",
            content="Can someone explain Django's purpose?",
            user=self.user,
        )
        self.reply = Reply.objects.create(
            content="Django is a web framework for rapid development.",
            question=self.question,
            user=self.user,
        )

    def test_reply_creation(self):
        self.assertEqual(self.reply.content, "Django is a web framework for rapid development.")
        self.assertEqual(self.reply.question, self.question)
        self.assertEqual(self.reply.user.username, "janedoe")

    def test_reply_instance(self):
        """Test the Reply instance."""
        self.assertIsInstance(self.reply, Reply)


class QuestionReactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="janedoe", password="password123")
        self.question = Question.objects.create(
            title="What is Django?",
            content="Can someone explain Django's purpose?",
            user=self.user,
        )
        self.reaction = QuestionReaction.objects.create(
            question=self.question, user=self.user, reaction_type=QuestionReaction.LIKE
        )

    def test_question_reaction(self):
        self.assertEqual(self.reaction.reaction_type, QuestionReaction.LIKE)
        self.assertEqual(self.reaction.user.username, "janedoe")
        self.assertEqual(self.reaction.question.title, "What is Django?")

    def test_question_reaction_instance(self):
        """Test the QuestionReaction instance."""
        self.assertIsInstance(self.reaction, QuestionReaction)


class NewsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="janedoe", password="password123")
        self.news = News.objects.create(
            title="Django 4.0 Released",
            content="The Django team has released version 4.0.",
            author=self.user,
            is_active=True,
        )

    def test_news_creation(self):
        self.assertEqual(self.news.title, "Django 4.0 Released")
        self.assertEqual(self.news.content, "The Django team has released version 4.0.")
        self.assertEqual(self.news.author.username, "janedoe")
        self.assertTrue(self.news.is_active)

    def test_news_instance(self):
        """Test the News instance."""
        self.assertIsInstance(self.news, News)
