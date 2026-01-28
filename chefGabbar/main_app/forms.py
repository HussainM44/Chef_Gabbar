from django.forms import ModelForm
from .models import Profile , Menu , Dish , Order
from django.contrib.auth.models import User


# forms here
class profileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "role", "address"]


class userUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

class orderStatusChange(ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class serviceTypeForm(ModelForm):
    class Meta:
        model = Order
        fields = ['service_type']
