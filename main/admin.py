from django.contrib import admin
from .models import Note, Category

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at')
    list_filter = ('author', 'category')
    search_fields = ('title', 'content', 'author__username')

admin.site.register(Note, NoteAdmin)
admin.site.register(Category)