from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from django.forms import ModelForm
from .models import Expense


class ExpenseForm(ModelForm):

    class Meta:

        model = Expense

        fields = [
            'description',
            'amount',
            'category',
            'date',
            'notes'
        ]