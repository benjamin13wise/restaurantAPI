from django.urls import path 
from .views import menuItemsListView , menuItemView , managerUsersListView , managerUserView   , cartView , orderView , singleOrderView , deliveryCrewUserView , deliveryCrewUsersListView , categoryListView


urlpatterns = [
    path('categories',categoryListView.as_view()),
    path('menu-items',menuItemsListView.as_view()),
    path('menu-items/<int:pk>',menuItemView.as_view()),
    path('groups/manager/users',managerUsersListView.as_view()),
    path('groups/manager/users/<int:pk>',managerUserView.as_view()),
    path('groups/delivery-crew/users',deliveryCrewUsersListView.as_view()),
    path('groups/manager/users/<int:pk>',deliveryCrewUserView.as_view()),
    path('cart/menu-items',cartView.as_view()),
    path('orders',orderView.as_view()),
    path('orders/<int:pk>',singleOrderView.as_view()),

]

