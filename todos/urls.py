from django.urls import path

from . import views


urlpatterns = [
    path('todos/', views.TodoListView.as_view(), name='todo_list'),
    path('todos/<int:pk>/', views.TodoDetailView.as_view(), name='todo_detail'),
    path('todos/<int:pk>/update/', views.TodoUpdateView.as_view(), name='todo_update'),
    path('todos/create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('todos/<int:pk>/toggle_completion/', views.TodoToggleCompletionView.as_view(), name='todo_toggle_completion'),
    path('todos/trash/<int:pk>/', views.TodoTrashView.as_view(), name='todo_trash'),
    path('todos/add_tag/', views.TagAddView.as_view(), name='add_tag'),
    path('todos/remove_tag/<int:pk>/', views.TagRemoveView.as_view(), name='remove_tag'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateForm.as_view(), name='project_update'),
    path('projects/<int:pk>/trash/', views.ProjectTrashView.as_view(), name='project_trash'),
    path('projects/<int:pk>/toggle_completion/', views.ProjectToggleCompletionView.as_view(), name='project_toggle_completion'),
]
