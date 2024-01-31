from django.urls import path

from . import views


urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo_list'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='todo_detail'),
    path('<int:pk>/update/', views.TodoUpdateView.as_view(), name='todo_update'),
    path('create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('toggle_completion/<int:pk>/', views.TodoToggleCompletionView.as_view(), name='todo_toggle_completion'),
    path('trash/<int:pk>/', views.TodoTrashView.as_view(), name='todo_trash'),
    path('add_tag/', views.TagAddView.as_view(), name='add_tag'),
    path('remove_tag/<int:pk>/', views.TagRemoveView.as_view(), name='remove_tag'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateForm.as_view(), name='project_update'),
]
