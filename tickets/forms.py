from django import forms
from .models import Ticket, TicketComment

class TicketForm(forms.ModelForm):
    """
    Form for creating and updating tickets.
    """
    class Meta:
        model = Ticket
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class TicketStatusForm(forms.ModelForm):
    """
    Form for updating ticket status.
    """
    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class TicketCommentForm(forms.ModelForm):
    """
    Form for adding comments to tickets.
    """
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tambahkan komentar...'}),
        }
        labels = {
            'content': '',
        }
