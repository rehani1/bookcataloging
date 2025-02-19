from django.urls import path

from . import views

app_name = "bookcataloging"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("book_recs/", views.book_recs, name="book_recs"),
]