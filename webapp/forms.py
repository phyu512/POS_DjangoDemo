from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from webapp.models import PortalUser,Menu,Category,Product,Outlet,Inventory,SaleOrder, SaleOrderDetails,Customer
from django.contrib.auth.models import Group,Permission
from django.db.models import Sum
from django.forms import inlineformset_factory
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError
#######################################################################
############################      Edit User      ######################
####################################################################### 
class EditUserProfileForm(UserChangeForm):
    password = None  # remove the default password field
    first_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, empty_label="Select Role", widget=forms.Select(attrs={'class': 'form-select'}))
    is_employee = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    
    class Meta:
       model = PortalUser
       fields = ['first_name','last_name','username', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['role'].initial = self.instance.groups.first()
            self.fields["is_employee"].initial = hasattr(
                self.instance, "employee"
            )

    # Optional: ensure email is unique
    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = PortalUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already used by another user.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get('role')

        if commit:
            user.save()

            # 🔑 THIS is where your tables get updated
            user.groups.clear()
            user.user_permissions.clear()

            if selected_role:
                user.groups.add(selected_role)
                user.user_permissions.set(
                    selected_role.permissions.all()
                )

        return user
    
#######################################################################
############################      Sign Up        ######################
#######################################################################     
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(required=True,label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'})) 
    password2 = forms.CharField(required=True,label="Password Confirmation", widget=forms.PasswordInput(attrs={'class': 'form-control'}))  
    class Meta:
        model = PortalUser
        fields = ['first_name','last_name','username','password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'  # Add class to input

#######################################################################
############################  Forget Password    ######################
#######################################################################  
class UsernameResetPasswordForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username"
        })
    )

    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "New password",
            "disabled": False
        })
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
            "disabled": False
        })
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") or cleaned.get("password2"):
            if cleaned.get("password1") != cleaned.get("password2"):
                raise forms.ValidationError("Passwords do not match.")
        return cleaned

#######################################################################
###############################    Role Form ##########################
#######################################################################  
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter role name'}),
        }

#######################################################################
##########################   Permission Form ##########################
#######################################################################  
class GroupPermissionForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Group",
        widget=forms.Select(attrs={
            "class": "form-select",   # Bootstrap dropdown
            "id": "id_group"
        })
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "form-check-input"
        }),
        required=False,
        label="Permissions"
    )

#######################################################################
##########################      Menu Form    ##########################
#######################################################################  
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'url_name', 'icon', 'parent', 'groups', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

#######################################################################
##########################    Category Form   #########################
#######################################################################  
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }

#######################################################################
##########################    Product Form   #########################
####################################################################### 

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

#######################################################################
##########################    Outlet Form   #########################
####################################################################### 
class OutletForm(forms.ModelForm):
    class Meta:
        model = Outlet
        fields = ['outlet_name', 'location', 'short_location']
        widgets = {
            'outlet_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'short_location': forms.TextInput(attrs={'class': 'form-control'}),
        }

#######################################################################
##########################    Inventory Form   #########################
####################################################################### 
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'outlet', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'outlet': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if not product or quantity is None:
            return cleaned_data

        # Get current inventory instance (for edit case)
        instance = self.instance

        # Sum all inventory quantities for this product
        total_quantity = (
            Inventory.objects
            .filter(product=product)
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

        # If editing, subtract old quantity first
        if instance.pk:
            total_quantity -= instance.quantity

        # Add new quantity
        new_total = total_quantity + quantity

        # Compare with product stock_quantity
        if new_total != product.stock_quantity:
            raise forms.ValidationError(
                f"Total inventory ({new_total}) must equal Product stock quantity ({product.stock_quantity})."
            )

        return cleaned_data

#######################################################################
##########################    SaleOrder Form   #########################
####################################################################### 
class SaleOrderForm(forms.ModelForm):
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="---------",
        required=True,  # Django validation still applies
        error_messages={'required': 'This field is required. Please select a customer.'},
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': False  # <- prevents browser popup
        })
    )

    class Meta:
        model = SaleOrder
        fields = ['customer']
        
        


class SaleOrderDetailsForm(forms.ModelForm):

    class Meta:
        model = SaleOrderDetails
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select product-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1'
            }),
            'price': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Force validation even if empty
        self.empty_permitted = False

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        delete = cleaned_data.get('DELETE')

        # Ignore deleted rows
        if delete:
            return cleaned_data

        # If product not selected → attach error to product field
        if not product:
            self.add_error('product', 'Please select a product.')

        # Optional: validate quantity too
        if product and (not quantity or quantity <= 0):
            self.add_error('quantity', 'Quantity must be greater than 0.')

        return cleaned_data

class BaseSaleOrderDetailFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_item = False

        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue

            if form.cleaned_data.get('product'):
                has_item = True

        if not has_item:
            raise ValidationError("Sale order must contain at least one item.")
        
SaleOrderDetailFormSet = inlineformset_factory(
    SaleOrder,
    SaleOrderDetails,
    form=SaleOrderDetailsForm,
    formset=BaseSaleOrderDetailFormSet,
    extra=1,
    can_delete=True
)


#######################################################################
##########################    customer Form   #################
#######################################################################
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'email', 'phone', 'address']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }