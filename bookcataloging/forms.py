from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'description',
            'quote',
            'books_read',
            'pages_read',
            'friends',
        ]