from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')  # Fields to display in the list view
    list_filter = ('author', 'created_at', 'updated_at')  # Filters for the right sidebar
    search_fields = ('title', 'content')  # Fields to search by
    readonly_fields = ('created_at', 'updated_at')  # Make these fields read-only in the admin

    # Customize the form for adding/editing blog posts
    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'is_published', 'content', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapse this section by default
        }),
    )