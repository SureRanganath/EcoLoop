from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendations_view, name='recommendations'),
    path('suggest-category/', views.suggest_category_view, name='suggest_category'),
]
