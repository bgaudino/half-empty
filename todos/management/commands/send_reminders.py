from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.utils.html import escape

from todos.models import Todo


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        User = get_user_model()
        should_remind = Exists(
            Todo.objects.todo().filter(
                user=OuterRef('pk'),
                deadline__lte=tomorrow
            )
        )
        users = User.objects.annotate(
            should_remind=should_remind
        ).filter(
            settings__receive_email_reminders=True,
            should_remind=True,
        ).prefetch_related('todo_set')
        for user in users:
            todos = user.todo_set.todo().filter(deadline__lte=tomorrow)
            upcoming = todos.filter(deadline__gt=now)
            overdue = todos.filter(deadline__lte=now)
            subject = 'You have '
            html = self.get_html(overdue) + self.get_html(upcoming)
            if upcoming and overdue:
                subject += 'upcoming and overdue todos'
            else:
                subject += 'upcoming todos'
        todos = Todo.objects.todo().filter(
            deadline__lte=tomorrow,
            user__settings__receive_email_reminders=True
        )
        for todo in todos:
            subject = f'Your todo is {"past due" if todo.deadline < now else "due soon"}'
            send_mail(
                subject,
                subject,
                settings.CONTACT_EMAIL,
                (todo.user.email,),
                html_message=html,
            )

    def get_html(self, todos, overdue=True):
        if not todos:
            return ''
        html = f'<h2>{"Overdue" if overdue else "Upcoming"} todos</h2><ul>'
        for todo in todos:
            html += f'<li><a href="{settings.SITE_URL}{todo.get_absolute_url()}">{escape(todo.name)}</a></li>'
        html += '</ul>'
        return html
