from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

# Variables

ROLE = (
    ("C","Customer"),
    ('M','Manager'),
    )
SERVICES = (
    ("R", "Dine-in"),
    ("D", "Delivery"),
    ("T","Take Away"),
    )

STATUS = (
    ('C','Cooking'),
    ('R', "Ready To Go"),
    ('D','Delivered'),
    ('F','Finished'),
    )

# User Auth

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    image = models.ImageField(upload_to="main_app/static/uploads", default="")
    role = models.CharField(max_length=2, choices=ROLE , default=[0][0])
    address = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.user} is a {self.role}'




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


class Order(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    item = models.ManyToManyField(Dish)
    service_type = models.CharField(max_length= 1 , choices= SERVICES , default=[0][0] )
    status = models.CharField(max_length=1 , choices=STATUS , default=[0][0])
    def total_price(self):
        total = 0
        for dish in self.item.all():
            total += dish.price
        return total

    def __str__(self):
        for dish in self.item.all():
            items = dish.name
        return f"{self.user.username} ordered: {items}"



