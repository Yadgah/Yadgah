from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import News, UserProfile

from django.utils.html import format_html

from django.contrib import admin
from .models import Question, Reply, News, UserProfile

# مدل Question را برای ادمین ثبت می‌کنیم
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')  # ستون‌هایی که در صفحه لیست نمایش داده شوند
    search_fields = ('title', 'content')  # قابلیت جستجو بر اساس عنوان و محتوا
    list_filter = ('created_at',)  # فیلتر بر اساس تاریخ ایجاد
    ordering = ('-created_at',)  # ترتیب نمایش سوالات بر اساس تاریخ ایجاد به صورت نزولی

# مدل Reply را برای ادمین ثبت می‌کنیم
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created_at')  # ستون‌هایی که در صفحه لیست نمایش داده شوند
    search_fields = ('content',)  # جستجو بر اساس محتوا
    list_filter = ('created_at',)  # فیلتر بر اساس تاریخ ایجاد
    ordering = ('-created_at',)  # ترتیب نمایش پاسخ‌ها بر اساس تاریخ ایجاد

# مدل UserProfile را برای ادمین ثبت می‌کنیم
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')  # نمایش کاربر و آواتار در پنل ادمین



def profile_picture_display(obj):
    try:
        if obj.userprofile.avatar:
            return format_html('<img src="{}" style="height:50px;width:50px;" />', obj.userprofile.avatar.url)
    except UserProfile.DoesNotExist:
        return "No Profile"
    return "No Avatar"

profile_picture_display.short_description = "Profile Picture"



class UserProfileInline(admin.StackedInline):
    """
    Inline model for UserProfile, allowing profile editing directly from the User admin.
    """

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = ("avatar",)  # Display avatar field in the user edit form


class UserAdmin(admin.ModelAdmin):
    """
    Custom admin for the User model, including the UserProfile inline.
    """

    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "profile_picture_display",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
    ordering = ("username",)

    def profile_picture_display(self, obj):
        """
        Display the user's profile picture in the admin list view.
        """
        try:
            if obj.userprofile.avatar:
                return mark_safe(
                    f'<img src="{obj.userprofile.avatar.url}" width="50" height="50" style="border-radius:50%;" />'
                )
        except UserProfile.DoesNotExist:
            pass
        return "No Profile Picture"

    profile_picture_display.short_description = "Profile Picture"





@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the News model.
    """

    list_display = ("title", "author", "published_at", "is_active")
    list_filter = ("is_active", "published_at")
    search_fields = ("title", "content")
    ordering = ("-published_at",)


# ثبت مدل‌ها در پنل ادمین
admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)