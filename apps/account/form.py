from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.account.models import User


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
        'email', 'first_name', 'last_name', 'gender', 'phone_number', 'bio', 'website', 'reg_type', 'pr_image')


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'phone_number', 'bio', 'website', 'pr_image')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        del self.fields['password']
