from django.contrib import admin
from .models import MyUser,Friendship
# Register your models here.

admin.site.register(MyUser)
admin.site.register(Friendship)