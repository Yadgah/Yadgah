from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Post

@receiver(pre_save, sender=Post)
def delete_old_post_image_on_update(sender, instance, **kwargs):
    # اگر این یک نمونه جدید باشد، کاری انجام نده
    if not instance.pk:
        return

    try:
        old_instance = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    # اگر تصویر قبلی وجود دارد و با تصویر جدید متفاوت است، آن را حذف کن
    if old_instance.image and old_instance.image != instance.image:
        old_instance.image.delete(save=False)
