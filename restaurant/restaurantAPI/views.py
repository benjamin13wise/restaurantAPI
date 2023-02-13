from django.shortcuts import get_object_or_404
from rest_framework import generics ,status
from .models import  MenuItem , Cart , OrderItem , Order , Category
from .serializers import  menuItemSerializer , userSerializer , cartSerializer , orderSerializer  , orderItemsDetailsSerializer , categorySerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User,Group
from .permissions import managerGroupPermission , deliveryGroupPermission
from rest_framework.response import Response
from datetime import datetime
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle
# Create your views here.
class categoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = categorySerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            permission_classes =[managerGroupPermission]
        return [permission() for permission in permission_classes]
class menuItemsListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = menuItemSerializer
    ordering_fields = ['title','price', 'inventory','featured']
    filterset_fields = ['price', 'inventory','category']
    search_fields = ['title','category']
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            permission_classes =[managerGroupPermission]
        return [permission() for permission in permission_classes]

class menuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = menuItemSerializer
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes =[managerGroupPermission]
        return [permission() for permission in permission_classes]


class managerUsersListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset =  User.objects.filter(groups__name = 'Manager')
    serializer_class = userSerializer
    permission_classes = [managerGroupPermission]
    def post(self,request):
        name = request.data['username']
        user = get_object_or_404(User, username = name)
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response('Manager added',status =status.HTTP_201_CREATED)

class managerUserView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [managerGroupPermission]
    def delete(self,request , pk):
        try:
            manager = User.objects.get(pk=pk)
        except :
            return Response(status=status.HTTP_404_NOT_FOUND)
        myGroup = Group.objects.get(name='Manager') 
        manager.groups.remove(myGroup)
        return Response(status=status.HTTP_200_OK) 

class deliveryCrewUsersListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset =  User.objects.filter(groups__name = 'Manager')
    serializer_class = userSerializer
    permission_classes = [managerGroupPermission]
    def post(self,request):
        name = request.data['username']
        user = get_object_or_404(User, username = name)
        managers = Group.objects.get(name='Delivery crew')
        managers.user_set.add(user)
        return Response('Delivery crew added',status =status.HTTP_201_CREATED)

class deliveryCrewUserView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [managerGroupPermission]
    def delete(self,request , pk):
        try:
            deliveryCrew = User.objects.get(pk=pk)
        except :
            return Response(status=status.HTTP_404_NOT_FOUND)
        mygroup = Group.objects.get(name='Delivery crew') 
        deliveryCrew.groups.remove(mygroup)
        return Response(status=status.HTTP_200_OK)     

class cartView(generics.ListCreateAPIView,generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = cartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user = user)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if not ('menuItem' in self.request.data.keys() and 'quantity' in self.request.data.keys()):
            return Response({'message': 'menu_item and quantity are required fields'}, status=status.HTTP_400_BAD_REQUEST)
        itemId = self.request.data['menuItem']
        quantity   = int(self.request.data['quantity'])
        item    = MenuItem.objects.get(pk=itemId)

        newItem = Cart(
            user       = user,
            menuItem  = item,
            quantity   = quantity,
            unitPrice = item.price,
            price      = (item.price * quantity)
        )
        newItem.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        user   = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_200_OK)

    
class orderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = orderSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['total','date']
    filterset_fields = ['status', 'date','user','deliveryCrew']
    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_superuser:
            queryset = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            queryset = Order.objects.all().filter(deliveryCrew = self.request.user)
        else:
            queryset = Order.objects.all().filter(user = self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        user= self.request.user
        cartRecords = Cart.objects.filter(user=user)

        if not cartRecords.exists():
            return Response({'Message':'Cart empty'},status=status.HTTP_412_PRECONDITION_FAILED)

        orderSum = sum([record.price for record in cartRecords])
        newOrder = Order(
            user = user,
            total = orderSum,
            date  = datetime.now(),
        )
        newOrder.save()

        for record in cartRecords:
            newOrderItem = OrderItem(
                order = newOrder,
                menuItem  = record.menuItem,
                quantity   = record.quantity,
                unitPrice = record.unitPrice,
                price      = record.price
            )
            newOrderItem.save()
        
        cartRecords.delete()
        return Response('Order created',status=status.HTTP_201_CREATED)

class singleOrderView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Order.objects.all()
    serializer_class = orderItemsDetailsSerializer
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT','DELETE']:
            permission_classes =[managerGroupPermission]
        elif self.request.method == 'PATCH':
            permission_classes [deliveryGroupPermission]
        return [permission() for permission in permission_classes]

    def __init__(self,*args, **kwargs) :
        super(singleOrderView, self).__init__(*args, **kwargs)
        self.serializer_action_classes = {
            'list':orderSerializer,
            'create':orderSerializer,
            'retrieve': orderItemsDetailsSerializer,
            'update':orderSerializer,
            'partial_update':orderSerializer,
            'destroy':orderSerializer,
        }

    def get_serializer_class(self, *args, **kwargs):
        """Instantiate the list of serializers per action from class attribute (must be defined)."""
        kwargs['partial'] = True
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(singleOrderView, self).get_serializer_class()

    def get(self,request,*args,**kwargs):
        user = self.request.user
        orderId = self.kwargs['pk']
        orderItem = get_object_or_404(Order,pk=orderId)

        if (user.groups.filter(name='Manager').exists() 
            or user.groups.filter(name='Delivery crew').exists()
            or orderItem.user.id == user.id
            or user.is_superuser):
            return super().get(self,request,*args,**kwargs)
        else:
            return Response({'message':'Order does not belong to you'}, status=status.HTTP_403_FORBIDDEN)

    def patch(self,request,*args,**kwargs):
        user = self.request.user
        if  user.groups.filter(name='Delivery crew').exists():
            orderId = self.kwargs['pk']
            orderItem= get_object_or_404(Order,pk=orderId)
            
            if 'status' not in self.request.data:
                return Response({'message':'status field is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            newStatus = self.request.data['status']
            orderItem.status = newStatus
            
            orderItem.save()
            return Response('Status updated', status=status.HTTP_200_OK)
        else:
            return super().patch(self,request,*args,**kwargs)



