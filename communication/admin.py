from django.contrib import admin
from .models import UserProfile, Note

admin.site.register(UserProfile)
admin.site.register(Note)