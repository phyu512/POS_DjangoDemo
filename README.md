##StarLink Trading - Full-Stack POS System

A dynamic Point of Sale (POS) and trading system prototype built with Python Django. This project demonstrates a robust back-office architecture focusing on secure, role-based access and dynamic UI rendering.

##Security & Identity
* **Dynamic Role-Based Menu:** The navigation sidebar is generated dynamically. Access permissions are refreshed immediately once an administrator updates a user's role.
* **Role-Based Access Control (RBAC):**
    * **IT Administrator:**  Full system control including Dashboard, Users, Roles, Menu Mapping, and Outlet (Branch) configuration.
    * **Sale Representative:** Access to the sales cycle—Customers, Sale Orders, Sale Invoices, and Payment Receipts.
    * **Inventory Manager:** Access to product lifecycle—Categories, Product management, and Stock Lists.
	* **Zero-Trust Onboarding:** New self-registered users are restricted to the Dashboard only until an Administrator assigns a functional role.
* **Security & Session Management:**
	* **Auto-Logout:** Sessions expire after 3 minutes of inactivity to protect unattended terminals in a retail environment.
    * **URL Protection:** Unauthorized users attempting to access restricted links will find the links expired or inaccessible.
    * **User Lifecycle:** Supports new user sign-up, admin-led role assignment, and password reset functionality.

##Getting Started & Testing
| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **IT Administrator** | admin | Password@123 | User, Role, Menu, Outlet |
| **Sale Representative** | spuser | Password@123 | Dashboard, Customers, Sales Order, Sale Invoice, Payment Receipt |
| **Inventory Manager** | whmanager | Password@123 | Dashboard, Category, Product, Inventory List |

##Tech Stack
* **Framework:** Django 5.2.10
* **Language:**  Python
* **Database:** sqlite 3
* **Utilities:** django-extensions, sqlparse
