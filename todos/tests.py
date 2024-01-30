from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
        response = self.client.get(f'{self.url}?completed=true')
        self.assertEqual(list(response.context['todos']), self.todos[:1])

    def test_filter_trashed(self):
        for i in range(1, 3):
            self.todos[i].is_trashed = True
            self.todos[i].save()
        response = self.client.get(f'{self.url}?in_trash=true')
        self.assertEqual(list(response.context['todos']), self.todos[1:])

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
