from django.urls import path, include
from django.contrib.auth.views import LogoutView

from . import views

app_name = "bookcataloging"
urlpatterns = [
    path("", views.index_view, name="index"),
    path('logout', LogoutView.as_view()),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search_view, name='search'),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path('home/', views.home_view, name='home'),
    path("collections/", views.collections_view, name="collections"),
    path("collections/add/", views.add_collection, name='add_collection'),
    path('collections/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('collections/<int:collection_id>/view/', views.view_collection, name='view_collection'),
]