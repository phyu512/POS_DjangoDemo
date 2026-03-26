from django.urls import path
from . import views

urlpatterns = [
   #path('', views.LoginAccount, name="Home"),
   path('signup', views.signup, name="signup"),
   path('signout', views.signout, name="signout"),
   path('login', views.login_view, name='login'),  # <- name='login'
   path('passwordreset', views.reset_password_view, name='passwordreset'),  # <- name='login'
   path('userlist', views.user_list_view, name='user_list'),  # <- name='login'
   path('dashboard', views.dashboard_view, name='dashboard'),  # <- name='dashboard'
   path('users/edit/<int:user_id>', views.edituserprofile, name='edit_user_profile'),
   path('users/deactivate/<int:user_id>', views.deactivateuserprofile, name="deactivate_user"),
   path('role-list', views.role_list_view, name='role_list'),  # <- name='login'
   path('roles/create-new-role', views.create_role, name='create_role'),
   path('roles/edit/<int:role_id>', views.edit_role, name='edit_role'),
   path('roles/delete/<int:role_id>', views.delete_role, name='delete_role'),
   #path("groups/permissions", views.assign_group_permissions,name="assign_group_permissions"),
   path('groups/permissions/<int:group_id>', views.assign_group_permissions, name='assign_group_permissions'),
   path('menus', views.menu_list, name='menu_list'),
   path('menus/edit/<int:pk>', views.createeditmenu, name='edit_menu'),
   path('menus/delete/<int:pk>', views.deactivatemenu, name='menu_delete'),
   path('menus/add', views.createeditmenu, name='create_menu'),
   path('category', views.category_list_view, name='category_list'),
   path('category/edit/<int:pk>', views.addeditcategory, name='edit_category'),
   path('category/delete/<int:pk>', views.delete_category, name='delete_category'),
   path('category/add', views.addeditcategory, name='create_category'),
   path('product', views.product_list, name='product_list'),
   path('product/edit/<int:pk>', views.addeditproduct, name='edit_product'),
   path('product/delete/<int:pk>', views.deleteproduct, name='delete_product'),
   path('product/add', views.addeditproduct, name='create_product'),

   path('outlet', views.outlet_list, name='outlet_list'),
   path('outlet/edit/<str:pk>', views.addeditoutlet, name='edit_outlet'),
   path('outlet/delete/<str:pk>', views.deleteoutlet, name='delete_outlet'),
   path('outlet/add', views.addeditoutlet, name='create_outlet'),

   path('customers', views.customer_list, name='customer_list'),
   path('customers/edit/<str:pk>', views.addedit_customer, name='edit_customer'),
   path('customers/delete/<str:pk>', views.customer_delete, name='delete_customer'),
   path('customers/add', views.addedit_customer, name='create_customer'),

   path('inventory', views.inventory_list, name='inventory_list'),
   path('inventory/edit/<str:pk>', views.addeditinventory, name='edit_inventory'),
   path('inventory/delete/<str:pk>', views.deleteinventory, name='delete_inventory'),
   path('inventory/add', views.addeditinventory, name='create_inventory'),

   path('sale-orders', views.sale_order_list, name='saleorder_list'),
   path('sale-orders/edit/<str:pk>', views.addeditsaleorder, name='edit_saleorder'),
   path('sale-orders/delete/<str:pk>', views.deleteinventory, name='delete_saleorder'),
   path('sale-orders/add', views.addeditsaleorder, name='create_saleorder'),
   path('get-product-price', views.get_product_price, name='get_productprice'),
   #temporary
   path('inventory', views.menu_list, name='inventory_list'),
   path('sale-invoice', views.menu_list, name='saleinvoice_list'),
   path('paymentrcpt', views.menu_list, name='paymentrcpt_list'),
   

    
]