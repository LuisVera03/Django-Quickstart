# Django Quick Start 🚀

## Introduction

**Django Quick Start** is a learning project designed to make Django’s core concepts easier to understand through clear examples and a well-organized codebase. It simplifies the official documentation into practical, real-world use cases, helping beginners and aspiring developers learn by building.

You’ll find working implementations of:
- Full CRUD operations with multiple approaches
- User authentication and authorization
- Django ORM queries (basic and advanced)
- Layered architecture (Repository → Service → View)
- REST-style JSON endpoints
- File handling and model relationships
- Custom middleware and signals
- Session management and dark mode
- Data exports (PDF/Excel)
- Many common patterns used in production apps

## 📋 Table of Contents

- [Technologies Used](#technologies-used)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Data Models](#data-models)
- [Project Applications](#project-applications)
  - [1. Rest (Main Application)](#1-rest-main-application)
  - [2. Layer and Generic](#2-layer-and-generic)
  - [3. JSON App](#3-json-app)
- [Implemented Methodologies](#implemented-methodologies)
- [Configuration and Environment Variables](#configuration-and-environment-variables)
- [Installation](#installation)
- [Usage](#usage)
- [Custom Commands](#custom-commands)
- [Permissions Structure](#permissions-structure)
- [Advanced Features](#advanced-features)
- [URL Structure](#url-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)
- [Changelog](#changelog)

---

## Technologies Used

- **Django 5.2.2** – Main web framework
- **Python 3.x** – Programming language
- **SQLite3** – Development database
- **Channels 4.3.1** – WebSockets/async support
- **Pillow 11.2.1** – Image processing
- **ReportLab 4.4.2** – PDF generation
- **OpenPyXL 3.1.5** – Excel file generation
- **django-auto-logout 0.5.1** – Automatic session management
- **python-decouple 3.8** – Environment variable management

---

## Key Features

✅ Multiple CRUD implementations
- Traditional CRUD with templates and HTML forms
- CRUD with Django Forms (automatic validation)
- JSON-based CRUD (REST-like endpoints)
- CRUD with Generic Class-Based Views (CBVs)

✅ Complete authentication system
- Sign up with robust password validation
- Login/Logout
- Groups and permissions
- User profile page

✅ Django ORM examples, end to end
- Basics: all, filter, get, exclude
- Advanced: select_related, prefetch_related
- Q objects and F expressions
- Aggregations: Count, Max, Min, Avg
- Pagination

✅ Clean, scalable architecture
- Clear separation (Repository → Service → View)
- Reusable patterns and DRY code
- Easy to test and extend

✅ Extra goodies
- Session-persistent Dark Mode
- Custom middleware for execution time logging
- Signals for user activity audit trail
- Custom error pages (400, 403, 404, 500)
- PDF and Excel exports
- Email sending example
- File/image uploads
- Custom template tags
- Flatpages for static content

---

## Project Architecture

Three apps with distinct educational focus:

```
django_quickstart/
├── django_quickstart/          # Project configuration
│   ├── settings.py            # Global settings
│   ├── urls.py                # Root URL routes
│   └── wsgi.py                # WSGI entrypoint
│
├── rest/                       # App 1: Traditional Django examples
│   ├── views.py               # Function-based views with CRUD & ORM demos
│   ├── models.py              # Table1, Table2, Table3, UserLog
│   ├── forms.py               # Django Forms for validation
│   ├── middleware.py          # Custom middleware
│   ├── signals.py             # User activity signals
│   ├── urls.py                # App routes
│   ├── templates/             # HTML templates
│   └── management/commands/   # Custom management commands
│       ├── setup_permissions.py
│       └── delete_logs.py
│
├── layer_and_generic/          # App 2: Layered architecture
│   ├── views.py               # Generic CBVs (List/Detail/Create/Update/Delete)
│   ├── services.py            # Business logic layer
│   ├── repositories.py        # Data access layer (ORM)
│   ├── forms.py               # Forms
│   └── templates/             # App templates
│
├── json_app/                   # App 3: JSON endpoints
│   ├── views.py               # JSON CRUD endpoints
│   ├── views_dark_mode.py     # Dark mode toggle/status
│   ├── context_processors.py  # Global dark_mode flag in templates
│   ├── urls.py                # App routes
│   └── templates/             # Templates with JS (AJAX)
│
├── static/                     # Global static files
│   ├── css/
│   ├── scripts/
│   └── img/
│
├── media/                      # Uploaded files
│   ├── images/
│   └── files/
│
├── templates/                  # Global templates
│   └── flatpages/             # Static flatpages
│
├── db.sqlite3                  # SQLite DB (dev)
├── manage.py                   # Django utility
└── requirements.txt            # Dependencies
```

---

## Data Models

This project uses three interrelated models to showcase all common Django field types and relationships:

### Table3
```python
class Table3(models.Model):
  duration_field = models.DurationField()       # Durations (timedelta)
  email_field = models.EmailField(unique=True)  # Validated emails
```

### Table2
```python
class Table2(models.Model):
    CHOICES = ((1, 'option1'), (2, 'option2'))
    positive_small_int = models.PositiveSmallIntegerField(choices=CHOICES)
```

### Table1 (Main Model)
```python
class Table1(models.Model):
  # Relationships
  foreign_key = models.ForeignKey(Table2, ...)      # Relation N:1
  one_to_one = models.OneToOneField(Table2, ...)    # Relation 1:1
  many_to_many = models.ManyToManyField(Table3, ...)# Relation N:N
    
  # Basic fields
    integer_field = models.IntegerField(...)
    float_field = models.FloatField(...)
    char_field = models.CharField(max_length=15)
    text_field = models.TextField(...)
    boolean_field = models.BooleanField(default=False)
    
  # Date/Time fields
    date_field = models.DateField(...)
    time_field = models.TimeField(...)
    datetime_field = models.DateTimeField(...)
    
  # File fields
    image_field = models.ImageField(upload_to='images/', ...)
    file_field = models.FileField(upload_to='files/', ...)
```

### UserLog
```python
class UserLog(models.Model):
    user = models.ForeignKey(User, ...)
    username = models.CharField(max_length=150)
    event_type = models.CharField(choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(...)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)
```

**Educational purpose:**
- Demonstrates ALL Django field types
- Shows the three relationship types
- Includes optional and required fields
- Handles files and images
- Enables practicing complex queries

---

## Project Applications

### 1. Rest (Main Application)

Purpose: Demonstrate traditional Django with function-based views (FBVs), Forms, and comprehensive ORM examples.

#### Features

##### User System
- Registration with password validation (length and composition)
- Login/Logout with feedback messages
- User profile: info, role, permissions
- User management: change roles (Admins only)
- Activity logs: login, logout, failed login, password change

##### Traditional CRUD
Two full CRUD approaches:

1) Manual CRUD (no Django Forms):
- `get_data`: Display all records
- `add_data`: Create records with backend validation
- `update_data`: Inline update flow with confirmation
- `delete_data_1`: Soft delete (mark as inactive)
- `delete_data_2`: Hard delete (permanent, cleans files)

2) CRUD with Django Forms:
- `get_data_form`: Validated list
- `form/<table>`: Dynamic create/edit form
- `add_data_form`: Choose table to create
- `update_data_form`: Choose table to edit

##### Django ORM Examples

Basics:
- `all_example`: Retrieve all
- `filter_example`: Filter with lookups (__gte, __contains, __icontains, ...)
- `get_example`: Retrieve specific records
- `exclude_example`: Exclude by condition
- `order_by_example`: Asc/Desc ordering
- `slice_example`: Slicing
- `exists_example`: Existence checks

Advanced:
- `select_related_example`: Optimize ForeignKey/OneToOne
- `prefetch_related_example`: Optimize ManyToMany
- `f_example`: F() expressions
- `Q_example`: Complex OR/AND logic
- `query_values_example`: Aggregations (Count/Max/Min/Avg) and annotations

##### Extras
- `export_pdf`: Export Table1 to PDF
- `export_excel`: Export Table1 to Excel
- Email contact form
- Custom template tags
- Template filters and HTML examples
- Custom error pages: 400/403/404/500

#### Implemented Middleware
- `ExecutionTimeMiddleware`: logs request execution time to console and adds `X-Execution-Time` header

#### Implemented Signals
- `user_logged_in`, `user_logged_out`, `user_login_failed`
- `pre_save(User)` to detect password changes

---

### 2. Layer and Generic
Purpose: Showcase a clean, layered architecture with Generic CBVs.

#### Layered Architecture

```
View Layer (views.py)
    ↓
Service Layer (services.py)
    ↓
Repository Layer (repositories.py)
    ↓
ORM / Database
```

##### Repository Layer (repositories.py)
Encapsulates data access operations:
- `BaseRepository`: generic CRUD helpers
- `Table1Repository`: optimized with `select_related`/`prefetch_related`; cleans files on delete
- `Table2Repository`, `Table3Repository`: specific repositories
- `UserRepository`: user creation and queries

Benefits:
- Centralized queries and optimizations
- Easier testing/mocking
- Transaction boundaries in one place

##### Service Layer (services.py)
Business logic orchestration:
- `BaseService`: generic list/get/create/update/delete
- `Table1Service`, `Table2Service`, `Table3Service`
- `UserService` + helpers: `try_login`, `register_user`, `perform_logout`
- `get_dashboard_data()` for Home metrics
- `get_field_data()` smart field serialization (choices, relations, files)

##### View Layer (views.py)
Reusable base mixins and CBVs:
- `BaseTableListView`, `BaseTableDetailView`, `BaseTableCreateView`, `BaseTableUpdateView`, `BaseTableDeleteView`
- Auth views: `LoginView`, `RegisterView`, `LogoutView`, `HomeView`
- Table-specific CBVs for Table1, Table2, Table3

Generic Templates:
- `Generic_templates/table.html`, `Generic_templates/detail.html`, `Generic_templates/form.html`

---

### 3. JSON App
Purpose: Provide REST-like JSON endpoints suitable for SPA usage.

#### Features

##### Table1 CRUD (`/json_app/table1/`)
- GET: Paginated list with relations (pagination enabled only if 5+ items)
- POST: Create (multipart form-data or JSON with base64 files)
- PUT: Update (requires `id`; replaces files, updates relations atomically)
- DELETE: Delete (cleans associated files)

Also exposes option lists for foreign keys and many-to-many relations.

##### Table2 & Table3 CRUD (`/json_app/table2/`, `/json_app/table3/`)
- Same pattern as Table1
- Table3 supports `DurationField` parsing (e.g., `"DD HH:MM:SS"`)

##### Search
- `search_json/`: Renders search page (AJAX driven)
- `search_all_json/`: Returns full unpaginated dataset (prefetched) for client-side filtering

##### Authentication (HTML templates)
- `register_json/`, `login_json/`, `logout_json/`, `profile_json/`
- Profile supports both HTML and JSON responses (based on `Accept` header or `?format=json`)

##### Global Dark Mode (root-level shortcuts)
- `toggle_dark_mode/`: Toggle session `dark_mode`
- `dark_mode_status/`: Read `dark_mode` flag
- `json_app.context_processors.dark_mode_context` injects the flag into all templates

---

## Implemented Methodologies

### 1) Repository Pattern
Encapsulated data access; easy to switch implementations without touching upper layers.

### 2) Service Layer Pattern
Centralized business logic; keeps views thin and focused on presentation.

### 3) DRY (Don’t Repeat Yourself)
Heavy reuse with mixins, base classes, and helpers.

### 4) Separation of Concerns
- Views: handle requests and responses
- Services: apply business rules
- Repositories: perform queries and persistence
- Forms: input validation
- Models: data structure

### 5) RESTful Design Principles
- Semantic endpoints
- Proper HTTP methods (GET/POST/PUT/DELETE)
- Clear status codes (200/201/204/400/404/500)
- Consistent JSON shapes

### 6) Security Best Practices
- Robust password validation
- `@login_required` and `@permission_required`
- CSRF protection (relaxed for JSON endpoints; secure tokens recommended)
- Safe file handling
- Automatic session timeouts (auto-logout)

### 7) Database Optimization
- `select_related()` (FK/OneToOne) and `prefetch_related()` (ManyToMany)
- Pagination strategies for large datasets
- Clean deletion of uploaded files

### 8) Error Handling
- Custom error pages (400/403/404/500)
- Guarded critical operations
- Helpful user feedback and server-side logs

---

## Configuration and Environment Variables

This project uses `python-decouple` for sensitive configuration. Create a `.env` file at the project root:

```env
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
CONTACT_EMAIL=recipient@example.com
```

Important:
- Never commit `.env` to version control
- For Gmail, use an App Password (not your regular password)
- In production, set `DEBUG=False` and configure `ALLOWED_HOSTS`

---

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtualenv (recommended)

### Steps

1) Clone the repository
```bash
git clone https://github.com/LuisVera03/Django-Quickstart.git
cd Django-Quickstart
```

2) Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3) Install dependencies
```bash
pip install -r requirements.txt
```

4) Create a `.env` file
Use the example above and adjust values to your environment.

5) Apply migrations
```bash
python manage.py migrate
```

6) Create default groups and permissions
```bash
python manage.py setup_permissions
```

7) Create a superuser (optional)
```bash
python manage.py createsuperuser
```

8) Configure Flatpages (optional)
- Go to `/admin/`
- Ensure a Site with ID=1 exists
- In Flatpages, create pages like `/pages/about/` and `/pages/policies/`

9) Run the development server
```bash
python manage.py runserver
```

10) Access the app
- Home: http://localhost:8000/
- Django Admin: http://localhost:8000/admin/
- Rest App: http://localhost:8000/rest_basic/
- Layer & Generic: http://localhost:8000/layer_and_generic/
- JSON App: http://localhost:8000/json_app/

---

## Usage

Typical workflow:

1) Register a user
- Use any app’s registration page
- New users are added to the `Customers` group

2) Explore ORM examples
- Login → menu → “Making Queries”
- Visit each example to see code and results

3) Practice CRUD
- Rest App: Traditional templates
- Layer & Generic: Layered CBV CRUD
- JSON App: JSON endpoints

4) Manage permissions (Admins)
- Create a superuser or promote a user to `Admins`
- Use the “User Management” page

5) Try features
- Upload images/files
- Export to PDF/Excel
- Send an email
- Toggle dark mode
- Review user logs

---

## Custom Commands

### setup_permissions
Creates the `Admins` and `Customers` groups and assigns permissions:
```bash
python manage.py setup_permissions
```

Created permissions (app-level):
- `view_data`: View all data
- `add_data`: Add data
- `change_data`: Change data
- `delete_data`: Delete data
- `manage_users`: Manage users

### delete_logs
Delete user logs older than 90 days:
```bash
python manage.py delete_logs
```

Tip: schedule as a cron job in production.

---

## Permissions Structure

### Customers (regular users)
- ✅ View data (`view_data`)
- ❌ Add/Change/Delete data
- ❌ Manage users

### Admins (administrators)
- ✅ View data (`view_data`)
- ✅ Add data (`add_data`)
- ✅ Change data (`change_data`)
- ✅ Delete data (`delete_data`)
- ✅ Manage users (`manage_users`)

Note: superusers bypass all restrictions.

---

## Advanced Features

### 1) Auto-Logout
Configured in `settings.py`:
```python
AUTO_LOGOUT = {
  'IDLE_TIME': timedelta(hours=1),
  'SESSION_TIME': timedelta(hours=12),
  'MESSAGE': 'Your session has expired due to inactivity. Please log in again.',
  'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}
```

### 2) Execution Time Middleware
Printed in the console and added as `X-Execution-Time` header:
```
Execution time: 0.0234 seconds - /rest_basic/get_data
```

### 3) Audit Signals
Automatically records:
- Logins, logouts, failed logins
- Password changes

See the “User Logs” page (Admins).

### 4) Persistent Dark Mode
Stored in session and injected into templates via context processor.

### 5) File Handling
- Old files are safely deleted on update/delete
- Public URLs accessible via helper `get_file_field_url`

Example:
```python
image_url = obj.get_file_field_url('image_field')
if obj.image_field:
  obj.image_field.delete(save=False)
```

### 6) Adaptive Pagination
Pagination only kicks in for datasets with 5+ records.

### 7) Flatpages
Create static pages from Django Admin under `/pages/...`.

---

## URL Structure

### Global (`django_quickstart/urls.py`)
```
/                         → Rest app index
/admin/                   → Django Admin
/rest_basic/              → Rest app landing (redirect to login)
/layer_and_generic/       → Layer & Generic app
/json_app/                → JSON App
/pages/                   → Flatpages
/toggle_dark_mode/        → Toggle dark mode (session)
/dark_mode_status/        → Read dark mode status

# Shortcuts
/layer_and_generic/login/ → Layer & Generic login
/json/login/              → JSON App login
```

### Rest App (`rest/urls.py`)
```
/                    → index
/rest_basic/         → redirect to login
/home_rest_basic     → home after login
/register_rest_basic/→ register
/login_rest_basic/   → login
/logout_rest_basic/  → logout
/profile_rest_basic/ → profile
/user_management     → user role management (Admins)
/user_logs           → recent activity logs (Admins)

# CRUD (manual)
/get_data            → list
/add_data            → create
/update_data         → update
/delete_data_1       → soft delete
/delete_data_2       → hard delete

# CRUD (forms)
/get_data_form       → list
/form/<table>        → create/edit form
/add_data_form       → choose table to add
/update_data_form    → choose table to update

# ORM examples
/making_queries
/all_example
/filter_example
/get_example
/exclude_example
/order_by_example
/slice_example
/exists_example
/select_related_example
/prefetch_related_example
/query_values_example
/f_example
/Q_example

# Misc
/html_example
/export_to_file
/export_pdf
/export_excel
/send_email
/template_tags
/test_400, /test_403, /test_404, /test_500
```

### Layer & Generic (`layer_and_generic/urls.py`)
```
/home_layer_and_generic             → home/dashboard
/register_layer_and_generic/        → register
/login_layer_and_generic/           → login
/logout_layer_and_generic/          → logout

# Table1 legacy aliases
/ListView/                          → list
/<int:pk>/                          → detail
/create/                            → create
/<int:pk>/update/                   → update
/<int:pk>/delete/                   → delete

# Table1 standard routes
/table1/                            → list
/table1/<int:pk>/                   → detail
/table1/create/                     → create
/table1/<int:pk>/update/            → update
/table1/<int:pk>/delete/            → delete

# Table2
/table2/                            → list
/table2/<int:pk>/                   → detail
/table2/create/                     → create
/table2/<int:pk>/update/            → update
/table2/<int:pk>/delete/            → delete

# Table3 (same pattern)
/table3/ ...
```

### JSON App (`json_app/urls.py`)
```
/home_json/     → home (HTML)
/register_json/ → register (HTML)
/login_json/    → login (HTML)
/logout_json/   → logout (HTML POST)
/profile_json/  → profile (HTML or JSON)

# JSON CRUD
/table1/        → Table1 CRUD (GET/POST/PUT/DELETE)
/table2/        → Table2 CRUD
/table3/        → Table3 CRUD

# Search
/search_json/   → search page (HTML)
/search_all_json/→ full dataset (JSON)
```

---

## Troubleshooting

### ImportError: No module named 'decouple'
Install dependencies:
```bash
pip install -r requirements.txt
```

### Database table not found
Apply migrations:
```bash
python manage.py migrate
```

### Image upload errors
Ensure Pillow is installed:
```bash
pip install Pillow
```

### Permissions not applied
Run setup command:
```bash
python manage.py setup_permissions
```

### Emails not sending
1) Check `.env` values
2) Use a Gmail App Password if using Gmail
3) Consider proper email backend credentials

---

## Contributing

This is an educational project. Contributions are welcome:

1) Open an issue describing a bug or enhancement
2) Fork the repository
3) Create a feature branch (`git checkout -b feature/YourFeature`)
4) Commit your changes (`git commit -m "Add YourFeature"`)
5) Push the branch (`git push origin feature/YourFeature`)
6) Open a Pull Request

---

## Additional Resources

- [Django documentation](https://docs.djangoproject.com/)

---

## License

Open source under the MIT License.

---

## Authors

**Luis Vera**
- GitHub: [@LuisVera03](https://github.com/LuisVera03)

**Agustin Palopoli**
- GitHub: [@AgustinPalopoli](https://github.com/AgustinPalopoli)

## Changelog

### v1.0.0 (2025)
- ✅ Three complete apps (Rest, Layer & Generic, JSON App)
- ✅ Comprehensive Django ORM examples
- ✅ Layered architecture (Repository → Service → View)
- ✅ JSON endpoints
- ✅ Auth and permissions
- ✅ Global dark mode
- ✅ Custom middleware and signals
- ✅ Management commands
- ✅ Data export (PDF/Excel)
- ✅ Email sending example
- ✅ File/image uploads
- ✅ Custom error pages
- ✅ Full documentation

---

If this repo helps you, please give it a ⭐ on GitHub.