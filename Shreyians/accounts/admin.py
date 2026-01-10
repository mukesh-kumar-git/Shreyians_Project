from django.contrib import admin
from django.utils.html import format_html
from .models import Course, CourseTag



class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','price_discounted','price_original','discount_percentage','is_live','image_preview','created_at',)

    search_fields = ('title', 'short_description')
    list_filter = ('is_live', 'created_at', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover;" />',obj.image.url)
        return "No Image"

    image_preview.short_description = "Preview"
admin.site.register(Course,CourseAdmin)

class CourseTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(CourseTag,CourseTagAdmin)