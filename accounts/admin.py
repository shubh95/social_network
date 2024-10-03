from django.contrib import admin

from .models import CustomUser, BlockedUser

admin.site.register(CustomUser)
admin.site.register(BlockedUser)
