from django import forms
from .models import *

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["category", "priority", "subject", "description", "tags", "max_reply_date", "age", "email"]

        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter subject"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Describe your issue..."}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "max_reply_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "age": forms.IntegerField(required=True),
            "email": forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }