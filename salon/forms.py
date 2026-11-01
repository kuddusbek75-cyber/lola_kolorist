import re
from datetime import date, time

from django import forms

from .models import Booking

TIME_RE = re.compile(r'^(\d{1,2})(?:[:.\-\s]?(\d{2}))?$')


class BookingForm(forms.ModelForm):
    time = forms.CharField(label='Время', max_length=5)

    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'phone', 'wish', 'date', 'time']
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'placeholder': '+996 ___ ___ ___',
                                            'autocomplete': 'tel'}),
            'wish': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите, что вы хотите сделать'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {'wish': 'Что вы хотите сделать?'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['time'].widget.attrs.update({
            'placeholder': 'например, 14:30', 'inputmode': 'numeric',
            'maxlength': '5', 'autocomplete': 'off', 'data-time-mask': '1',
        })

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if len(re.sub(r'\D', '', phone)) < 9:
            raise forms.ValidationError('Введите номер телефона полностью.')
        return phone

    def clean_wish(self):
        wish = self.cleaned_data['wish'].strip()
        if len(wish) < 3:
            raise forms.ValidationError('Напишите, что вы хотите сделать.')
        return wish

    def clean_date(self):
        d = self.cleaned_data['date']
        if d < date.today():
            raise forms.ValidationError('Выберите сегодняшнюю или будущую дату.')
        return d

    def clean_time(self):
        m = TIME_RE.match(self.cleaned_data['time'].strip())
        hour, minute = (int(m.group(1)), int(m.group(2) or 0)) if m else (99, 99)
        if hour > 23 or minute > 59:
            raise forms.ValidationError('Введите время в формате 14:30.')
        return time(hour, minute)
