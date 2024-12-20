# type: ignore
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/',views.logout_view, name='logout'),
    path('password-reset/',views.password_reset_view, name='password-reset'),
    path('password-reset/<uuid:uuid>/',views.verify_reset_view, name='verify-reset'),
    path('map/', views.home, name="map-home"),

]
