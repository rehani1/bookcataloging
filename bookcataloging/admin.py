from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, BookReview, UserProfile

admin.site.register(Book)
admin.site.register(BookReview)
admin.site.register(UserProfile)