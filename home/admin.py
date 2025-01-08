from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import UserProfile, News
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('avatar',)  # نمایش تصویر پروفایل در فرم ویرایش

class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]  # اضافه کردن UserProfileInline
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'profile_picture_display')

    # نمایش تصویر پروفایل در قسمت لیست کاربران
    def profile_picture_display(self, obj):
        try:
            return mark_safe(f'<img src="{obj.userprofile.avatar.url}" width="50" height="50" />')
        except:
            return "بدون عکس پروفایل"
    profile_picture_display.short_description = "عکس پروفایل"
    profile_picture_display.allow_tags = True  # اجازه دادن به نمایش HTML

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_active")
    list_filter = ("is_active", "published_at")
    search_fields = ("title", "content")
    ordering = ("-published_at",)
