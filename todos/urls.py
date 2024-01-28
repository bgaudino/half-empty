from django.urls import path

from . import views


urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo_list'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='todo_detail'),
    path('create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('toggle_completion/<int:pk>/', views.TodoToggleCompletionView.as_view(), name='todo_toggle_completion'),
    path('trash/<int:pk>/', views.TodoTrashView.as_view(), name='todo_trash'),
]
