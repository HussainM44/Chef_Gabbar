from django.urls import path
from . import views
from django.contrib.auth.models import User
from django.conf.urls.static import static
from django.conf import settings


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
    path('menu/<int:pk>/delete/', views.MenuDelete.as_view(), name = "menu_delete"),
    path('menu/<int:pk>/dish/create/', views.DishCreate.as_view(), name = "dish_create"),
    path('dish/<int:pk>/delete/', views.DishDelete.as_view(), name = "dish_delete"),
    path('dish/<int:pk>/update/', views.DishUpdate.as_view(), name = "dish_update"),

    # Order List for Manager
    path('order/list/', views.OrderList.as_view(),name = 'order_list'),
    path('order/<int:order_id>/update/', views.statusUpdate, name = 'status_update'),
    path('order/<int:order_id>/cancel/', views.orderCancellation, name = 'order_cancel'),

    # Bucket For Customer
    path('dish_bucket/add/<int:dish_id>/', views.addDish, name= 'add_dish'),
    path('bucket/<int:bucket_id>/service_type/',views.serviceType , name = 'service_type'),
    path('bucket/<int:bucket_id>/add/',views.bucketToOrder, name= "bucketToOrder"),
    path('bucket/<int:pk>/delete/', views.BucketDelete.as_view(), name='bucket_delete'),
    path('bucket/<int:bucket_id>/item/<int:item_id>/delete/', views.singleItemDelete, name = 'single_item_delete'),

    # User Moments
    path('moments/list/', views.MomentList.as_view(), name='moment_list'),
    path('moments/create/', views.MomentCreate.as_view(), name='moment_create'),
    path('moments/<int:pk>/update/', views.MomentUpdate.as_view(), name='moment_update'),
    path('moments/<int:pk>/delete/', views.MomentDelete.as_view(), name='moment_delete'),

    # PAYMENT URL
    path("checkout/<int:bucket_id>/", views.CreateCheckoutSessionView.as_view(), name = 'checkout'),
    path('success/',views.success, name ='success' ),
    path('failed/',views.failed, name ='failed' ),

]
