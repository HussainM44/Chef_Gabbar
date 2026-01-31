from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Create your models here.

# Variables


SERVICES = (
    ("R", "Dine-in"),
    ("D", "Delivery"),
    ("T","Take Away"),
    )

STATUS = (
    ("P","In-Progress"),
    ('C','Cooking'),
    ('R', "Ready To Go"),
    ('D','Delivered'),
    )

# User Auth

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    image = models.ImageField(upload_to="main_app/static/uploads", default="")
    address = models.CharField(max_length=50 )

    def __str__(self):
        return f'{self.user}'




class Menu(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    cuisine = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.cuisine}"

class Dish(models.Model):
    menu = models.ForeignKey(Menu , on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=100)
    price = models.DecimalField( max_digits=3 ,decimal_places=1)
    dish_image = models.ImageField(upload_to="main_app/static/uploads", default= "")

    def __str__(self):
        return f"{self.name}"

class Bucket(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    items = models.ManyToManyField(Dish)
    service_type = models.CharField(max_length= 10 , choices= SERVICES , default='Dine-in')
    def total_price(self):
        total = 0
        for items in self.items.all():
            total += items.price
        return total

    def __str__(self):
        for items in self.items.all():
            return f"{self.items}"


class Order(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    status = models.CharField(max_length=10 , choices=STATUS , default="Waiting")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s {self.order_id}"


class Moment(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    description = models.TextField(max_length=50 , null=True, blank=True)
    file = models.FileField(upload_to="main_app/static/uploads", blank=True, null=True)

    def __str__(self):
        return f'{self.user},s moment'
