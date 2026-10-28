from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from .models import Post


class PostImageOptimizationTests(TestCase):
    """Issue #175: post images are converted to optimized WebP on save
    (the shared home.utils mechanism), including admin uploads."""

    def setUp(self):
        self.author = User.objects.create_user(
            "author1", "a@example.com", "test-pass-12345"
        )

    def tearDown(self):
        for post in Post.objects.all():
            if post.image:
                post.image.delete(save=False)

    def test_post_image_converted_to_webp_preserving_alpha(self):
        buffer = BytesIO()
        Image.new("RGBA", (800, 600), color=(200, 30, 30, 128)).save(
            buffer, format="PNG"
        )
        post = Post.objects.create(
            title="مقاله تستی",
            author=self.author,
            body="متن مقاله",
            published=True,
            image=SimpleUploadedFile(
                "pic.png", buffer.getvalue(), content_type="image/png"
            ),
        )
        self.assertTrue(post.image.name.endswith(".webp"))
        with post.image.open("rb") as f:
            mode = Image.open(f).mode
        # Transparency must survive the conversion.
        self.assertIn(mode, ("RGBA", "RGBX", "LA"))
