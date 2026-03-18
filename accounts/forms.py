from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import User


ROLE_CHOICES = [
    ('ROOT_DEV', 'Root Developer'),
    ('DEV', 'Developer'),
    ('ADMIN', 'Admin'),
    ('USER', 'User'),
]


class RootCreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    mobile_number = forms.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'role',
            'first_name',
            'last_name',
            'mobile_number',
            'email',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        # assign extra fields
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        user.mobile_number = self.cleaned_data['mobile_number']

        if commit:
            user.save()
            role = self.cleaned_data['role']
            # Optional: add to group if needed
            try:
                group = Group.objects.get(name=role)
                user.groups.clear()
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        return user
