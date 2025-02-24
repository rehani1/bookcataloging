from django.urls import path, include
from django.contrib.auth.views import LogoutView

from . import views

app_name = "bookcataloging"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("book_recs/", views.book_recs, name="book_recs"),
    path('logout', LogoutView.as_view()),
    path('profile/', views.profile_view, name='profile'),
]