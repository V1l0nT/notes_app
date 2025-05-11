from django.forms import ModelForm, TextInput, Textarea, Select
from .models import Note, Category
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ('username', 'email')
 
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают")

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["title", "category", "content"]
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название',
            }),
            "category": Select(attrs={
                'class': 'form-control',
            }),
            "content": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Содержание',
                'rows': 5,
            }),
        }
        
class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории',
            }),
            'description': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание категории',
                'rows': 3,
            }),
        }