from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import News, UserProfile


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


# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the News model.
    """

    list_display = ("title", "author", "published_at", "is_active")
    list_filter = ("is_active", "published_at")
    search_fields = ("title", "content")
    ordering = ("-published_at",)
