from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile , Menu , Dish , Order, Moment, Bucket, Comment

# Register your models here.
admin.site.register(Profile)
admin.site.register(Menu)
admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(Moment)
admin.site.register(Bucket)
admin.site.register(Comment)
