from django.shortcuts import render

# Create your views here.

import mysql.connector
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from decimal import Decimal

def create_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='manaal123',
            database='aleena_db',
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']
        
        connection = None
        cursor = None
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                
                if user_type == 'customer':
                    cursor.execute("SELECT cust_id FROM customers WHERE username=%s AND password=%s", (username, password))
                    user = cursor.fetchone()
                    if user:
                        request.session['user_id'] = user[0]
                        request.session['user_type'] = 'customer'
                        request.session.modified = True  # Critical addition
                        messages.success(request, 'Login successful!')
                        
                        # Ensure connection is closed before redirect
                        if cursor: cursor.close()
                        if connection: connection.close()
                        
                        return redirect('customer_home')
                
                elif user_type == 'admin':
                    cursor.execute("SELECT admin_id FROM admin WHERE username=%s AND password=%s", (username, password))
                    user = cursor.fetchone()
                    if user:
                        request.session['user_id'] = user[0]
                        request.session['user_type'] = 'admin'
                        request.session.modified = True  # Critical addition
                        messages.success(request, 'Admin login successful!')
                        
                        if cursor: cursor.close()
                        if connection: connection.close()
                        
                        return redirect('admin_home')
                
                messages.error(request, 'Invalid credentials')
        
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')
        
        finally:
            if cursor: cursor.close()
            if connection: connection.close()
    
    return render(request, 'store/login.html')

def register_customer(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        address = request.POST['address']
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO customers (name, phone_no, username, password, email, address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, phone, username, password, email, address))
                connection.commit()
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {e}')
            finally:
                cursor.close()
                connection.close()
    
    return render(request, 'store/register_customer.html')

def register_admin(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        address = request.POST['address']
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO admin (email, username, password, name, address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, username, password, name, address))
                connection.commit()
                messages.success(request, 'Admin registration successful! Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Admin registration failed: {e}')
            finally:
                cursor.close()
                connection.close()
    
    return render(request, 'store/register_admin.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Customer Views
#@login_required
def customer_home(request):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    return render(request, 'store/customer_home.html')

#@login_required
# def view_products(request):
#     connection = create_connection()
#     products = []
#     if connection:
#         cursor = connection.cursor()
#         cursor.execute("SELECT product_id, name, price, quantity FROM products")
#         products = cursor.fetchall()
#         cursor.close()
#         connection.close()
    
#     context = {'products': products}
#     return render(request, 'store/view_products.html', context)

def view_products(request):
    connection = create_connection()
    products = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT product_id, name, price, quantity, image_path FROM products")  # Added image_path
        products = cursor.fetchall()
        cursor.close()
        connection.close()
    
    context = {'products': products}
    return render(request, 'store/view_products.html', context)

#@login_required
def view_cart(request):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    cust_id = request.session.get('user_id')
    cart_items = []
    total = 0
    cart_count = 0  # Initialize cart_count
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Fetch cart items
        cursor.execute("""
            SELECT sc.product_id, p.name, sc.quantity, sc.total_price, p.price
            FROM shopping_cart sc
            JOIN products p ON sc.product_id = p.product_id
            WHERE sc.cust_id = %s
        """, (cust_id,))
        cart_items = cursor.fetchall()
        
        # Calculate total price and cart count
        total = sum(item[3] for item in cart_items)  # Sum of total_price for all items
        cart_count = sum(item[2] for item in cart_items)  # Sum of quantities for all items
        
        cursor.close()
        connection.close()
    
    # Pass cart_count along with other context data
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count,
    }
    return render(request, 'store/view_cart.html', context)

# #@login_required
# def add_to_cart(request, product_id):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     if request.method == 'POST':
#         quantity = int(request.POST['quantity'])
#         cust_id = request.session.get('user_id')
        
#         connection = create_connection()
#         if connection:
#             cursor = connection.cursor()
            
#             # Check product availability
#             cursor.execute("SELECT price, quantity FROM products WHERE product_id=%s", (product_id,))
#             product = cursor.fetchone()
            
#             if product and product[1] >= quantity:
#                 price = product[0]
#                 total_price = price * quantity
                
#                 # Check if product already in cart
#                 cursor.execute("""
#                     SELECT cart_id, quantity FROM shopping_cart 
#                     WHERE cust_id=%s AND product_id=%s
#                 """, (cust_id, product_id))
#                 existing_item = cursor.fetchone()
                
#                 if existing_item:
#                     # Update existing item
#                     new_quantity = existing_item[1] + quantity
#                     new_total = price * new_quantity
#                     cursor.execute("""
#                         UPDATE shopping_cart 
#                         SET quantity=%s, total_price=%s 
#                         WHERE cart_id=%s
#                     """, (new_quantity, new_total, existing_item[0]))
#                 else:
#                     # Add new item
#                     cursor.execute("""
#                         INSERT INTO shopping_cart (cust_id, product_id, quantity, total_price)
#                         VALUES (%s, %s, %s, %s)
#                     """, (cust_id, product_id, quantity, total_price))
                
#                 connection.commit()
#                 messages.success(request, 'Product added to cart!')
#             else:
#                 messages.error(request, 'Not enough stock available.')
            
#             cursor.close()
#             connection.close()
    
#     return redirect('view_products')
# @login_required
def add_to_cart(request, product_id):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        cust_id = request.session.get('user_id')
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            
            try:
                # Check product availability
                cursor.execute("SELECT price, quantity FROM products WHERE product_id=%s", (product_id,))
                product = cursor.fetchone()
                
                if product:
                    price, stock_quantity = product
                    if stock_quantity >= quantity:
                        total_price = price * quantity
                        
                        # Check if product is already in the cart
                        cursor.execute("""
                            SELECT cart_id, quantity FROM shopping_cart 
                            WHERE cust_id=%s AND product_id=%s
                        """, (cust_id, product_id))
                        existing_item = cursor.fetchone()
                        
                        if existing_item:
                            # Update the existing cart item
                            cart_id, existing_quantity = existing_item
                            new_quantity = existing_quantity + quantity
                            new_total = price * new_quantity
                            cursor.execute("""
                                UPDATE shopping_cart 
                                SET quantity=%s, total_price=%s 
                                WHERE cart_id=%s
                            """, (new_quantity, new_total, cart_id))
                        else:
                            # Add new item to the cart
                            cursor.execute("""
                                INSERT INTO shopping_cart (cust_id, product_id, quantity, total_price)
                                VALUES (%s, %s, %s, %s)
                            """, (cust_id, product_id, quantity, total_price))
                        
                        # Commit the transaction
                        connection.commit()
                        messages.success(request, 'Product added to cart!')
                    else:
                        messages.error(request, 'Not enough stock available.')
                else:
                    messages.error(request, 'Product not found.')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
            finally:
                cursor.close()
                connection.close()
    
    return redirect('view_products')


#@login_required
def remove_from_cart(request, product_id):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cust_id = request.session.get('user_id')
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            
            # Get current cart item
            cursor.execute("""
                SELECT cart_id, quantity FROM shopping_cart 
                WHERE cust_id=%s AND product_id=%s
            """, (cust_id, product_id))
            item = cursor.fetchone()
            
            if item:
                if quantity >= item[1]:
                    # Remove entire item
                    cursor.execute("DELETE FROM shopping_cart WHERE cart_id=%s", (item[0],))
                else:
                    # Update quantity
                    new_quantity = item[1] - quantity
                    cursor.execute("""
                        SELECT price FROM products WHERE product_id=%s
                    """, (product_id,))
                    price = cursor.fetchone()[0]
                    new_total = price * new_quantity
                    
                    cursor.execute("""
                        UPDATE shopping_cart 
                        SET quantity=%s, total_price=%s 
                        WHERE cart_id=%s
                    """, (new_quantity, new_total, item[0]))
                
                connection.commit()
                messages.success(request, 'Cart updated successfully!')
            
            cursor.close()
            connection.close()
    
    return redirect('view_cart')

#changed
from django.db import transaction
from decimal import Decimal
from datetime import datetime

def checkout(request):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    cust_id = request.session.get('user_id')
    cart_items = []
    subtotal = Decimal('0.00')

    # Fetch cart items first
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT sc.product_id, p.name, sc.quantity, p.price, sc.total_price
                FROM shopping_cart sc
                JOIN products p ON sc.product_id = p.product_id
                WHERE sc.cust_id = %s
            """, (cust_id,))
            cart_items = cursor.fetchall()
            
            if cart_items:
                subtotal = sum(Decimal(str(item[4])) for item in cart_items)
        except Exception as e:
            messages.error(request, f'Error fetching cart items: {e}')
        finally:
            cursor.close()
            connection.close()

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        payment_method = request.POST.get('payment_method')
        
        if not address:
            messages.error(request, 'Please provide a shipping address')
            return redirect('checkout')
            
        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('view_cart')

        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                
                # Start transaction
                cursor.execute("START TRANSACTION")
                
                try:
                    # 1. Create order
                    cursor.execute("""
                        INSERT INTO orders (cust_id, order_date, payment_status, order_status, shipping_address)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        cust_id,
                        datetime.now().date(),
                        "Paid",
                        "Processing",
                        address
                    ))
                    order_id = cursor.lastrowid
                    
                    # 2. Create order details for each item
                    for item in cart_items:
                        product_id, name, quantity, price, total_price = item
                        
                        cursor.execute("""
                            INSERT INTO order_details (order_id, product_id, quantity, price)
                            VALUES (%s, %s, %s, %s)
                        """, (order_id, product_id, quantity, price))
                        
                        # 3. Update product inventory
                        cursor.execute("""
                            UPDATE products 
                            SET quantity = quantity - %s 
                            WHERE product_id = %s
                        """, (quantity, product_id))
                    
                    # 4. Clear shopping cart
                    cursor.execute("DELETE FROM shopping_cart WHERE cust_id = %s", (cust_id,))
                    
                    # Commit only if all operations succeed
                    connection.commit()
                    
                    messages.success(request, 'Order placed successfully!')
                    return redirect('shopping_history')
                    
                except Exception as e:
                    connection.rollback()
                    messages.error(request, f'Order processing failed: {str(e)}')
                finally:
                    cursor.close()
                    connection.close()
                    
        except Exception as e:
            messages.error(request, f'Checkout error: {str(e)}')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': Decimal('0.00'),
        'total': subtotal + Decimal('0.00'),
    }
    return render(request, 'store/checkout.html', context)
# #@login_required
# def checkout(request):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     cust_id = request.session.get('user_id')
    
#     if request.method == 'POST':
#         address = request.POST['address']
#         payment_status = "Paid"
#         order_status = "Processing"
#         order_date = datetime.now()
        
#         connection = create_connection()
#         if connection:
#             cursor = connection.cursor()
            
#             try:
#                 # Create order
#                 cursor.execute("""
#                     INSERT INTO orders (cust_id, order_date, payment_status, order_status, shipping_address)
#                     VALUES (%s, %s, %s, %s, %s)
#                 """, (cust_id, order_date, payment_status, order_status, address))
#                 order_id = cursor.lastrowid
                
#                 # Get cart items
#                 cursor.execute("""
#                     SELECT product_id, quantity, total_price 
#                     FROM shopping_cart 
#                     WHERE cust_id=%s
#                 """, (cust_id,))
#                 cart_items = cursor.fetchall()
                
#                 # Process each item
#                 for product_id, quantity, total_price in cart_items:
#                     # Add to order details
#                     cursor.execute("""
#                         INSERT INTO order_details (order_id, product_id, quantity, price)
#                         VALUES (%s, %s, %s, %s)
#                     """, (order_id, product_id, quantity, total_price/quantity))
                    
#                     # Update product stock
#                     cursor.execute("""
#                         UPDATE products 
#                         SET quantity = quantity - %s 
#                         WHERE product_id = %s
#                     """, (quantity, product_id))
                
#                 # Clear cart
#                 cursor.execute("DELETE FROM shopping_cart WHERE cust_id=%s", (cust_id,))
                
#                 connection.commit()
#                 messages.success(request, 'Order placed successfully!')
#                 return redirect('shopping_history')
            
#             except Exception as e:
#                 connection.rollback()
#                 messages.error(request, f'Checkout failed: {e}')
            
#             finally:
#                 cursor.close()
#                 connection.close()
    
#     return render(request, 'store/checkout.html')

#@login_required
# def shopping_history(request):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     cust_id = request.session.get('user_id')
#     orders = []
    
#     connection = create_connection()
#     if connection:
#         cursor = connection.cursor()
        
#         # Get orders
#         cursor.execute("""
#             SELECT o.order_id, o.order_date, o.order_status
#             FROM orders o
#             WHERE o.cust_id = %s
#             ORDER BY o.order_date DESC
#         """, (cust_id,))
#         orders = cursor.fetchall()
        
#         # Get order details for each order
#         order_details = {}
#         for order in orders:
#             cursor.execute("""
#                 SELECT p.name, od.quantity, od.price
#                 FROM order_details od
#                 JOIN products p ON od.product_id = p.product_id
#                 WHERE od.order_id = %s
#             """, (order[0],))
#             details = cursor.fetchall()
#             order_details[order[0]] = {
#                 'items': details,
#                 'total': sum(quantity * price for _, quantity, price in details)
#             }
        
#         cursor.close()
#         connection.close()
    
#     context = {
#         'orders': orders,
#         'order_details': order_details
#     }
#     return render(request, 'store/shopping_history.html', context)


# def shopping_history(request):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     cust_id = request.session.get('user_id')
#     orders = []
    
#     connection = create_connection()
#     if connection:
#         cursor = connection.cursor()
        
#         # Get orders
#         cursor.execute("""
#             SELECT o.order_id, o.order_date, o.order_status
#             FROM orders o
#             WHERE o.cust_id = %s
#             ORDER BY o.order_date DESC
#         """, (cust_id,))
#         orders = cursor.fetchall()
        
#         # Get order details for each order
#         order_details = {}
#         for order in orders:
#             cursor.execute("""
#                 SELECT p.product_id, p.name, od.quantity, od.price  # Added p.product_id
#                 FROM order_details od
#                 JOIN products p ON od.product_id = p.product_id
#                 WHERE od.order_id = %s
#             """, (order[0],))
#             details = cursor.fetchall()
#             order_details[order[0]] = {
#                 'items': details,
#                 'total': sum(quantity * price for _, _, quantity, price in details)  # Updated index
#             }
        
#         cursor.close()
#         connection.close()
    
#     context = {
#         'orders': orders,
#         'order_details': order_details
#     }
#     return render(request, 'store/shopping_history.html', context)

#changed
from django.db import connection
from collections import defaultdict

def shopping_history(request):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    cust_id = request.session.get('user_id')
    orders = []
    order_details_dict = {}
    feedback_exists = defaultdict(dict)

    try:
        with connection.cursor() as cursor:
            # Fetch order headers
            cursor.execute("""
                SELECT o.order_id, o.order_date, o.order_status
                FROM orders o
                WHERE o.cust_id = %s
                ORDER BY o.order_date DESC
            """, [cust_id])
            orders = cursor.fetchall()

            if orders:
                # Fetch all order details
                cursor.execute("""
                    SELECT od.order_id, od.product_id, p.name, od.quantity, od.price
                    FROM order_details od
                    JOIN products p ON od.product_id = p.product_id
                    WHERE od.order_id IN (
                        SELECT order_id FROM orders WHERE cust_id = %s
                    )
                """, [cust_id])
                
                # Build dictionary of order details
                for row in cursor.fetchall():
                    if row[0] not in order_details_dict:
                        order_details_dict[row[0]] = []
                    order_details_dict[row[0]].append(row)
                
                # Check which products have been rated
                cursor.execute("""
                    SELECT order_id, product_id 
                    FROM feedback 
                    WHERE order_id IN %s AND cust_id = %s
                """, [tuple(o[0] for o in orders), cust_id])
                
                for row in cursor.fetchall():
                    feedback_exists[row[0]][row[1]] = True

    except Exception as e:
        messages.error(request, f'Error fetching order history: {e}')

    context = {
        'orders': orders or [],
        'order_details': order_details_dict,
        'feedback_exists': feedback_exists,
    }
    return render(request, 'store/shopping_history.html', context)

#@login_required
# def rate_product(request, order_id, product_id):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     cust_id = request.session.get('user_id')
    
#     if request.method == 'POST':
#         rating = int(request.POST['rating'])
        
#         if 1 <= rating <= 5:
#             connection = create_connection()
#             if connection:
#                 cursor = connection.cursor()
                
#                 # Verify the product was in the order
#                 cursor.execute("""
#                     SELECT 1 FROM order_details 
#                     WHERE order_id = %s AND product_id = %s
#                 """, (order_id, product_id))
                
#                 if cursor.fetchone():
#                     timestamp = datetime.now()
#                     cursor.execute("""
#                         INSERT INTO feedback (cust_id, order_id, rating, timestamp)
#                         VALUES (%s, %s, %s, %s)
#                     """, (cust_id, order_id, rating, timestamp))
#                     connection.commit()
#                     messages.success(request, 'Thank you for your feedback!')
#                 else:
#                     messages.error(request, 'Invalid product for this order')
                
#                 cursor.close()
#                 connection.close()
#         else:
#             messages.error(request, 'Rating must be between 1 and 5')
    
#     return redirect('shopping_history')


def rate_product(request, order_id, product_id):
    if request.session.get('user_type') != 'customer':
        return redirect('home')
    
    cust_id = request.session.get('user_id')
    
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            
            if not 1 <= rating <= 5:
                messages.error(request, 'Rating must be between 1 and 5')
                return redirect('shopping_history')
            
            connection = create_connection()
            if not connection:
                messages.error(request, 'Database connection failed')
                return redirect('shopping_history')
                
            try:
                cursor = connection.cursor()
                
                # 1. Verify the product was in the order
                cursor.execute("""
                    SELECT 1 FROM order_details 
                    WHERE order_id = %s AND product_id = %s
                """, (order_id, product_id))
                
                if not cursor.fetchone():
                    messages.error(request, 'Invalid product for this order')
                    return redirect('shopping_history')
                
                # 2. Check if already rated
                cursor.execute("""
                    SELECT 1 FROM feedback 
                    WHERE order_id = %s AND product_id = %s
                """, (order_id, product_id))
                
                if cursor.fetchone():
                    messages.error(request, 'You have already rated this product from this order')
                    return redirect('shopping_history')
                
                # 3. Insert new rating
                cursor.execute("""
                    INSERT INTO feedback (cust_id, order_id, product_id, rating, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (cust_id, order_id, product_id, rating, datetime.now()))
                
                connection.commit()
                messages.success(request, 'Thank you for your feedback!')
                
            except Exception as e:
                connection.rollback()
                if "Duplicate entry" in str(e):
                    messages.error(request, 'You have already rated this product')
                else:
                    messages.error(request, f'Failed to submit rating: {str(e)}')
            finally:
                cursor.close()
                connection.close()
                
        except ValueError:
            messages.error(request, 'Invalid rating value')
            
        return redirect('shopping_history')
    
    # GET request - show rating form
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if already rated
            cursor.execute("""
                SELECT 1 FROM feedback 
                WHERE order_id = %s AND product_id = %s
            """, (order_id, product_id))
            
            if cursor.fetchone():
                messages.error(request, 'You have already rated this product')
                return redirect('shopping_history')
            
            # Get product info
            cursor.execute("""
                SELECT p.name FROM products p
                WHERE p.product_id = %s
            """, (product_id,))
            product = cursor.fetchone()
            
            if product:
                return render(request, 'store/rate_product.html', {
                    'order_id': order_id,
                    'product_id': product_id,
                    'product_name': product['name'],
                    'already_rated': False
                })
                
        except Exception as e:
            messages.error(request, f'Error fetching product: {str(e)}')
        finally:
            cursor.close()
            connection.close()
    
    messages.error(request, 'Product not found')
    return redirect('shopping_history')
#old1 works but can rate multiple times
# def rate_product(request, order_id, product_id):
#     if request.session.get('user_type') != 'customer':
#         return redirect('home')
    
#     cust_id = request.session.get('user_id')
    
#     if request.method == 'POST':
#         rating = int(request.POST['rating'])
        
#         if 1 <= rating <= 5:
#             connection = create_connection()
#             if connection:
#                 cursor = connection.cursor()
                
#                 # Verify the product was in the order
#                 cursor.execute("""
#                     SELECT 1 FROM order_details 
#                     WHERE order_id = %s AND product_id = %s
#                 """, (order_id, product_id))
                
#                 if cursor.fetchone():
#                     timestamp = datetime.now()
#                     cursor.execute("""
#                         INSERT INTO feedback (cust_id, order_id, product_id, rating, timestamp)
#                         VALUES (%s, %s, %s, %s, %s)
#                     """, (cust_id, order_id, product_id, rating, timestamp))
#                     connection.commit()
#                     messages.success(request, 'Thank you for your feedback!')
#                 else:
#                     messages.error(request, 'Invalid product for this order')
                
#                 cursor.close()
#                 connection.close()
#         else:
#             messages.error(request, 'Rating must be between 1 and 5')
        
#         return redirect('shopping_history')
    
#     # GET request - show rating form
#     connection = create_connection()
#     if connection:
#         cursor = connection.cursor()
#         cursor.execute("""
#             SELECT p.name FROM products p
#             WHERE p.product_id = %s
#         """, (product_id,))
#         product = cursor.fetchone()
#         cursor.close()
#         connection.close()
        
#         if product:
#             return render(request, 'store/rate_product.html', {
#                 'order_id': order_id,
#                 'product_id': product_id,
#                 'product_name': product[0]
#             })
    
#     messages.error(request, 'Product not found')
#     return redirect('shopping_history')

# Admin Views
#@login_required
# def admin_home(request):
#     if request.session.get('user_type') != 'admin':
#         return redirect('home')
#     return render(request, 'store/admin_home.html')


def admin_home(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    connection = create_connection()
    if not connection:
        messages.error(request, 'Database connection failed')
        return render(request, 'store/admin_home.html')
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) as count FROM products")
        product_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        order_count = cursor.fetchone()['count']
        
        # Average rating
        cursor.execute("SELECT AVG(rating) as avg FROM feedback")
        avg_rating = cursor.fetchone()['avg'] or 0
        
        # Total revenue
        # Total revenue (FIXED)
        cursor.execute("""
        SELECT SUM(od.quantity * od.price) as total
        FROM order_details od
        JOIN orders o ON od.order_id = o.order_id
        WHERE o.payment_status = 'Paid'
        """)
        revenue = cursor.fetchone()['total'] or 0


        
        # Product category distribution (if you have categories)
        # cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category")
        # category_dist = cursor.fetchall()
        
        # For now, we'll create a placeholder since you don't have categories
        category_dist = [{'category': 'All Products', 'count': product_count}]
        
    except Exception as e:
        messages.error(request, f'Error fetching statistics: {str(e)}')
        product_count = 0
        order_count = 0
    
        
    finally:
        if connection:
            connection.close()
    
    context = {
        'product_count': product_count,
        'order_count': order_count,

    }
    return render(request, 'store/admin_home.html', context)

#@login_required
def admin_products(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    connection = create_connection()
    products = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT product_id, name, price, quantity FROM products")
        products = cursor.fetchall()
        cursor.close()
        connection.close()
    
    context = {'products': products}
    return render(request, 'store/admin_products.html', context)

#@login_required
# def add_product(request):
#     if request.session.get('user_type') != 'admin':
#         return redirect('home')
    
#     if request.method == 'POST':
#         name = request.POST['name']
#         price = float(request.POST['price'])
#         quantity = int(request.POST['quantity'])
#         production_date = request.POST['production_date']
        
#         connection = create_connection()
#         if connection:
#             cursor = connection.cursor()
#             try:
#                 cursor.execute("""
#                     INSERT INTO products (name, price, quantity, production_date)
#                     VALUES (%s, %s, %s, %s)
#                 """, (name, price, quantity, production_date))
#                 connection.commit()
#                 messages.success(request, 'Product added successfully!')
#                 return redirect('admin_products')
#             except Exception as e:
#                 messages.error(request, f'Failed to add product: {e}')
#             finally:
#                 cursor.close()
#                 connection.close()
    
#     return render(request, 'store/add_product.html')



import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# def add_product(request):
#     if request.session.get('user_type') != 'admin':
#         return redirect('home')
    
#     if request.method == 'POST':
#         name = request.POST['name']
#         price = float(request.POST['price'])
#         quantity = int(request.POST['quantity'])
#         production_date = request.POST['production_date']
        
#         # Handle file upload
#         image_path = None
#         if 'image' in request.FILES:
#             image = request.FILES['image']
#             fs = FileSystemStorage()
#             filename = fs.save(f'products/{image.name}', image)
#             image_path = fs.url(filename)
        
#         connection = create_connection()
#         if connection:
#             cursor = connection.cursor()
#             try:
#                 cursor.execute("""
#                     INSERT INTO products (name, price, quantity, production_date, image_path)
#                     VALUES (%s, %s, %s, %s, %s)
#                 """, (name, price, quantity, production_date, image_path))
#                 connection.commit()
#                 messages.success(request, 'Product added successfully!')
#                 return redirect('admin_products')
#             except Exception as e:
#                 messages.error(request, f'Failed to add product: {e}')
#             finally:
#                 cursor.close()
#                 connection.close()
    
#     return render(request, 'store/add_product.html')


def add_product(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST['name']
        price = float(request.POST['price'])
        quantity = int(request.POST['quantity'])
        production_date = request.POST['production_date']
        
        # Handle file upload - THIS IS THE CRITICAL PART
        # image_path = None
        # if 'image' in request.FILES:
        #     image = request.FILES['image']
        #     fs = FileSystemStorage()
        #     # Save to 'products/' subdirectory without /media prefix
        #     filename = fs.save(f'products/{image.name}', image)
        #     # Store relative path in database
        #     image_path = filename  # This will be 'products/filename.jpg'
        
        image_path = None
        if 'image' in request.FILES:
           image = request.FILES['image']
           fs = FileSystemStorage()
        # Generate a clean filename (removes special characters)
           clean_name = image.name.replace(' ', '_').replace('.0', '')  # Removes .0 from filename
           filename = fs.save(f'products/{clean_name}', image)
        # Store ONLY the relative path without /media prefix
           image_path = filename 
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO products (name, price, quantity, production_date, image_path)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, price, quantity, production_date, image_path))
                connection.commit()
                messages.success(request, 'Product added successfully!')
                return redirect('admin_products')
            except Exception as e:
                messages.error(request, f'Failed to add product: {e}')
            finally:
                cursor.close()
                connection.close()
    
    return render(request, 'store/add_product.html')

#@login_required
def remove_product(request, product_id):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
            connection.commit()
            messages.success(request, 'Product removed successfully!')
        except Exception as e:
            messages.error(request, f'Failed to remove product: {e}')
        finally:
            cursor.close()
            connection.close()
    
    return redirect('admin_products')

#@login_required
def update_stock(request, product_id):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        new_stock = int(request.POST['quantity'])
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    UPDATE products SET quantity=%s WHERE product_id=%s
                """, (new_stock, product_id))
                connection.commit()
                messages.success(request, 'Stock updated successfully!')
                return redirect('admin_products')
            except Exception as e:
                messages.error(request, f'Failed to update stock: {e}')
            finally:
                cursor.close()
                connection.close()
    
    return render(request, 'store/update_stock.html', {'product_id': product_id})

#@login_required
def update_price(request, product_id):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        new_price = float(request.POST['price'])
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    UPDATE products SET price=%s WHERE product_id=%s
                """, (new_price, product_id))
                connection.commit()
                messages.success(request, 'Price updated successfully!')
                return redirect('admin_products')
            except Exception as e:
                messages.error(request, f'Failed to update price: {e}')
            finally:
                cursor.close()
                connection.close()
    
    return render(request, 'store/update_price.html', {'product_id': product_id})

#@login_required
def view_feedback(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    connection = create_connection()
    feedbacks = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT f.feedback_id, c.name, f.order_id, f.rating, f.timestamp
            FROM feedback f
            JOIN customers c ON f.cust_id = c.cust_id
            ORDER BY f.timestamp DESC
        """)
        feedbacks = cursor.fetchall()
        cursor.close()
        connection.close()
    
    context = {'feedbacks': feedbacks}
    return render(request, 'store/view_feedback.html', context)

# Public Views
def home(request):
    return render(request, 'store/home.html')