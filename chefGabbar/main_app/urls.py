from django.urls import path
from . import views
from django.contrib.auth.models import User

urlpatterns = [
    path('',views.home, name='home'),

    # User Auth
    path("accounts/signup/",views.signup , name='signup'),

    # User Profile
    path('profile/<int:pk>/', views.UserDetail.as_view(), name = "profile"),
    path('profile/<int:user_id>/update/', views.userUpdate, name = "user_update"),

    # Menu List
    path('menu/list/',views.MenuList.as_view(), name = 'menu_list'),

    # Menu Creation for Managers
    path('menu/create/', views.MenuCreate.as_view(), name = "menu_create"),
    path('menu/<int:pk>/dish/create/', views.DishCreate.as_view(), name = "dish_create"),
    path('dish/<int:pk>/delete/', views.DishDelete.as_view(), name = "dish_delete"),

]
