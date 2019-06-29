from django.urls import include, path
from django.contrib import admin
from app import views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/social/login/cancelled/', views.results_list, name='results_list'),
    path('accounts/', include('allauth.urls')),
    path('', include('app.urls')),
    path('', include('Score_evaluator.urls'))

]
