from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views


urlpatterns = [
    path('', views.results_list, name='results_list'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    path('signup/', views.signup, name='signup'),
]
