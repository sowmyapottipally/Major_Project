from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomePage, name='homepage'),
    path('login', views.UserLogin, name='login'),
    path('admin-login', views.AdminLogin, name='adminlogin'),
    path('adminhome',views.adminhome,name='adminhome'),
    path('register',views.register_user,name='register'),
    path('viewuser',views.view_user,name='viewuser'),
    path('activate/<int:id>',views.activate_user,name='activate'),
    path('block/<int:id>',views.block_user,name='block'),
]