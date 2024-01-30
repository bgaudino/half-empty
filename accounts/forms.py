from django.contrib.auth import get_user_model
from authtools.forms import UserCreationForm


User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
