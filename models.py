from django.db import models

# Create your models here.

from django.contrib.auth.models import User

# These models should match your MySQL database tables
class Customer(models.Model):
    cust_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()

    class Meta:
        db_table = 'customers'

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.TextField()

    class Meta:
        db_table = 'admin'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image_path = models.CharField(max_length=255, blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'products'

class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cust_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'shopping_cart'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cust_id')
    order_date = models.DateTimeField()
    payment_status = models.CharField(max_length=20)
    order_status = models.CharField(max_length=20)
    shipping_address = models.TextField()

    class Meta:
        db_table = 'orders'

class OrderDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_details'

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cust_id')
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    rating = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'feedback'