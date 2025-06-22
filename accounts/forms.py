from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError

class CustomUserForm(forms.ModelForm):
    # Make password optional for editing
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        min_length=8,
        help_text="Leave blank to keep current password. Password must be at least 8 characters long."
    )
    
    status = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'dob', 'phone_number', 'email', 'role', 'status']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial status from instance if it exists
        if self.instance and self.instance.pk:
            self.fields['status'].initial = self.instance.status

    def save(self, commit=True):
        user = super().save(commit=False)
        # Only update password if a new one was provided
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user