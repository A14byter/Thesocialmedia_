from django.contrib import admin

from .models import Post,Comment,Like,Save



class CommentInLine(admin.TabularInline):
    model = Comment
    extra = 0

class LikeInLine(admin.TabularInline):
    model = Like
    extra = 0

class PostAdmin(admin.ModelAdmin):
    list_display = ['user','head','caption','file','type','created_date']
    list_filter = ['user','type','created_date']
    search_fields = ['user','type']
    inlines=[CommentInLine,LikeInLine]

admin.site.register(Post,PostAdmin)