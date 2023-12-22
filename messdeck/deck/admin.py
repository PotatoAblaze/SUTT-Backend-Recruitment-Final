from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import MyUser, Rating, Dish, Complaint, AttendanceRecord


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username', 'Name', 'BITS_ID', 'PSRN_No', 'Mess', 'Hostel')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('username', 'Name', 'password', 'BITS_ID', 'PSRN_No', 'Mess', 'Hostel')


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'Name', 'BITS_ID', 'PSRN_No', 'Mess', 'Hostel')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('username', 'Name', 'password', 'BITS_ID', 'PSRN_No')}),
        ('Hostel Details', {'fields': ('Mess', 'Hostel')}),
    )

    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'Name', 'password1', 'password2', 'BITS_ID', 'PSRN_No', 'Mess', 'Hostel'),
        }),
    )
    search_fields = ('BITS_ID', 'Name')
    ordering = ('BITS_ID',)
    filter_horizontal = ()

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Rating)
admin.site.register(Dish)
admin.site.register(Complaint)
admin.site.register(AttendanceRecord)
