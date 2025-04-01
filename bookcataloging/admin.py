from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, BookReview, UserProfile, Collections, Request

class CollectionsAdmin(admin.ModelAdmin):
    filter_horizontal = ('books',) 

admin.site.register(Book)
admin.site.register(BookReview)
admin.site.register(UserProfile)
admin.site.register(Collections, CollectionsAdmin)
admin.site.register(Request)

