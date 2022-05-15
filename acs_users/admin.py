from django.contrib import admin
from .models import AuthUser

from django.contrib import admin
from django.contrib.auth import admin as upstream
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, User
from django.contrib.admin.sites import NotRegistered
 
class UserAdmin(upstream.UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'phone_number', 'client_id')}
         ),
    )
    form = UserChangeForm
    add_form = UserCreationForm


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(AuthUser, UserAdmin)


 