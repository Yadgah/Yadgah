from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Label, News, Question, Reply, UserProfile


# Register the Question model for the admin
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "created_at",
    )  # Columns to display in the list view
    search_fields = ("title", "content")  # Enable search by title and content
    list_filter = ("created_at",)  # Filter by creation date
    ordering = ("-created_at",)  # Order by creation date in descending order


# Register the Reply model for the admin
class ReplyAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "user",
        "created_at",
    )  # Columns to display in the list view
    search_fields = ("content",)  # Enable search by content
    list_filter = ("created_at",)  # Filter by creation date
    ordering = ("-created_at",)  # Order by creation date in descending order


# Function to display profile picture in the admin
def profile_picture_display(obj):
    try:
        if obj.userprofile.avatar:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;border-radius:50%;" />',
                obj.userprofile.avatar.url,
            )
    except UserProfile.DoesNotExist:
        return "No Profile"
    return "No Avatar"


profile_picture_display.short_description = "Profile Picture"


# Inline model for UserProfile, allowing profile editing directly from the User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = ("avatar",)  # Display avatar field in the user edit form


# Custom admin for the User model, including the UserProfile inline
class UserAdmin(admin.ModelAdmin):
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


# Admin configuration for the News model
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_active")
    list_filter = ("is_active", "published_at")
    search_fields = ("title", "content")
    ordering = ("-published_at",)


# Register the models in the admin panel
admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(UserProfile)  # No need for UserProfileAdmin, as it's already handled in UserAdmin
# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Label)

