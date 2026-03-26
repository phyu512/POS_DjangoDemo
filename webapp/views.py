from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout,get_user_model
from webapp.forms import UsernameResetPasswordForm,SignUpForm,EditUserProfileForm,GroupForm,GroupPermissionForm,MenuForm, CategoryForm,ProductForm,OutletForm,InventoryForm,CustomerForm,SaleOrderForm, SaleOrderDetailFormSet
from webapp.routes import Url
from webapp.helpers import DateUtils
from webapp.permissions import GrpPermissions
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from webapp.models import PortalUser,Employee,Menu,Category,Product,SaleOrderDetails,Outlet,Inventory,SaleOrder,Customer
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Q,ProtectedError
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from webapp.utils import group_required_for_menu
from django.contrib.sessions.models import Session
from django.http import JsonResponse

def is_superuser(user):
    return user.is_superuser
def is_inventory_manager(user):
    return user.groups.filter(name='Inventory Manager').exists()
def is_inventory_manager(user):
    return user.groups.filter(name='Inventory Manager').exists()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.instance.is_staff = True
            user = form.save(commit=False)  # Save the user

            # set flags BEFORE saving
            #user.is_staff = True
            #user.is_active = True

            # 1️⃣ Save user first (creates PK)
            user.save()

            form.save_m2m()

     
            return redirect('login')  # <-- make sure 'login' is the correct URL name
            #return redirect('home')  # NOT 'login'
        else:
            print(form.errors)  # <<< DEBUG
    else:
        form = SignUpForm()
    
    return render(request, Url.SignupPage, {
        'current_year': datetime.now().year,
        'form': form
        })

def signout(request):
    logout(request)
    list(get_messages(request))
    if request.GET.get("timeout"):
        messages.warning(request, "You have been logged out due to inactivity.")
    return redirect('login')  # Redirect to login page after logout

def login_view(request):
    # Clear all previous sessions
    Session.objects.all().delete()
    # Kill any previous user session
    if request.user.is_authenticated:
        storage = messages.get_messages(request)
        storage.used = True
        logout(request)  # Logs out the current user and clears their session

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get the authenticated user
            login(request, user)    # Log the user in
            messages.success(request, f"Welcome {user.username}!")

            # Redirect based on role of the logged-in user
            if user.is_superuser:
                return redirect('user_list')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, Url.LoginPage, {'form': form})

def reset_password_view(request):
    user_found = False
    user = None

    if request.method == "POST":
        form = UsernameResetPasswordForm(request.POST)

        if "find_user" in request.POST:
            if form.is_valid():
                username = form.cleaned_data["username"]
                try:
                    user = PortalUser.objects.get(username=username)
                    user_found = True
                except PortalUser.DoesNotExist:
                    form.add_error("username", "Username not found.")

        elif "reset_password" in request.POST:
            username = request.POST.get("username")
            try:
                user = PortalUser.objects.get(username=username)
                form = UsernameResetPasswordForm(request.POST)
                if form.is_valid():
                    user.password = make_password(form.cleaned_data["password1"])
                    user.save()
                    messages.success(request, "Password reset successful.")
                    return redirect("login")
            except PortalUser.DoesNotExist:
                form.add_error("username", "Username not found.")

    else:
        form = UsernameResetPasswordForm()

    return render(request, "webapp/passwordreset.html", {
        "form": form,
        "user_found": user_found
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_list_view(request):
    query = request.GET.get('q', '').strip()

    users = PortalUser.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    return render(request, Url.UserListPage, {'users': users})


# Edit user
@login_required
@user_passes_test(is_superuser)
def edituserprofile(request, user_id):
    user_obj = get_object_or_404(PortalUser, id=user_id)

    if request.method == "POST":
        form = EditUserProfileForm(request.POST, instance=user_obj)
        if form.is_valid():
            portal_user = form.save()

            # Get is_employee from the form, not model
            is_employee = form.cleaned_data.get('is_employee', False)

            if is_employee:
                full_name = f"{portal_user.first_name} {portal_user.last_name}"

                employee, created = Employee.objects.get_or_create(
                    user=portal_user,
                    defaults={
                        "employee_name": full_name
                    }
                )

                # Update name if already exists
                if not created:
                    employee.employee_name = full_name
                    employee.save()
            else:
                # If unchecked, remove employee link
                Employee.objects.filter(user=portal_user).delete()

            portal_user.save()
            return redirect('user_list')

    else:
        form = EditUserProfileForm(instance=user_obj)

    return render(request, Url.EditUserPage, {"form": form, "user_obj": user_obj})

# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def deactivate_user_profile(request, user_id):
#     user_obj = get_object_or_404(PortalUser, id=user_id)

#     # Prevent superuser from deactivating themselves
#     if user_obj == request.user:
#         messages.error(request, "You cannot deactivate your own account.")
#         return redirect("user_list")

#     if request.method == "POST":
#         user_obj.is_active = False
#         user_obj.save(update_fields=["is_active"])

#         messages.success(
#             request,
#             f"User '{user_obj.username}' has been deactivated."
#         )
#         return redirect("user_list")

#     return render(
#         request,
#         "users/confirm_deactivate_user.html",
#         {"user_obj": user_obj}
#     )

@login_required
@user_passes_test(lambda u: u.is_superuser)
def deactivateuserprofile(request, user_id):
    user_obj = get_object_or_404(PortalUser, id=user_id)

    # Prevent superuser from deactivating themselves
    if user_obj == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("user_list")

    user_obj.is_active = False
    user_obj.save(update_fields=["is_active"])

    messages.success(
        request,
        "The user will no longer be able to log in. Inactive successfully."
    )

    return redirect("user_list")

#######################################################################
############################    Role   ################################
#######################################################################
# Create role
@login_required
@user_passes_test(is_superuser)
# --- Create Role ---
def create_role(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('role_list')  # Back to user form
    else:
        form = GroupForm()
    return render(request, Url.AddEditRolePage, {
        'form': form,
        'title': 'Create Role',
        'button_text': 'Save'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def role_list_view(request):
    try:
        query = request.GET.get('q', '').strip()

        if query:
            roles = Group.objects.filter(name__icontains=query)
        else:
            roles = Group.objects.all()

    except Exception as e:
        messages.error(request, f"Error loading roles: {e}")
        roles = Group.objects.none()

    return render(request, Url.RoleListPage, {
        'roles': roles,
        'query': query
    })

# Edit role
@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_role(request, role_id):

    role = get_object_or_404(Group, id=role_id)

    try:
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=role)
            if form.is_valid():
                form.save()
                messages.success(request, f"Role '{role.name}' updated successfully.")
                return redirect('role_list')
        else:
            form = GroupForm(instance=role)

    except Exception as e:
        messages.error(request, f"Error updating role: {e}")

    return render(request, Url.AddEditRolePage, {
        'form': form,
        'title': 'Edit Role',
        'button_text': 'Update'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_role(request, role_id):

    if request.method != "POST":
        return redirect("role_list")

    role = get_object_or_404(Group, id=role_id)
    role_name = role.name

    try:
        # ✅ Check if any PortalUser is linked to this role
        if PortalUser.objects.filter(groups=role).exists():
            messages.error(
                request,
                f"Cannot delete role '{role_name}'. It is assigned to users."
            )
            return redirect("role_list")

        role.delete()

        messages.success(
            request,
            f"Role '{role_name}' deleted successfully."
        )

    except Exception as e:
        messages.error(request, f"Error deleting role: {str(e)}")

    return redirect("role_list")

#######################################################################
############################    Permission  ###########################
#######################################################################
# Create permission
def assign_group_permissions(request, group_id):

    # Get group from URL parameter
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            permissions = form.cleaned_data["permissions"]
            group.permissions.set(permissions)
            return redirect("role_list")
    else:
        form = GroupPermissionForm(initial={
            "group": group,
            "permissions": group.permissions.all()
        })

    return render(request, Url.AssignGroupPermissionPage, {
        "form": form,
        "title": "Assign Group Permission",
        "group": group
    })

#######################################################################
############################    Dashboard  ###########################
#######################################################################
@login_required
def dashboard_view(request):
    """
    Simple dashboard page for non-superusers.
    Superusers are redirected to user_list from login_view.
    """
    # Example: you can pass any data to the template
    context = {
        'username': request.user.username,
        'current_year': datetime.now().year,
    }
    return render(request, Url.DashboardPage, context)

#######################################################################
###############################    Menu  ##############################
#######################################################################
@login_required
@user_passes_test(is_superuser)
def menu_list(request):
    menuitems = Menu.objects.all()  # already ordered by `order`
    return render(request, Url.MenuListPage, {'menuitems': menuitems})

@login_required
@user_passes_test(is_superuser)
def createeditmenu(request, pk=None):
    if pk:
        menu = get_object_or_404(Menu, pk=pk)  # Edit existing menu
    else:
        menu = None  # Create new menu

    if request.method == "POST":
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuForm(instance=menu)

    title = 'Edit Menu' if pk else 'Create Menu'
    return render(request, Url.EditMenuPage, {'form': form, 'title': title})

@login_required
@user_passes_test(is_superuser)
def deactivatemenu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        try:
            menu.delete()
            messages.success(request, "Menu deleted successfully.")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this menu. It is linked to Category and Product and Users and Menu List and Outlet and Customer."
            )
        
        
    return redirect('menu_list')

#@login_required
#@user_passes_test(is_superuser)
#def deactivatemenu(request, pk):
#    menu = get_object_or_404(Menu, pk=pk)

#    # Prevent superuser from deactivating themselves
#    if request.method == 'POST':
#        menu.is_active = False
#        menu.save(update_fields=["is_active"])

#        messages.success(
#           request,
#            "The menu is inactive successfully."
#        )
#        return redirect('menu_list')

#######################################################################
###############################    Category  ##########################
#######################################################################
# Create category
@login_required
@user_passes_test(is_inventory_manager)
# --- Create category ---
def addeditcategory(request, pk=None):
    if pk:
        category = get_object_or_404(Category, pk=pk)
        title = "Edit Category"
        button_text = "Update"
    else:
        category = None
        title = "Create Category"
        button_text = "Save"

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, Url.AddEditCategoryPage, {
        'form': form,
        'title': title,
        'button_text': button_text
    })

@login_required
@user_passes_test(is_inventory_manager)
def category_list_view(request):

    query = request.GET.get('q', '').strip()

    categories = Category.objects.all()

    if query:
        categories = categories.filter(
            Q(category_name__icontains=query)
        )

    categories = categories.order_by('category_name')

    return render(request, Url.CategoryListPage, {
        "categories": categories,
        "query": query
    })

# Delete role
@login_required
@user_passes_test(is_inventory_manager)
def delete_category(request, pk):

    cat = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':

        # Check if products linked
        if Product.objects.filter(category=cat).exists():
            messages.error(
                request,
                f"Cannot delete '{cat.category_name}' because it has linked products."
            )
            return redirect('category_list')

        # Safe to delete
        cat.delete()
        messages.success(
            request,
            f"Category '{cat.category_name}' deleted successfully."
        )
        return redirect('category_list')

    return redirect(Url.CategoryListPage)

#######################################################################
###############################    Product  ##########################
#######################################################################
@login_required
@user_passes_test(is_inventory_manager)
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, Url.ProductListPage, {
        'products': products
    })

@login_required
@user_passes_test(is_inventory_manager)
# --- Create Product ---
def addeditproduct(request, pk=None):
    if pk:
        product = get_object_or_404(Product, pk=pk)
        title = "Edit Product"
        button_text = "Update"
    else:
        product = None
        title = "Create Product"
        button_text = "Save"

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, Url.AddEditProductPage, {
        'form': form,
        'title': title,
        'button_text': button_text
    })

def deleteproduct(request, pk):

    prod = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':

        # Check if linked to sale order details
        if SaleOrderDetails.objects.filter(product=prod).exists():
            messages.error(
                request,
                f"Cannot delete '{prod.product_name}' because it has linked sale order items."
            )
            return redirect('product_list')
        
        # Check if linked to inventory (FIXED HERE)
        if Inventory.objects.filter(product=prod).exists():
            messages.error(
                request,
                f"Cannot delete '{prod.product_name}' because it has linked inventory records."
            )
            return redirect('product_list')

        try:
            prod.delete()
            messages.success(
                request,
                f"Product '{prod.product_name}' deleted successfully."
            )
        except ProtectedError:
            messages.error(
                request,
                f"Cannot delete '{prod.product_name}'. It is linked to other records."
            )

    return redirect('product_list')


#######################################################################
###############################    Outlet  ##########################
#######################################################################
@login_required
@user_passes_test(is_inventory_manager)
def outlet_list(request):
    query = request.GET.get('q', '').strip()

    outlets = Outlet.objects.all().order_by('outlet_name')

    if query:
        outlets = outlets.filter(
            Q(outlet_name__icontains=query)
        )

    outlets = outlets.order_by('outlet_name')

    return render(request, Url.OutletListPage, {
        "outlets": outlets,
        "query": query
    })


# ✅ Add / Edit Outlet
@login_required
@user_passes_test(is_inventory_manager)
def addeditoutlet(request, pk=None):
    if pk:
        outlet = get_object_or_404(Outlet, pk=pk)
        title = "Edit Outlet"
        button_text = "Update"
    else:
        outlet = None
        title = "Create Outlet"
        button_text = "Save"

    if request.method == "POST":
        form = OutletForm(request.POST, instance=outlet)
        if form.is_valid():
            form.save()
            return redirect('outlet_list')
    else:
        form = OutletForm(instance=outlet)

    return render(request, Url.AddEditOutletPage, {
        'form': form,
        'title': title,
        'button_text': button_text
    })


# ✅ Delete Outlet
@login_required
@user_passes_test(is_inventory_manager)
def deleteoutlet(request, pk):

    outlet = get_object_or_404(Outlet, pk=pk)

    if request.method == 'POST':

        # Check if linked to inventory (FIXED HERE)
        if Inventory.objects.filter(outlet=outlet).exists():
            messages.error(
                request,
                f"Cannot delete '{outlet.outlet_name}' because it has linked inventory records."
            )
            return redirect('outlet_list')

        try:
            outlet.delete()
            messages.success(request, "Outlet deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete. Outlet is linked to inventory.")

        return redirect('outlet_list')

    return redirect('outlet_list')

#######################################################################
###############################    Inventory  ##########################
#######################################################################
@login_required
@user_passes_test(is_inventory_manager)
def inventory_list(request):
    query = request.GET.get('q', '').strip()

    inventories = Inventory.objects.select_related(
        'product', 'outlet'
    ).all()

    if query:
        inventories = inventories.filter(
            Q(product__product_name__icontains=query) |
            Q(outlet__outlet_name__icontains=query)
        )

    return render(
        request,
        Url.InventoryListPage,
        {
            'inventories': inventories,
            'query': query
        }
    )

@login_required
@user_passes_test(is_inventory_manager)
def addeditinventory(request, pk=None):
    if pk:
        inventory = get_object_or_404(Inventory, pk=pk)
        title = "Edit Inventory"
        button_text = "Update"
    else:
        inventory = None
        title = "Create Inventory"
        button_text = "Save"

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Inventory saved successfully.")
                return redirect('inventory_list')
            except Exception as e:
                messages.error(request, "Product already exists for this outlet.")

    else:
        form = InventoryForm(instance=inventory)

    return render(request, Url.AddEditInventoryPage, {
        'form': form,
        'inventory': inventory,
        'button_text': button_text,
        'title': title
    })


@login_required
@user_passes_test(is_inventory_manager)
def deleteinventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        inventory.delete()
        messages.success(request, "Inventory deleted successfully.")
        return redirect('inventory_list')

    return render(request, Url.InventoryListPage, {
        'inventory': inventory
    })


#######################################################################
###############################  customer  ##########################
#######################################################################
@login_required
@group_required_for_menu('Customer')
def customer_list(request):
    query = request.GET.get('q', '').strip()

    customers = Customer.objects.all().order_by('-created_at')

    if query:
        customers = customers.filter(customer_name__icontains=query)

    return render(request, Url.CustomerListPage, {
        'customers': customers,
        'query': query
    })

@login_required
@group_required_for_menu('Customer')
def addedit_customer(request, pk=None):
    if pk:
        customer = get_object_or_404(Customer, pk=pk)
        title = "Edit Customer"
        button_text = "Update"
    else:
        customer = None
        title = "Create Customer"
        button_text = "Save"

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, Url.AddEditCustomerPage, {
        'form': form,
        'title': title,
        'button_text': button_text
    })

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        try:
            customer.delete()
            messages.success(request, "Customer deleted successfully.")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this customer. It is linked to Sale Order or Sale Invoice."
            )

        return redirect("customer_list")

    return redirect("customer_list")

#######################################################################
###############################  sale order  ##########################
#######################################################################
@login_required
def sale_order_list(request):
    # Dynamically check if user has permission to view Sale Orders
    required_permission = GrpPermissions.can_view_sale_order  # Dynamically or based on view
    
    # Check if the user has the required permission through their groups
    if not request.user.groups.filter(permissions__codename=required_permission).exists():
        messages.error(request, "You do not have permission to view Sale Orders.")
        return redirect('/')  # redirect to home or dashboard

     # Fetch all sale orders with related customer and employee
    orders = SaleOrder.objects.select_related('customer', 'employee').all()

    # Prepare the list of orders with total amount calculated
    order_data = []
    for order in orders:
        total_amount = sum(item.subtotal for item in order.items.all())  # Assuming `saleorderdetail` has a `subtotal` field
        order_data.append({
            'order_id': order.order_id,
            'order_date': DateUtils.format_dd_mmm_yyyy(order.created_at),
            'customer_name': order.customer.customer_name,
            'customer_address': order.customer.address,
            'customer_phone': order.customer.phone,
            'total_amount': total_amount,
            'status': order.status,
        })
    
    return render(request, Url.SaleOrderListPage, {'order_data': order_data})

def get_product_price(request):
    product_id = request.GET.get('product_id')
    try:
        product = Product.objects.get(pk=product_id)
        return JsonResponse({'price': product.selling_price })
    except Product.DoesNotExist:
        return JsonResponse({'price': 0})

@login_required
def addeditsaleorder(request, pk=None):
    if pk:
        sale_order = get_object_or_404(SaleOrder, pk=pk)
    else:
        sale_order = None

    employee = getattr(request.user, "employee", None)

    if request.method == "POST":
        form = SaleOrderForm(request.POST, instance=sale_order)
        formset = SaleOrderDetailFormSet(request.POST, instance=sale_order)

        if form.is_valid() and formset.is_valid():

            # 🔴 Check if there is at least ONE valid detail line
            has_item = False
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get("DELETE", False):
                    has_item = True
                    break

            if not has_item:
                messages.error(request, "Sale order must contain at least one item.")
            else:
                sale_order = form.save(commit=False)
                sale_order.employee = employee
                sale_order.save()

                formset.instance = sale_order
                formset.save()

                messages.success(request, "Sale order saved successfully.")
                return redirect("saleorder_list")

    else:
        form = SaleOrderForm(instance=sale_order)
        formset = SaleOrderDetailFormSet(instance=sale_order)

    product_prices = {
        str(product.pk): float(product.selling_price)
        for product in Product.objects.all()
    }

    return render(request, "webapp/addeditsaleorder.html", {
        "form": form,
        "formset": formset,
        "title": "Create Sale Order" if not pk else "Edit Sale Order",
        "button_text": "Save" if not pk else "Update",
        "employee": employee,
        "product_prices": product_prices,  # ✅ important
    })