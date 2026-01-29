from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from django.contrib.auth.models import User
from .models import Profile, Menu, Dish, Order
from django.http import JsonResponse
# to log in new user and create a auth session
from django.contrib.auth import login

# to update the auth session of the same user
from django.contrib.auth import update_session_auth_hash
from .forms import profileForm, userUpdateForm, orderStatusChange , serviceTypeForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse


# Create your views here.


# BASIC Views


def home(request):
    return render(request, "home.html")


#  User Auth
# creating the profile and sign up in same def


def signup(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        # importing form from forms.py & req.FILES for image uploading
        profile_form = profileForm(request.POST, request.FILES)
        # checking the form is valid or not
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # saving profile with user and profile model
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # logging in the same user that signed up
            login(request, user)
            return redirect("/")
        else:
            error_message = "Invalid sign up - try again"
    else:
        user_form = UserCreationForm()
        profile_form = profileForm()
        error_message = None
        # sending forms and error messages to the template
    return render(
        request,
        "registration/signup.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "error_message": error_message,
        },
    )


# User Profile views


class UserDetail(DetailView):
    model = User


def userUpdate(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user_id=user_id)

    if request.method == "POST":
        user_form = userUpdateForm(request.POST, instance=user)
        profile_form = profileForm(request.POST, request.FILES, instance=profile)
        # passwordChangeForm requires user and request instead of instance
        password_form = PasswordChangeForm(user, request.POST)
        if (
            user_form.is_valid()
            and profile_form.is_valid()
            and password_form.is_valid()
        ):
            user_form.save()
            profile_form.save()
            password_form.save()
            # to update the session for the same user and keep user logged in
            update_session_auth_hash(request, user)
            # login(request, user)
            return redirect("/")
        else:
            error_message = "Invalid info- TRY AGAIN"
    else:
        user_form = userUpdateForm(instance=user)
        profile_form = profileForm(instance=profile)
        password_form = PasswordChangeForm(user)

        error_message = None
    return render(
        request,
        "registration/userUpdate.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "password_form": password_form,
            "error_message": error_message,
        },
    )


# Menu Views


class MenuList(ListView):
    model = Menu


class MenuCreate(CreateView):
    model = Menu
    fields = ["cuisine"]
    success_url = "/menu/<int:pk>/dish/create/"

    # this is adding user in menu manually that is logged in
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # success_url will only directs to static urls (it does not transfer id)
    # get_success_url transfers the id to that url
    # return reverse('url_name(where id is needed)', kwarg = {"user_id or pk(whatever called in url)":self.object.pk(calling the id of the self)})
    def get_success_url(self):
        return reverse("dish_create", kwargs={"pk": self.object.pk})


class MenuDelete(DeleteView):
    model = Menu
    success_url = "/menu/list/"


class DishCreate(CreateView):
    model = Dish
    fields = ["name",'price', "description", "dish_image"]
    success_url = "/menu/list/"

    def form_valid(self, form):
        # this automatically receives the id from the get_success_url
        menu = Menu.objects.get(pk=self.kwargs["pk"])
        form.instance.menu = menu
        return super().form_valid(form)


class DishDelete(DeleteView):
    model = Dish
    success_url = "/menu/list/"


class DishUpdate(UpdateView):
    model = Dish
    fields = ["name", "price", "description", "dish_image"]
    success_url = "/menu/list/"


# Order for Manager


class OrderList(ListView):
    model = Order
    ordering = ["-created_at"]
    # to send the data of other model to the the cbv
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #form for manager to change status
        context["form"] = orderStatusChange()
        # form for user to add service needed
        context['service_form'] = serviceTypeForm()
        return context


def statusUpdate(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        form = orderStatusChange(request.POST, instance=order)
        if form.is_valid():
            form.save()

            return redirect("order_list")
        else:
            orderStatusChange(instance=order)
            serviceTypeForm(instance=order)

    return redirect("order_list")


def addDish(request , dish_id):
    dish = Dish.objects.get(id=dish_id)

    order = Order.objects.filter(user = request.user ).first()


    if not order:
        order = Order.objects.create(user = request.user)

    order.item.add(dish)
    return redirect('/menu/list/')

def serviceType(request , order_id):
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        service_form = serviceTypeForm(request.POST , instance=order)
        if service_form.is_valid():
            service_form.save()
        else:
            serviceTypeForm(instance=order)

    return redirect("order_list")


