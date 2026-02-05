from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


# Create your models here.

# Variables


SERVICES = (
    ("P","-----"),
    ("R", "Dine-in"),
    ("D", "Delivery"),
    ("T","Take Away"),
    )

STATUS = (
    ("P","In-Progress"),
    ('C','Cooking'),
    ('R', "Ready To Go"),
    ('D','Delivered'),
    ('F','Finished'),
    )

# User Auth

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/profiles", default="", blank=True)
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
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    price = models.DecimalField( max_digits=3 ,decimal_places=1)
    dish_image = models.ImageField(upload_to="uploads/dishes", default="", blank=True)

    def __str__(self):
        return f"{self.name}"

class Bucket(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    items = models.ManyToManyField(Dish)
    paid = models.BooleanField(default=False)
    service_type = models.CharField(max_length= 10 , choices= SERVICES , default='P')
    created_at = models.DateTimeField(default=timezone.now)
    def total_price(self):
        total = 0
        for items in self.items.all():
            total += items.price
        return total

    def __str__(self):
        return f"Bucket for {self.user.username}"


class Order(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS, default="P")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bucket.id}"
    # if current time is more than time created + 3 mins it is true
    def can_delete(self):
        return timezone.now() <= self.created_at + timedelta(minutes=3)


class CompletedOrder(models.Model):
    user = models.CharField(max_length=50)
    payment = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=3 ,decimal_places=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} has paid {self.total}'

class Moment(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    description = models.TextField(max_length=50 , null=True, blank=True)
    file = models.FileField(upload_to="uploads/moments", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user},s moment'


