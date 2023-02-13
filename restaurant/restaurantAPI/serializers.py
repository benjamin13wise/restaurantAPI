from rest_framework import serializers
from .models import Category, MenuItem , Cart , Order , OrderItem
from django.contrib.auth.models import User

class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class menuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = categorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','category','price','featured','category_id']

class userSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = ['id','username','email']

class cartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
)

    class Meta :
        model = Cart
        fields = ['user','menuItem','quantity','unitPrice','price','id']
    
        extra_kwargs= {
            'quantity':{'min_value':1},
            'unitPrice':{'read_only':True},
            'price':{'read_only':True}
        }
        

class orderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
)
    class Meta:
        model = Order
        fields = ['id','user','deliveryCrew','status','total','date']
        extra_kwargs = {
            'user':{'read_only':True},
            'total':{'read_only':True},
            'date':{'read_only':True},
        }

class orderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'menu_item',
            'quantity',
            'unit_price',
            'price',
        ]
    
class orderItemsDetailsSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'deliveryCrew',
            'status',
            'total',
            'date',
            'items'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'total': {'read_only': True},
            'date' : {'read_only': True},
        }
    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = orderItemSerializer(order_items, many=True)
        return serializer.data

