from django import forms
from .models import WeeklyProgram, DailyEntry

class ProgramForm(forms.ModelForm):
    class Meta:
        model = WeeklyProgram
        fields = ['week_start', 'room', 'movie']
        widgets = {
            'week_start': forms.DateInput(attrs={'type': 'date'}),
        }

class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['date', 'room', 'entrances']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }