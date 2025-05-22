"""
URL configuration for deepshoestoreproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from store import views


from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('logout/', views.logout_view, name='logout'),
    
    # Customer views
    path('customer/', views.customer_home, name='customer_home'),
    path('products/', views.view_products, name='view_products'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('history/', views.shopping_history, name='shopping_history'),
    path('rate_product/<int:order_id>/<int:product_id>/', views.rate_product, name='rate_product'),
    
    # Admin views
    path('admin-home/', views.admin_home, name='admin_home'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.add_product, name='admin_add_product'),  # Changed
    path('admin/products/remove/<int:product_id>/', views.remove_product, name='admin_remove_product'),  # Changed
    path('admin/products/update-stock/<int:product_id>/', views.update_stock, name='admin_update_stock'),  # Changed
    path('admin/products/update-price/<int:product_id>/', views.update_price, name='admin_update_price'),  # Changed
    path('admin/feedback/', views.view_feedback, name='admin_feedback'),

    path('admin/', admin.site.urls),
    #path('admin/', include('django.contrib.admin.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






    #path('admin-home/', views.admin_home, name='admin_home'),
    ##path('admin/products/', views.admin_products, name='admin_products'),
    #path('admin/products/add/', views.add_product, name='add_product'),
    #path('admin/products/remove/<int:product_id>/', views.remove_product, name='remove_product'),
    #path('admin/products/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    #path('admin/products/update-price/<int:product_id>/', views.update_price, name='update_price'),
    #path('admin/feedback/', views.view_feedback, name='view_feedback'),