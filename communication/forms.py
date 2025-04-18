from django import forms
from .models import Note, SECTION_CHOICES, STATUS_CHOICES

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['to_section', 'subject', 'description']
        widgets = {
            'to_section': forms.Select(choices=SECTION_CHOICES),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class StatusUpdateForm(forms.ModelForm):
    receiver_comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label='Comments'
    )

    class Meta:
        model = Note
        fields = ['status', 'receiver_comments']
        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES, attrs={'class': 'form-control'}),
        }

class ForwardNoteForm(forms.Form):
    to_section = forms.ChoiceField(
        choices=SECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Forward to Section'
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label='Forwarding Comments'
    )