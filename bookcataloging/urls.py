from django.urls import path, include
from django.contrib.auth.views import LogoutView

from . import views

app_name = "bookcataloging"
urlpatterns = [
    path("", views.index_view, name="index"),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search_view, name='search'),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path('home/', views.home_view, name='home'),
    path("collections/", views.collections_view, name="collections"),
    path("collections/add/", views.add_collection, name='add_collection'),
    path('collections/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('collections/<int:collection_id>/view/', views.view_collection, name='view_collection'),
    path('collections/<int:collection_id>/add_book_to_collection/', views.add_book_to_collection, name='add_book_to_collection'),
    path('collections/<int:collection_id>/view_users/', views.view_users, name='view_users'),
    path('collections/<int:collection_id>/delete_book_from_collection/<int:book_id>/', views.delete_book_from_collection, name='delete_book_from_collection'),
    path('collections/request/<int:collection_id>/', views.request_collection, name='request_collection'),  # Request access to collection
    path('requests/view/', views.view_requests, name='view_requests'),  # View all requests
    path('requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),  # Approve a request
    path('requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),  # Deny a request
    path('books/check_out/<int:book_id>/', views.check_out_book, name='check_out_book'),
    path('books/return/<int:book_id>/', views.return_book, name='return_book'),
    path('checked_out/', views.checked_out_books, name='checked_out_books'),
    path('add_book/', views.add_book, name="add_book" ),
    path('search/<int:book_id>/edit_book/', views.edit_book, name='edit_book'),
    path('search/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('profile/view_patrons/', views.view_patrons, name="view_patrons"),
    path('profile/view_patrons/<int:patron_id>/upgrade/', views.upgrade_patrons, name="upgrade_patrons"),
    path('collections/<int:collection_id>/view/search/', views.search_collection, name='search_collection'), 
    path('books/<int:book_id>/rate/', views.add_book_rating, name='add_book_rating'),

]