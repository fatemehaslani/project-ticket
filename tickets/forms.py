import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import *

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class TicketForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=MultiFileInput(attrs={
            "multiple": True,
            "class": "form-control"
        }),
        required=False,
        help_text="You can upload multiple files (PDF, Word, Images).")



    class Meta:
        model = Ticket
        fields = ["category", "priority", "subject", "description", "tags", "max_reply_date"]

        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter subject"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Describe your issue..."}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "max_reply_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
           # "age": forms.IntegerField(required=True),
           # "email": forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({
                'class': 'form-control'
            })

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        count = tags.count() if tags else 0

        if count < 1:
            raise forms.ValidationError("Please select at least one tag.")
        if count > 5:
            raise forms.ValidationError("You can select a maximum of 5 tags.")

        return tags

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png'
        ]
        for f in files:
            if f.content_type not in allowed_types:
                raise forms.ValidationError(f"{f.name} has an unsupported file type.")
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError(f"{f.name} exceeds 5 MB size limit.")
        return files


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a '}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Email '})
        }
        labels = {
            'username': 'Username',
            'email': 'Email address',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. ")
        return username


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) == 0:
            raise ValidationError("Email address is required.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. ")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password do not match.")

        if password1 and len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if password1 and not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one number.")

        if password1 and not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase.")

        if password1 and not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase uppercase.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user