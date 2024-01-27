from django.urls import path

from . import views


urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo_list'),
    path('create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('toggle_completion/<int:pk>/', views.TodoToggleCompletionView.as_view(), name='todo_toggle_completion'),
]
