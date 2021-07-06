from django.contrib import admin
from .models import User_Info, Reports, Friends

# Register your models here.
admin.site.register(User_Info)
admin.site.register(Reports)
admin.site.register(Friends)
