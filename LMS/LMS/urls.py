"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from rsLib.views import index, book_details, about, collection, event, search_books, signup, login, logout, dashboard, issue_request, confirm_request, issued_books, issue_requests, delete_request, returned_book, show_users, adminSignup, adminLogin, show_Adminusers, adminLogout, recent_orders

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('home/', index, name='home'),
    path('books/<path:title>/<path:volume_id>/', book_details, name='book_details'),
    # path('books/<str:volume_id>/', book_details, name='book_details'),
    path('about/', about, name='about'),
    path('collection/', collection, name='collection'),
    path('event/', event, name='event'),
    path('books/', search_books, name='search_books'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('admin_dashboard/', dashboard, name='dashboard'),
    
    # path('issue_request/', issue_request, name='issue_request'),
    # path('issue_request_confirmation/<str:title>/<str:volume_id>/',
    #      issue_request_confirmation, name='issue_request_confirmation'),

    # path('confirm_request/<int:request_id>/',
    #      confirm_request, name='confirm_request'),
    
    # path('issued_books/', issued_books, name='issued_books')
    
    path('issue_request/', issue_request, name='issue_request'),
    path('admin_dashboard/issue_requests/', issue_requests, name='admin_dashboard/issue_requests/'),
    path('confirm_request/<int:request_id>/', confirm_request, name='confirm_request'),
    path('admin_dashboard/issued_books/', issued_books,
         name='admin_dashboard/issued_books/'),
    path('delete_request/<int:request_id>/', delete_request, name='delete_request'),
    path('returned_book/<int:request_id>/',
         returned_book, name='returned_book'),
    path('admin_dashboard/registered_user/', show_users,
         name='admin_dashboard/registered_user/'),
    path('admin_dashboard/admin_members/', show_Adminusers,
         name='admin_dashboard/admin_members/'),
    path('admin_signup/', adminSignup, name='admin_signup'),
    path('admin_login/', adminLogin, name='admin_login'),
    
    path('admin_dashboard/admin_logout/', adminLogout,
         name='admin_dashboard/admin_logout/'),

    path('recent_orders/', recent_orders, name='recent_orders'),

]

