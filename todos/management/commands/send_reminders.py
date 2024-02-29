from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone

from todos.models import Todo


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
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
                html_message=f'''View it <a href="{settings.SITE_URL}{todo.get_absolute_url()}">here</a>'''
            )
