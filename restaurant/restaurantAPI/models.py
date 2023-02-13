from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Category (models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=250,db_index=True, unique=True)
    def __str__(self) -> str:
        return self.title
    

class MenuItem(models.Model):
    title = models.CharField(max_length=250,db_index=True, unique=True)
    price = models.DecimalField(max_digits=6,decimal_places=2,db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    def __str__(self) -> str:
        return self.title
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    menuItem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    price = models.DecimalField(max_digits=6,decimal_places=2, null= True)
    unitPrice = models.DecimalField(max_digits=6,decimal_places=2, null= True)

    class Meta:
        unique_together = ['menuItem','user']

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    deliveryCrew = models.ForeignKey(User,on_delete=models.SET_NULL, related_name='deliveryCrew',null= True)
    status = models.BooleanField(db_index=True,default=0)
    total = models.DecimalField(max_digits=6,decimal_places=2,null=True)
    date = models.DateField(db_index=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)  
    menuItem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    price = models.DecimalField(max_digits=6,decimal_places=2, null= True)
    unitPrice = models.DecimalField(max_digits=6,decimal_places=2, null= True)

    class Meta:
        unique_together = ['menuItem','order']
