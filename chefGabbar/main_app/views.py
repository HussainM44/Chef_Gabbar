from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from django.contrib.auth.models import User
from .models import Profile, Menu, Dish, Order, Moment, Bucket, CompletedOrder
from django.http import JsonResponse

# to log in new user and create a auth session
from django.contrib.auth import login

# to update the auth session of the same user
from django.contrib.auth import update_session_auth_hash
from .forms import (
    profileForm,
    userUpdateForm,
    orderStatusChange,
    serviceTypeForm,
    CompleteOrderForm,
)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.views import View
import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.

# succeeds          4242 4242 4242 4242
# authentication    4000 0025 0000 3155
# declined          4000 0000 0000 9995

# same as csrf token
@method_decorator(csrf_exempt, name="dispatch")
class CreateCheckoutSessionView(View):

    def post(self, request, bucket_id):

        bucket = Bucket.objects.get(id=bucket_id)

        domain = "http://127.0.0.1:8000/"

        success_url = f"{domain}success/?bucket_id={bucket.id}"
        cancel_url = f"{domain}cancel/"
        # for checkout session from stripe api
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(bucket.total_price() * 100),
                        "product_data": {
                            "name": f"Order #{bucket.id} dated {bucket.created_at}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return redirect(checkout_session.url)


def success(request):
    bucket_id = request.GET.get("bucket_id")
    if bucket_id:
        bucket = Bucket.objects.get(id=bucket_id)
        bucket.paid = True
        bucket.save()
        Order.objects.get_or_create(bucket=bucket)
    return redirect("/order/list/")


def failed(request):
    return HttpResponse("Payment Failed ")


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["moments"] = Moment.objects.filter(user=self.object)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query
        query = self.request.GET.get("q", "")
        if query:
            dishes = Dish.objects.filter(name__icontains=query)
        else:
            dishes = Dish.objects.none()
        context["search_results"] = dishes
        context["search_query"] = query

        # Buckets for the user
        if self.request.user.is_authenticated:
            context["buckets"] = Bucket.objects.filter(user=self.request.user)
            context["bucket_added"] = Order.objects.filter(
                bucket__in=context["buckets"]
            ).values_list("bucket_id", flat=True)
        else:
            context["buckets"] = None
            context["bucket_added"] = []

        context["form"] = serviceTypeForm()
        return context


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
    fields = ["name", "price", "description", "dish_image"]
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
        completed_order = CompletedOrder.objects.all()
        context = super().get_context_data(**kwargs)
        context["form"] = orderStatusChange()
        context["completed_order"] = completed_order
        return context


def statusUpdate(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        form = orderStatusChange(request.POST, instance=order)
        if form.is_valid():
            form.save()
            if order.status == "F":
                bucket = order.bucket
                user = str(bucket.user.username)
                payment = str(bucket.paid)
                total = float(bucket.total_price())
                completedOrder = CompletedOrder.objects.create(
                user = user,
                total = total,
                payment= payment,
                )

                order.delete()
                bucket.delete()



            return redirect("order_list")
        else:
            orderStatusChange(instance=order)
    return redirect("order_list")


def bucketToOrder(request, bucket_id):
    bucket = Bucket.objects.get(id=bucket_id)

    order = Order.objects.filter(bucket=bucket).first()
    if not order:
        order = Order.objects.create(bucket=bucket)

    return redirect("/order/list/")


# Bucket for Customer


def addDish(request, dish_id):

    dish = Dish.objects.get(id=dish_id)

    bucket = Bucket.objects.filter(user=request.user).first()

    if not bucket:
        bucket = Bucket.objects.create(user=request.user)

    if Order.objects.filter(bucket=bucket).exists():
        return redirect("/menu/list/")

    bucket.items.add(dish)

    return redirect("/menu/list/")


def serviceType(request, bucket_id):
    bucket = Bucket.objects.get(id=bucket_id)

    if request.method == "POST":
        form = serviceTypeForm(request.POST, instance=bucket)
        if form.is_valid():
            form.save()
            return redirect("/menu/list/")
    else:
        form = serviceTypeForm(instance=bucket)

    return redirect("/menu/list/")


class BucketDelete(DeleteView):
    model = Bucket
    success_url = "/menu/list/"

    def get_bucket(self):
        return Bucket.objects.filter(user=self.request.user)


# Moment Views


class MomentList(ListView):
    model = Moment
    ordering = ["-created_at"]


class MomentCreate(CreateView):
    model = Moment
    fields = ["file", "description"]
    success_url = "/moments/list/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MomentUpdate(UpdateView):
    model = Moment
    fields = ["description"]
    success_url = "/moments/list/"


class MomentDelete(DeleteView):
    model = Moment
    success_url = "/moments/list/"


# PAYMENTS
