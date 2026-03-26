import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.conf import settings  # to reference your custom user model
from decimal import Decimal


def generate_16_char_id():
    return str(uuid.uuid4().int)[:16]  # first 16 digits of UUID

def generate_random_suffix(length=12):
    """Generate a random string of letters and digits."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# # ----------------------------------------------------------------------------------------------------
# # PortalGroup TABLE --> Store portal-specific group (like auth_group)
# # ----------------------------------------------------------------------------------------------------
# class PortalGroup(models.Model):
#     name = models.CharField(max_length=100)
#     outlet = models.ForeignKey('Outlet', on_delete=models.CASCADE, null=True, blank=True)

# # ----------------------------------------------------------------------------------------------------
# # PortalPermission TABLE --> Store portal-specific permissions (like auth_permission)
# # ----------------------------------------------------------------------------------------------------
# class PortalPermission(models.Model):
#     codename = models.CharField(max_length=100, unique=True)
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name

# -------------------------
# PortalUser TABLE
# -------------------------

class PortalUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class PortalUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            "unique": "This username already exists."
        }
    )
    email = None  # remove email field

    # Link to Django's built-in Group
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='portal_users'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = PortalUserManager()

    def __str__(self):
        return self.get_username() if not self.get_full_name().strip() else self.get_full_name()
    
# # -----------------------------------------------------------------------------------------------------------------------------
# # PortalUserGroup TABLE --> Link a user to a portal-specific permission (like webapp_portaluser_groups)
# # -----------------------------------------------------------------------------------------------------------------------------
# class PortalUserGroup(models.Model):
#     # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     # group = models.ForeignKey(PortalGroup, on_delete=models.CASCADE)
#     user = models.ForeignKey(PortalUser, on_delete=models.CASCADE)
#     group = models.ForeignKey(PortalGroup, on_delete=models.CASCADE)
#     # -----------------------------------------------------------------------------------------------------------------------------
# # PortalUserPermission TABLE --> Link a user to a portal-specific permission (like webapp_portaluser_user_permissions)
# # -----------------------------------------------------------------------------------------------------------------------------
# class PortalUserPermission(models.Model):
#     # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     # permission = models.ForeignKey(PortalPermission, on_delete=models.CASCADE)
#     user = models.ForeignKey(PortalUser, on_delete=models.CASCADE)
#     permission = models.ForeignKey(PortalPermission, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('user', 'permission')  # optional, prevent duplicates

#     def __str__(self):
#         return f"{self.user.username} → {self.permission.codename}"
# -------------------------
# Category TABLE
# -------------------------
class Category(models.Model):
    category_id = models.CharField(primary_key=True, max_length=16, default=generate_16_char_id, editable=False)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
    
    class Meta: 
        db_table = 'category'

# -------------------------
# PRODUCT TABLE
# -------------------------
class Product(models.Model):
    product_id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False
    )
    product_name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            today = timezone.now().strftime('%Y%m%d')  # YYYYMMDD
            last_product = Product.objects.filter(
                product_id__startswith=today
            ).order_by('-product_id').first()

            if last_product:
                last_number = int(last_product.product_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.product_id = f"{today}{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"
    
    class Meta: 
        db_table = 'product'
        permissions = [
            ("change_product_sellingprice", "Can change product selling price")
        ]

# -------------------------
# CUSTOMER  TABLE
# -------------------------
class Customer(models.Model):
    customer_id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False
    )
    customer_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            today = timezone.now().strftime('%Y%m%d')  # YYYYMMDD
            last_cust = Customer.objects.filter(
                customer_id__startswith=today
            ).order_by('-customer_id').first()

            if last_cust:
                last_number = int(last_cust.customer_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.customer_id = f"{today}{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_name} ({self.customer_id})"
    
    class Meta: 
        db_table = 'customer'
# -------------------------
# Outlet TABLE
# -------------------------
class Outlet(models.Model):
    outlet_id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False
    )
    outlet_name = models.CharField(max_length=150)
    location = models.CharField(max_length=255, blank=True, null=True)
    short_location = models.CharField(max_length=3)  # first 3 chars of ID

    def save(self, *args, **kwargs):
        # Generate outlet_id only if not set
        if not self.outlet_id:
            # Ensure short_location is exactly 3 chars
            prefix = (self.short_location.upper() + "XXX")[:3]  # pad if needed
            # Generate 13-char random suffix
            suffix = generate_random_suffix(12)
            self.outlet_id = f"{prefix}-{suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.outlet_name} ({self.outlet_id})"
    
    class Meta: 
        db_table = 'outlet'
# -------------------------
# Inventory TABLE
# -------------------------
class Inventory(models.Model):
    inventory_id = models.CharField(primary_key=True, max_length=16, default=generate_16_char_id, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    outlet = models.ForeignKey(Outlet, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'outlet')  # one record per product per outlet

    def __str__(self):
        return f"{self.product.name} @ {self.outlet.name}: {self.quantity}"
    class Meta: 
        db_table = 'inventory'
        permissions = [
            ("approve_saleorder", "Can approve sale order"),
            ("cancel_saleorder", "Can cancel sale order"),
        ]
# -------------------------
# EMPLOYEE TABLE
# -------------------------
class Employee(models.Model):
    user = models.OneToOneField(
        PortalUser,
        on_delete=models.CASCADE,
        null=True,
        related_name="employee"
    )
    employee_id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False
    )
    employee_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            today = timezone.now().strftime('%Y%m%d')
            last_employee = Employee.objects.filter(
                employee_id__startswith=today
            ).order_by('-employee_id').first()

            if last_employee:
                last_number = int(last_employee.employee_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.employee_id = f"{today}{new_number:04d}"

        super().save(*args, **kwargs)

    # ✅ MUST BE OUTSIDE save()
    def __str__(self):
        if self.user:
            return f"{self.employee_name} ({self.user.username})"
        return self.employee_name

    class Meta:
        db_table = 'employee'
    
# -------------------------
# SALE ORDER TABLE
# -------------------------
class SaleOrder(models.Model):
    order_id = models.CharField(max_length=16, primary_key=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approval_requested', 'Approval Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancel_requested', 'Cancel Requested'),
        ('cancel_approved', 'Cancel Approved'),
        ('cancel_rejected', 'Cancel Rejected')
    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='draft')

    def save(self, *args, **kwargs):
        if not self.order_id:
            today = timezone.now().strftime('%Y%m%d')
            last_order = SaleOrder.objects.filter(order_id__startswith=today).order_by('-order_id').first()
            new_number = int(last_order.order_id[-4:]) + 1 if last_order else 1
            self.order_id = f"{today}{new_number:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale Order {self.order_id}"
    
    class Meta: 
        db_table = 'saleorder'
        permissions = [
            ("approve_saleorder", "Can approve the sale order"),
            ("reject_saleorder", "Can reject the sale order"),
            ("approve_request_saleorder", "Can request to approve the sale order"),
            ("cancel_request_saleorder", "Can request to cancel the sale order"),
            ("approve_cancelrequest_saleorder", "Can approve the cancel request sale order"),
            ("reject_cancelrequest_saleorder", "Can reject the cancel request sale order")
        ]

# -------------------------
# SALE ORDER DETAILS TABLE
# -------------------------
class SaleOrderDetails(models.Model):
    order_item_id = models.CharField(max_length=16, primary_key=True, editable=False)
    order = models.ForeignKey(SaleOrder, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return (self.quantity or 0) * (self.price or Decimal('0.00'))


    def save(self, *args, **kwargs):
        if not self.order_item_id:
            today = timezone.now().strftime('%Y%m%d')

            last_item = SaleOrderDetails.objects.filter(
                order_item_id__startswith=today
            ).order_by('-order_item_id').first()

            new_number = int(last_item.order_item_id[-4:]) + 1 if last_item else 1
            self.order_item_id = f"{today}{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    class Meta:
        db_table = 'saleorderdetails'
        

# -------------------------
# PAYMENT TABLE
# -------------------------
class PaymentReceipt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.PROTECT, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=30)
    received_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('draft', 'Draft'),  # Created but not yet submitted
        ('approval_requested', 'Approval Requested'),  # Requested approval
        ('approved', 'Approved'),  # Approved by approver
        ('rejected', 'Rejected'),  # Rejected by approver
        ('cancel_requested', 'Cancel Requested'),  # Cancellation requested
        ('cancel_approved', 'Cancel Approved'),  # Cancel request approved
        ('cancel_rejected', 'Cancel Rejected')  # Cancel request rejected
    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='draft')

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_payments"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'paymentreceipt'
        permissions = [
            ("approve_paymentreceipt", "Can approve payment receipt"),
            ("reject_paymentreceipt",  "Can reject payment receipt"),
            ("approve_request_paymentreceipt", "Can request to approve the payment receipt"),
            ("cancel_request_paymentreceipt", "Can request to cancel the payment receipt"),
            ("approve_cancelrequest_paymentreceipt", "Can approve the cancel request payment receipt"),
            ("reject_cancelrequest_paymentreceipt", "Can reject the cancel request payment receipt")
        ]

# --------------------------------------------------
# Menu TABLE
# --------------------------------------------------
class Menu(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(
        max_length=100,
        blank=True,      # allows empty in forms
        null=True,       # allows NULL in database
        help_text="Django URL name (e.g. user_list, dashboard)"
    )
    icon = models.CharField(max_length=50, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.PROTECT
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text="Which roles can see this menu"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
    

# --------------------------------------------------
# Sale Invoice TABLE
# --------------------------------------------------
class SaleInvoice(models.Model):
    invoice_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False,
        unique=True
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    STATUS_CHOICES = [
        ('draft', 'Draft'),  # Created but not yet submitted
        ('approval_requested', 'Approval Requested'),  # Requested approval
        ('approved', 'Approved'),  # Approved by approver
        ('rejected', 'Rejected'),  # Rejected by approver
        ('cancel_requested', 'Cancel Requested'),  # Cancellation requested
        ('cancel_approved', 'Cancel Approved'),  # Cancel request approved
        ('cancel_rejected', 'Cancel Rejected')  # Cancel request rejected
    ]

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.customer}"

    class Meta:
        ordering = ['-date']
        permissions = [
            ("approve_saleinvoice", "Can approve sale invoice"),
            ("reject_saleinvoice",  "Can reject sale invoice"),
            ("approve_request_saleinvoice", "Can request to approve the sale invoice"),
            ("cancel_request_saleinvoice", "Can request to cancel the sale invoice"),
            ("approve_cancelrequest_saleinvoice", "Can approve the cancel request sale invoice"),
            ("reject_cancelrequest_saleinvoice", "Can reject the cancel request sale invoice")
        ]


# --------------------------------------------------
# Sale Invoice Details TABLE
# --------------------------------------------------
class SaleInvoiceLine(models.Model):
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.PROTECT, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # Auto-calculate line total
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} x {self.quantity}"