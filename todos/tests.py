from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import models

User = get_user_model()


class TodoListViewTest(TestCase):
    def setUp(self):
        self.url = reverse('todo_list')
        self.user = User.objects.create_user(email='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.todos = [models.Todo.objects.create(user=self.user, name=f'Todo {i}') for i in range(3)]

    def test_todo_list_view_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_todo_list_returns_users_todos(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['todos']), self.todos)

    def test_todo_list_does_not_return_other_users_todos(self):
        user = User.objects.create(email='testuser2@gmail.com', password='password')
        todo = models.Todo.objects.create(user=user, name='Forbidden')
        response = self.client.get(self.url)
        self.assertNotIn(todo, response.context['todos'])

    def test_filter_completed(self):
        self.todos[0].toggle_completion()
        response = self.client.get(f'{self.url}?status=completed')
        self.assertEqual(list(response.context['todos']), self.todos[:1])

    def test_filter_trashed(self):
        for i in range(1, 3):
            self.todos[i].trash()
        response = self.client.get(f'{self.url}?status=in_trash')
        self.assertEqual(list(response.context['todos']), self.todos[1:])

    def test_filter_todo(self):
        self.todos[0].toggle_completion()
        response = self.client.get(f'{self.url}?status=todo')
        self.assertEqual(list(response.context['todos']), self.todos[1:])

    def test_filter_overdue(self):
        self.todos[0].deadline = timezone.now()
        self.todos[0].save()
        response = self.client.get(f'{self.url}?status=overdue')
        self.assertEqual(list(response.context['todos']), self.todos[:1])

    def test_filter_by_tag(self):
        tag = models.Tag.objects.create(user=self.user, name='tag')
        self.todos[-1].tags.add(tag)
        response = self.client.get(f'{self.url}?tag=tag')
        self.assertEqual(list(response.context['todos']), self.todos[-1:])

    def test_htmx_request_returns_partial_template(self):
        response = self.client.get(
            f'{self.url}?completed=true',
            HTTP_HX_REQUEST='true'
        )
        self.assertTemplateUsed(response, 'todos/partials/_todo_list.html')


class TodoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser', password='testpassword')
        self.todo = models.Todo.objects.create(
            name='Test project',
            user=self.user,
        )

    def test_convert_to_project(self):
        self.todo.convert_to_project()
        self.assertEqual(models.Todo.objects.count(), 0)
        project = models.Project.objects.get(name=self.todo.name)
        self.assertEqual(project.name, self.todo.name)

    def test_toggle_completion(self):
        self.todo.toggle_completion()
        self.todo.refresh_from_db()
        self.assertIsNotNone(self.todo.completed_at)
        self.todo.toggle_completion()
        self.todo.refresh_from_db()
        self.assertIsNone(self.todo.completed_at)

    def test_is_completed(self):
        self.assertFalse(self.todo.is_completed)
        self.todo.toggle_completion()
        self.assertTrue(self.todo.is_completed)


class TodoQuerySetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser', password='testpassword')
        self.todos = [
            models.Todo.objects.create(
                user=self.user,
                name=f'Project {i}',
            ) for i in range(3)
        ]

    def test_get_all_todos(self):
        self.assertEqual(models.Todo.objects.count(), 3)

    def test_active_todos(self):
        self.todos[0].trash()
        self.assertEqual(models.Todo.objects.active().count(), 2)

    def test_todo_todos(self):
        self.todos[0].toggle_completion()
        self.assertEqual(models.Todo.objects.todo().count(), 2)

    def test_trashed_todos(self):
        self.todos[0].trash()
        self.assertEqual(models.Todo.objects.trashed().count(), 1)

    def test_completed_todos(self):
        self.todos[0].toggle_completion()
        self.assertEqual(models.Todo.objects.completed().count(), 1)

    def test_overdue_todos(self):
        self.todos[0].deadline = timezone.now()
        self.todos[0].save()
        self.assertEqual(models.Todo.objects.overdue().count(), 1)


class ProjectTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser', password='testpassword')
        self.project = models.Project.objects.create(
            name='Test project',
            user=self.user,
        )
        self.todos = [
            models.Todo.objects.create(
                user=self.user,
                project=self.project,
                name=f'Todo {i}',
            ) for i in range(3)
        ]

    def test_todo_count(self):
        project = models.Project.objects.with_todo_count().get(pk=self.project.pk)
        self.assertEqual(project.todo_count, 3)

    def test_todo_count_excludes_completed_todos(self):
        self.todos[0].toggle_completion()
        project = models.Project.objects.with_todo_count().get(pk=self.project.pk)
        self.assertEqual(project.todo_count, 2)

    def test_todo_count_excludes_trashed_todos(self):
        self.todos[0].is_trashed = True
        self.todos[0].save()
        project = models.Project.objects.with_todo_count().get(pk=self.project.pk)
        self.assertEqual(project.todo_count, 2)

    def test_has_todos_remaining(self):
        self.assertTrue(self.project.has_todos_remaining())
        self.project.todo_set.update(completed_at=timezone.now())
        self.assertFalse(self.project.has_todos_remaining())

    def test_trash(self):
        self.project.trash()
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_trashed)
        self.assertEqual(self.project.todo_set.active().count(), 0)
        self.assertEqual(self.project.todo_set.trashed().count(), 3)
