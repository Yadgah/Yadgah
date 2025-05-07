from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Label, Question, Reply, Slide, UserProfile


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    search_fields = ("title", "content")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


class ReplyAdmin(admin.ModelAdmin):
    list_display = ("question", "user", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = ("avatar", "score")


class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]

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

    def user_score(obj):
        try:
            return obj.userprofile.score
        except UserProfile.DoesNotExist:
            return "No Profile"

    user_score.short_description = "Score"

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        profile_picture_display,
        user_score,
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
    ordering = ("username",)


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    readonly_fields = ("order", "slug")
    search_fields = ("title", "description")
    ordering = ("order",)


class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "color_preview")
    search_fields = ("name",)
    ordering = ("name",)

    def color_preview(self, obj):
        return format_html(
            '<div style="width:30px; height:30px; background-color:{}; border-radius:50%;"></div>',
            obj.color,
        )

    color_preview.short_description = "Cor"


admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Label)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
